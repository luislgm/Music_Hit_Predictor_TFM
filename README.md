# Music Hit Predictor

Este proyecto consiste en estudiar los éxitos musicales en Estados Unidos según la lista de éxitos publicada semanalmente por Billboard (hot-100s).

En el proyecto se realizará la extracción de todos los hits musicales desde su origen, 1958, y se añadirán una serie de características proporcionadas por la API de [Billboard](https://github.com/guoguo12/billboard-charts) y la API de spotify ([spotipy](https://spotipy.readthedocs.io/en/2.13.0/)).

Tras la extracción, se realizará un análisis de los hits a lo largo del tiempo, y se obtendrán conclusiones interesantes.

Otro propósito del proyecto será buscar un modelo de predicción, dados los features obtenidos, predecir el porcentaje de que una canción sea éxito o no. Para ello también se descargarán canciones que no han sido hit aleatoriamente, para así conformar un dataset de entrenamiento y test.

Por último, se extraerán las letras de las canciones de los hits según su género musical, para este caso se extraerán las letras de los hits que pertenecen al género pop y al género urban contemporary (R&B, Hip-Hop, Rap, Trap...) y se realizara un pequeño estudio de las letras para estos géneros.

## Requisitos

Para poder ejecutar todos los notebooks del proyecto, se recomienda usar el entorno conda que se proporciona en el fichero environment_tfm.yml

Para la creación del entorno ejecutar:
~~~
conda env create -f environment_tfm.yml
~~~
Para la activación del entorno:
~~~
conda activate tfm
~~~

Para ejecutar los cuadernos Jupyter, se han lanzado con Jupyter-lab, que es la herramienta que se incluye en el entorno.
~~~
Jupyter-lab
~~~

Para la extracción de los datos, es necesario estar identificado y tener los token pertinentes para el uso de la API de Spotify y la API de Genius.
  - Para crear un "client id" para usar la API de spotify, seguir los pasos que se indican en el [enlace](https://developer.spotify.com/documentation/general/guides/app-settings/).
  - Para crear un "client_id" para usar la API de Genius. Es necesario seguir los pasos que se indican en el [enlace](https://docs.genius.com/#/getting-started-h1).

## Estructura del proyecto

En el proyecto se pueden observar las siguientes carpetas:
  - Data
  - Data_Generation
  - Hit_Data_Analysis
  - Models
  - Predictive_Modelling

<b>Data</b> será donde se almacenen todos los datos generados en formato csv, esta carpeta estará vacía en git. Los datos podrán ser generados siguiendo los notebooks de la carpeta Data_Generation. Por comodidad y, ya que la generación de datos es un proceso que requiere bastante tiempo, se facilitan los ficheros en el siguiente [enlace](https://drive.google.com/drive/folders/1NyCAPqVdK4ZcOPovaSirImuEoe7fceAl?usp=sharing) de Google Drive.

<b>Data_Generation</b>, contiene todos los notebooks y paquetes necesarios para la realización de la extracción de los datos.

<b>Hit_Data_Analysis</b>, contiene los notebooks en los que se realiza el análisis de los datos de las canciones que han sido hit.

<b>Models</b>, contiene todos los modelos entrenados en formato .pkl

<b>Predictive_Modelling</b>, es donde se incluyen los notebooks para buscar el mejor modelo de predicción.

## Orden de lectura del proyecto

A continuación se explicará la secuencia de lectura de los notebooks para ver todo el proceso llevado a cabo.

Lo primero es la generación de datos. Todo lo necesario para ello se encuentra dentro del directorio <b>Data_Generation</b>.
Se ha desarrollado un Objeto, que incluye diferentes funciones para extraer los datos, esta se encuentre en music_data.py.

El orden de lectura es el siguiente:

1_data_hits_extraction.ipynb en este notebook se muestran ejemplos de la extracción de *hits*.

2_data_hits_fusion.ipynb en este notebook se realiza la fusión de todos los *hits* generados en el cuaderno anterior.

A continuación se realizó un análisis de los *hits*, esto se encuentra dentro del directorio <b>Hit_Data_Analysis</b>.

1_hit_analysis.ipynb en este cuaderno se realiza un estudio de los *hits* obtenidos.

A continuación, y ya que vamos a usar modelos de predicción muy sensible a *outliers*, será según lo observado en el cuaderno 1_hit_analysis.ipynb, hacer una limpieza de estos *outliers* para así aunque hayan sido *hit* conseguir un modelo más generalizable. Esta parte se encuentra dentro del directorio <b>Predictive_Modelling</b> y corresponde con el cuaderno 3_clean_dataset.ipynb.

Lo siguiente que hicimos es generar un dataset que poder entrenar, para ello se han extraído datos de canciones aleatorias de los cuales nos quedaríamos con aquellas que no son *hit* y lo fusionaríamos con el dataset del cuaderno 3_clean_dataset.ipynb. Esto es hace en el cuaderno 3_data_random_extract.ipynb y 4_data_fusion_all.ipynb.

Una vez generados nuestros datasets a entrenar, pasamos a la parte de aprendizaje supervisado, donde probaremos diferentes modelos y manipularemos los hiperparametros de estos para tratar de conseguir la mejor predicción. Esto se hace en los cuadernos 1_looking_predictive_model.ipynb y 2_looking_predictive_model_93_20.ipynb dentro del directorio <b>Predictive_Modelling</b>.

Tras entrenar los diferentes modelos se ha, realizado un pequeño test con *hits* que salieron posteriores a la fecha de creación del dataset y a ver si nuestros modelos son capaces de predecirlos como *hit*, esto se hace en el cuaderno 4_model_testing.ipynb.

Por último se hizo un pequeño análisis de lenguaje natural para los *hits* pertenecientes al género *pop* y al género *urban contemporary*. Para ello se hizo una extracción de las letras de las canciones de estos, que se realiza en el cuaderno 5_extract_lyrics_by_genre.ipynb dentro del directorio <b>Data_Generation</b>.

El análisis de estas letras de canciones se realiza en el cuaderno 3_analysis_lyrics.ipynb dentro del directorio <b>Hit_Data_Analysis</b>.

A continuación se muestran el orden de lectura de los *notebooks* de manera resumida.

  1. 1_data_hits_extraction.ipynb (<b>Data_Generation</b>)
  2. 2_data_hits_fusion.ipynb (<b>Data_Generation</b>)
  3. 1_hit_analysis.ipynb (<b>Hit_Data_Analysis</b>)
  4. 3_clean_dataset.ipynb (<b>Predictive_Modelling</b>)
  5. 3_data_random_extract.ipynb (<b>Data_Generation</b>)
  6. 4_data_fusion_all.ipynb (<b>Data_Generation</b>)
  7. 1_looking_predictive_model.ipynb (<b>Predictive_Modelling</b>)
  8. 2_looking_predictive_model_93_20.ipynb (<b>Predictive_Modelling</b>)
  9. 4_model_testing.ipynb (<b>Predictive_Modelling</b>)
  10. 5_extract_lyrics_by_genre.ipynb (<b>Data_Generation</b>)
  11. 3_analysis_lyrics.ipynb (<b>Hit_Data_Analysis</b>)