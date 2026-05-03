## 📌 Sobre el Proyecto

Este proyecto es un script de análisis y procesamiento de datos orientado a series temporales de los diferentes sensores. Su objetivo principal es transformar datos crudos en información visual útil y estructurada.

### ⚙️ Características Principales (Features)
* **Procesamiento de Datos:** Lectura de registros JSON anidados en archivos CSV y estructuración cronológica mediante `pandas`.
* **Segmentación Automática:** Identificación dinámica de diferentes ciclos de "Cultivo" basándose en ventanas de inactividad de los sensores (saltos mayores a 10 días).
* **Limpieza y Normalización (Data Cleansing):** Detección de valores anómalos (outliers) fuera de rangos biológicos coherentes y corrección automática mediante imputación selectiva.
* **Agrupación Temporal:** Resampleo de datos a promedios de 1 hora para suavizar el ruido de los sensores y facilitar el análisis de tendencias.
* **Visualización de Datos:** Generación automática de dos sets de gráficas (dispersión y relacionales) para observar el comportamiento global y las comparativas lado a lado por cada ciclo de cultivo usando `seaborn`.