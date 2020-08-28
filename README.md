# Music Hit Predictor

Este proyecto consiste en estudiar los exitos musicales en Estados Unidos segun la lista de exitos publicada semanalmente por Billboard (hot-100s).

En el proyecto se realizará la extraccion de todos los hits musicales desde su origen, 1958, y se añadiran una serie de caracteristicas proporcionadas por la API de [Billboard](https://github.com/guoguo12/billboard-charts) y la API de spotify ([spotipy](https://spotipy.readthedocs.io/en/2.13.0/)).

Tras la extracción, se realizará un analisis de los hits a lo largo del tiempo, y se obtendran conclusiones interesantes.

Otro proposito del proyecto será buscar un modelo de predicción, dados los features obtenidos, predecir si el porcentaje de que una canción sea exito o no. Para ello se descargarán canciones que no han sido hit aleatoriamente, conformando un dataset de entrenamiento.

## Estructura del proyecto

En el proyecto se pueden observar las siguientes carpetas:
  - Data
  - Data_Generation
  - Hit_Data_Analysis
  - Predictive_Modelling

<b>Data</b> será donde se almacenen todos los datos generados en formato csv, esta carpeta estará vacia en git. Los datos podran ser generados siguiendo los notebook de la carpeta Data_Generation. Por comodidad y ya que la generación de datos es un proceso que requiere bastante tiempo, se facilitan los ficheros en el siguiente link de Google Drive.

<b>Data_Generation</b>, contendra todos los notebooks y paquetes necesarios para la realizacion de la extracción de los datos.

<b>Hit_Data_Analysis</b>, contiene los notebook en los que se realiza el analisis de los datos de las canciones que han sido hit.

<b>Predictive_Modelling</b>, es donde se incluyen los notebook para buscar el mejor modelo de predicción.

## Requerimientos

Para la extracción de los datos, es necesario estar identificado y tener los token perminentes para el uso de la API de Spotify y la API de Genius.
  - Para crear un "client id" para usar la API de spotify, seguir los pasos que se indican en el [enlace](https://developer.spotify.com/documentation/general/guides/app-settings/).
  - Para crear un "client_id" para usar la API de Genius. Es necesario seguir los pasos que se indican en el [enlace](https://docs.genius.com/#/getting-started-h1).

## Orden de lectura del proyecto

A continuacion se explicara la secuencia de lectura de los notebook para ver todo el proceso llevado a cabo.

Lo primero es la generación de datos. Todo lo necesario para ello se encuentra dentro del directorio <b>Data_Generation</b>.
Se ha desarrollado un Objeto, que incluye diferentes funciones para extraer los datos, esta se encuentre en music_data.py.

1_data_hits_extraction.ipynb en este notebook se muestran ejemplos de la extraccion de hits.

2_data_hits_fusion.ipynb en este notebook se realiza la fusion de todos los datos generados en el cuaderno anterior.

3_data_random_extract.ipynb en este notebook se realiza la extraccion de canciones aleatorias, que posteriormente se fusionaran con los hits para tener un dataset que podamos usar para entrenar usando las tecnicas de machine learning.

4_data_fusion_all.ipynb en este notebook se realiza la fusion de los datos aleatorios con los hits.

A continuación se realizo un analisis de los hits, esto se encuentra dentro del directorio <b>Hit_Data_Analysis</b>.

1_hit_analysis.ipynb en este cuaderno se realiza un estudio de los datos obtenidos.

Tras este punto se trabajo en la busqueda de un modelo de prediccion, esto se encuentra en el directorio <b>Predictive_Modelling</b>.

1_looking_predictive_model.ipynb, en este cuaderno se realizan diferentes pruebas aplicando diferente modelos y realizando un estudio de los resultados obtenidos.