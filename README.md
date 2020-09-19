# Music Hit Predictor

Este proyecto consiste en estudiar los éxitos musicales en Estados Unidos según la lista de éxitos publicada semanalmente por Billboard (*hot-100*).

En el proyecto se realizará la extracción de todos los hits musicales desde su origen, 1958, y se añadirán una serie de características proporcionadas por la API de [Billboard](https://github.com/guoguo12/billboard-charts) y la API de spotify ([spotipy](https://spotipy.readthedocs.io/en/2.13.0/)).

Tras la extracción, se realizará un análisis de los hits a lo largo del tiempo, y se obtendrán conclusiones interesantes.

Otro propósito del proyecto será buscar un modelo de predicción, dados los *features* obtenidos, se tratará de predecir el porcentaje de que una canción sea éxito. Para ello también se descargarán canciones que no han sido *hit* aleatoriamente, para así conformar un dataset de entrenamiento y test.

Por último, se extraerán las letras de las canciones de los hits según su género musical. Hemos escogido extraer las letras de los *hits* que pertenecen al género pop y al género *urban contemporary* (R&B, Hip-Hop, Rap, Trap...), con estas letras se realizara un pequeño estudio.

## Requisitos

Para poder ejecutar todos los notebooks del proyecto, se recomienda usar el entorno conda que se proporciona en el fichero environment_tfm.yml

Para la creación del entorno ejecutar:
~~~
conda env create -f environment_tfm.yml
~~~

A continuación, es necesario descargar un modelo preentrentado para la parte de NLP que usara la librería *spacy*, esto se hará con el siguiente comando en la *shell*:
 
~~~
python -m spacy download en_core_web_md
~~~
 
Por último antes de activar el entorno, hay crear el nuevo entorno como kernel de Jupyter:
~~~
python -m ipykernel install --user --name=tfm
~~~
 
Para la activación del entorno:
~~~
conda activate tfm
~~~
 
Para ejecutar los cuadernos Jupyter, estos se han lanzado con Jupyter-lab, que es la que se incluye en el entorno.
~~~
Jupyter-lab
~~~
 
Para la extracción de los datos, es necesario estar identificado y tener los *tokens* pertinentes para el uso de la API de Spotify y la API de Genius.
  - Para crear un "client id" (client_id, client_secret) para usar la API de spotify, seguir los pasos que se indican en el [enlace](https://developer.spotify.com/documentation/general/guides/app-settings/).
  - Para crear un "client_id" para usar la API de Genius. Es necesario seguir los pasos que se indican en el [enlace](https://docs.genius.com/#/getting-started-h1).
  
## Estructura del proyecto
 
En el proyecto se pueden observar las siguientes carpetas:
  - Data
  - Data_Generation
  - Hit_Data_Analysis
  - Models
  - Predictive_Modelling
 
<b>Data</b>: será donde se almacenen todos los datos generados en formato csv, esta carpeta estará vacía en git. Los datos podrán ser generados siguiendo los notebooks de la carpeta Data_Generation. Por comodidad y, ya que la generación de datos es un proceso que requiere bastante tiempo, se facilitan los ficheros en el siguiente [enlace](https://drive.google.com/drive/folders/1NyCAPqVdK4ZcOPovaSirImuEoe7fceAl?usp=sharing) de Google Drive.

<b>Data_Generation</b>: contiene todos los cuadernos y paquetes necesarios para la realización de la extracción de los datos.

<b>Hit_Data_Analysis</b>: contiene los cuadernos en los que se realiza el análisis de los datos de las canciones que han sido *hit*.

<b>Models</b>: contiene todos los modelos entrenados en formato .pkl

<b>Predictive_Modelling</b>: es donde se incluyen los cuadernos para buscar el mejor modelo de predicción.

## Orden de lectura del proyecto

En este punto se explicará la secuencia de lectura de los cuadernos para ver todo el proceso llevado a cabo, al final del punto se indicará también el orden en modo lista.

Lo primero es la generación de datos. Todo lo necesario para ello se encuentra dentro del directorio <b>Data_Generation</b>.
Se ha desarrollado un objeto, que incluye diferentes funciones para extraer los datos, esta se encuentra en music_data.py.

El orden de lectura es el siguiente:

1_data_hits_extraction.ipynb en este notebook se muestran ejemplos de la extracción de *hits*.

2_data_hits_fusion.ipynb en este notebook se realiza la fusión de todos los *hits* generados en el cuaderno anterior.

A continuación se realizó un análisis de los *hits*, esto se encuentra dentro del directorio <b>Hit_Data_Analysis</b>.

1_hit_analysis.ipynb en este cuaderno se realiza un estudio de los *hits* obtenidos.

A continuación, y ya que vamos a usar modelos de predicción sensible a *outliers*, será según lo observado en el cuaderno 1_hit_analysis.ipynb, hacer una limpieza de estos *outliers* para así, aunque hayan sido *hit* conseguir un modelo más generalizable. Esta parte se encuentra dentro del directorio <b>Predictive_Modelling</b> y corresponde con el cuaderno 1_clean_dataset.ipynb.

Lo siguiente que hicimos es generar un dataset que poder entrenar, para ello se han extraído datos de canciones aleatorias de los cuales nos quedaríamos con aquellas que no son *hit* y lo fusionaríamos con el dataset generado del cuaderno 1_clean_dataset.ipynb. Esto es hace en el cuaderno 3_data_random_extract.ipynb y 4_data_fusion_all.ipynb en el directorio <b>Data_Generation</b>.

Una vez generados nuestros datasets a entrenar, pasamos a la parte de aprendizaje supervisado, donde probaremos diferentes modelos y manipularemos los hiperparametros de estos para tratar de conseguir la mejor predicción. Esto se hace en los cuadernos 2_looking_predictive_model.ipynb y 3_looking_predictive_model_93_20.ipynb dentro del directorio <b>Predictive_Modelling</b>.

Tras entrenar los diferentes modelos, se ha realizado un pequeño test con *hits* que salieron posteriores a la fecha de creación del dataset y se vera si nuestros modelos son capaces de predecirlos como *hit*, esto se hace en el cuaderno 4_model_testing.ipynb en <b>Predictive_Modelling</b>.

Por último se hizo un pequeño análisis de lenguaje natural para los *hits* pertenecientes al género *pop* y al género *urban contemporary*. Para ello se hizo una extracción de las letras de las canciones de estos, que se realiza en el cuaderno 5_extract_lyrics_by_genre.ipynb dentro del directorio <b>Data_Generation</b>.

El análisis de estas letras de canciones se realiza en el cuaderno 2_analysis_lyrics.ipynb dentro del directorio <b>Hit_Data_Analysis</b>.

Por último se incluye una pequeña aplicación gráfica que se ejecutará a través de streamlit y nos permitirá hacer predicciones de cualquier canción de la que indiquemos su artista y titulo, y seleccionando el modelo que queramos nos dirá la probabilidad de ser un *hit*. Esta aplicación se encuentra en el directorio raíz con el nombre app_streamlit.py y para ser ejecutada seguir los pasos del punto siguiente.

A continuación se muestran el orden de lectura de los *notebooks* de manera resumida.
 
  1. 1_data_hits_extraction.ipynb (<b>Data_Generation</b>)
  2. 2_data_hits_fusion.ipynb (<b>Data_Generation</b>)
  3. 1_hit_analysis.ipynb (<b>Hit_Data_Analysis</b>)
  4. 1_clean_dataset.ipynb (<b>Predictive_Modelling</b>)
  5. 3_data_random_extract.ipynb (<b>Data_Generation</b>)
  6. 4_data_fusion_all.ipynb (<b>Data_Generation</b>)
  7. 2_looking_predictive_model.ipynb (<b>Predictive_Modelling</b>)
  8. 3_looking_predictive_model_93_20.ipynb (<b>Predictive_Modelling</b>)
  9. 4_model_testing.ipynb (<b>Predictive_Modelling</b>)
  10. 5_extract_lyrics_by_genre.ipynb (<b>Data_Generation</b>)
  11. 2_analysis_lyrics.ipynb (<b>Hit_Data_Analysis</b>)
   
## ML Streamlit App

Para ejecutar la aplicación de streamlit, antes de hacerlo es necesario sustituir los strings 'sp_cid' y 'sp_secret' en la función SpotifyClientCredentials, por los *tokens* obtenidos según se detalla en el punto de requisitos.

Para ejecutar la aplicación con streamlit.
~~~
streamlit run app_streamlit.py
~~~

La aplicación constará de dos opciones en el menú, una para hacer predicciones y otra para ver diferentes gráficos de interés.

Para hacer las predicciones, se debe elegir el modelo a utilizar. Los modelos son los siguientes:

- RandomForest: modelo de *random forest* entrenado con todo el dataset desde 1958 hasta 2020.

- AdaBoost: modelo Ada Boost entrenado con todo el dataset desde 1958 hasta 2020.
  
- LightGBM: modelo de *Gradient Boosting* implementado en LightGBM entrenado con todo el dataset desde 1958 hasta 2020.
  
- RandomForest_Year': modelo de *random forest* entrenado con todo el dataset desde 1958 hasta 2020 y que incluye el año como característica.
  
- AdaBoost_Year: modelo Ada Boost entrenado con todo el dataset desde 1958 hasta 2020 y que incluye el año como característica.
  
- LightGBM_Year: modelo de *Gradient Boosting* implementado en LightGBM entrenado con todo el dataset desde 1958 hasta 2020 y que incluye el año como característica.
  
- RandomForest_93_20: modelo de *random forest* entrenado con dataset de canciones comprendidas entre 1993 y 2020.
  
- AdaBoost_93_20: modelo de Ada boost entrenado con dataset de canciones comprendidas entre 1993 y 2020.
  
- LightGBM_93_20: modelo de *Gradient Boosting* implementado en LightGBM entrenado con dataset de canciones comprendidas entre 1993 y 2020.
  
- RandomForest_93_20_year: modelo de *random forest* entrenado con dataset de canciones comprendidas entre 1993 y 2020 y que incluye el año como característica.
  
- AdaBoost_93_20_year: modelo de Ada boost entrenado con dataset de canciones comprendidas entre 1993 y 2020 y que incluye el año como característica.
  
- LightGBM_93_20_year: modelo de *Gradient Boosting* implementado en LightGBM entrenado con dataset de canciones comprendidas entre 1993 y 2020 y que incluye el año como característica.
  
Tras seleccionar el modelo de interés, buscamos la canción que queremos predecir, insertando el artista y titulo, esperamos a que el resultado de la búsqueda sea el que esperábamos, y pulsamos sobre *evaluate*, podremos ver el porcentaje que tiene esa canción de ser un *hit* según las características musicales obtenidas.

En el apartado *Graphics* podremos ver diferentes gráficas interactivas gracias a la librería de altair. Para facilitar la ejecución de estas gráficas y no tener que generar los datos ni descargarlos de drive, se han alojado en el repositorio.
