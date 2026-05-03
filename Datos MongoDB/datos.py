import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Carga de datos y ordenamiento cronológico
data = []
with open('datos.csv', 'r') as f:
    for line in f:
        if line.strip():
            try: data.append(json.loads(line))
            except: continue

df = pd.DataFrame(data)
df['start_ts'] = pd.to_datetime(df['start_ts'])
df = df.sort_values('start_ts')

# 2. Detección Automática de Cultivos
# Cualquier salto temporal mayor a 10 días se considera un nuevo cultivo
df['cultivo'] = (df['start_ts'].diff() > pd.Timedelta(days=10)).cumsum() + 1
df['cultivo'] = 'Cultivo ' + df['cultivo'].astype(str)
df['month'] = df['start_ts'].dt.strftime('%Y-%m')

# 3. Rangos de Normalización
ranges = {
    'temp_air': (5.0, 45.0), 
    'hum_air': (20.0, 95.0),
    'temp_water': (10.0, 28.0),
    'ph': (5.5, 7.0),
    'ec': (0.8, 2.5),
    'distance_cm': (25.0, 120.0) # Límites del tanque
}

# Función de valores aleatorios coherentes
def get_random_sensible(col, temp_water):
    tw = temp_water if pd.notna(temp_water) else 20.0
    if col == 'ph': return np.clip(6.2 - 0.02 * (tw - 20) + np.random.uniform(-0.2, 0.2), 5.5, 7.0)
    elif col == 'ec': return np.clip(1.6 + 0.015 * (tw - 20) + np.random.uniform(-0.2, 0.2), 0.8, 2.5)
    elif col == 'temp_air': return np.random.uniform(20.0, 35.0)
    elif col == 'hum_air': return np.random.uniform(65.0, 85.0)
    elif col == 'temp_water': return np.random.uniform(18.0, 22.0)
    elif col == 'distance_cm': return np.random.uniform(40.0, 100.0)
    return np.nan

# Limpieza e imputación selectiva solo en valores anómalos
for col, (low, high) in ranges.items():
    if col in df.columns:
        outliers = (df[col] < low) | (df[col] > high)
        df.loc[outliers, col] = df[outliers].apply(
            lambda row: get_random_sensible(col, row.get('temp_water', np.nan)), axis=1
        )

# Guardar CSV corregido
df.to_csv('datosNormalizados.csv', index=False)

# 4. Preparación de dataframes promediados a 1 hora
# 4a. Resample General (Serie de tiempo completa)
df_resampled_1h = df.set_index('start_ts').resample('1h').mean(numeric_only=True)
df_resampled_1h = df_resampled_1h.dropna(how='all')
df_resampled_1h['month'] = df_resampled_1h.index.strftime('%Y-%m')

# 4b. Resample agrupado por Cultivo
df_indexed = df.set_index('start_ts')
df_resampled_cultivo = df_indexed.groupby('cultivo').resample('1h').mean(numeric_only=True).reset_index()
df_resampled_cultivo = df_resampled_cultivo.dropna(subset=list(ranges.keys()), how='all')
df_resampled_cultivo['month'] = df_resampled_cultivo['start_ts'].dt.strftime('%Y-%m')

# 5. Generar AMBOS sets de gráficas
for var in [v for v in ranges.keys() if v in df.columns]:
    
    # ==========================================
    # SET 1: GRÁFICAS GLOBALES (Serie Completa)
    # ==========================================
    plt.figure(figsize=(12, 6))
    if var == 'ec':
        df_plot_global = df.dropna(subset=[var])
        sns.scatterplot(data=df_plot_global, x='start_ts', y=var, hue='month', palette='magma', s=50, alpha=0.9)
        plt.title('Dispersión General de EC')
        plt.xlabel('Fecha de Medición')
    else:
        if var in df_resampled_1h.columns:
            df_plot_global = df_resampled_1h.dropna(subset=[var])
            sns.scatterplot(data=df_plot_global, x=df_plot_global.index, y=var, hue='month', palette='viridis', s=45, alpha=0.8)
            titulo = f'Promedio General de {var.upper()}'
            if var == 'distance_cm': titulo = 'Promedio General del Nivel del Tanque'
            plt.title(titulo)
            plt.xlabel('Fecha de Medición')
        else: continue
            
    plt.ylabel(f'Valor de {var.upper()}')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'global_1h_{var}.png')
    plt.close()

    # ==========================================
    # SET 2: GRÁFICAS POR CULTIVO (Lado a Lado)
    # ==========================================
    if var == 'ec':
        df_plot_cultivo = df.dropna(subset=[var])
        titulo_cultivo = f'Dispersión de EC por Cultivo'
    else:
        df_plot_cultivo = df_resampled_cultivo.dropna(subset=[var])
        titulo_cultivo = f'Promedio de {var.upper()} por Cultivo'
        if var == 'distance_cm': titulo_cultivo = 'Promedio del Nivel del Tanque por Cultivo'
            
    g = sns.relplot(
        data=df_plot_cultivo,
        x='start_ts',
        y=var,
        col='cultivo',
        hue='month',
        palette='tab10',
        kind='scatter',
        facet_kws={'sharex': False, 'sharey': True}, 
        height=5, 
        aspect=1.2,
        s=40,
        alpha=0.8
    )
    
    # Ajustes estéticos para la gráfica compuesta
    g.figure.subplots_adjust(top=0.85)
    g.figure.suptitle(titulo_cultivo, fontsize=20, fontweight='bold')
    g.set_titles("{col_name}", size=15)
    g.set_axis_labels("Fecha", f"Valor de {var.upper()}")
    
    # Rotar las fechas en el eje X para mejorar la lectura
    for ax in g.axes.flat:
        ax.tick_params(axis='x', labelsize=13)
        ax.tick_params(axis='y', labelsize=13)

        for label in ax.get_xticklabels():
            label.set_rotation(45)
            
    g.savefig(f'por_cultivo_1h_{var}.png')
    plt.close()

print("Proceso finalizado. Datos normalizados y gráficas guardadas.")