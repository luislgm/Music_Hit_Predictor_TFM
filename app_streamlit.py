import streamlit as st
import os
import joblib
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials  
import altair as alt
import pandas as pd
from dateutil.parser import parse

@st.cache(allow_output_mutation=True)
def init_sp():
    # Sustituir 'sp_cid' y 'sp_secret' por los tokens generados según enlace
    # https://developer.spotify.com/documentation/general/guides/app-settings/
    client_credentials_manager = SpotifyClientCredentials(client_id='sp_cid', client_secret='sp_cid') 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=50)
    return sp

def find_song(sp, artist, title):

    Searched = str (title + " " + artist)
    track = sp.search(Searched)
    try:
        id_track = track["tracks"]["items"][0]["uri"]
        track = sp.track(id_track)
        track_feat = sp.audio_features(id_track)
        song = [[track_feat[0]["danceability"], track_feat[0]["energy"], track_feat[0]["key"],
                track_feat[0]["loudness"], track_feat[0]["mode"], track_feat[0]["speechiness"],
                track_feat[0]["acousticness"], track_feat[0]["instrumentalness"], track_feat[0]["liveness"],
                track_feat[0]["valence"], track_feat[0]["tempo"],track_feat[0]["time_signature"],
                track["duration_ms"]]]

        st.write ("Canción elegida:",track["name"], "de", track["artists"][0]["name"] )
        return song
    except:
        st.write ("ERROR: Titulo no encontrado")

def find_song_year(sp, artist, title):

    Searched = str (title + " " + artist)
    track = sp.search(Searched)
    try:
        id_track = track["tracks"]["items"][0]["uri"]
        track = sp.track(id_track)
        get_year = lambda date: parse(date, fuzzy=True).year
        year_realease = get_year(track["album"]["release_date"])
        track_feat = sp.audio_features(id_track)
        song = [[year_realease, track_feat[0]["danceability"], track_feat[0]["energy"],
                track_feat[0]["key"],track_feat[0]["loudness"], track_feat[0]["mode"],
                track_feat[0]["speechiness"],track_feat[0]["acousticness"],
                track_feat[0]["instrumentalness"], track_feat[0]["liveness"],track_feat[0]["valence"],
                track_feat[0]["tempo"],track_feat[0]["time_signature"],track["duration_ms"]]]

        st.write ("Canción elegida:",track["name"], "de", track["artists"][0]["name"] )
        return song
    except:
        st.write ("ERROR: Titulo no encontrado")

def load_genres_graph():
    df_count_genres_10 = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/top_10_genres_count.csv')
    df_genres_10 = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/Top_10_Genres.csv')

    select_type = alt.selection(type="single",encodings=["x"])

    line_genres = alt.Chart(df_genres_10).mark_line().encode(
        x='year:T',
        y='count',
        color='genre'
    ).properties(
        width=650,
        height=300,
    ).interactive().transform_filter(select_type)

    bar_genres = alt.Chart(df_count_genres_10).mark_bar().encode(
        x="genre",
        y="count",
        tooltip="count",
        color="genre"
    ).add_selection(select_type)

    chart_genres = (bar_genres|line_genres)

    return chart_genres

def load_top_artists_hits():
    df_artists_bar_data = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/top_10_artists_hits.csv')

    bar_artists_chart = alt.Chart(df_artists_bar_data).mark_bar().encode(
                        x="artist",
                        y="title",
                        color="artist",
                        tooltip="title"
                        ).properties(
                        width=400,
                        height=450,
                        )
    return bar_artists_chart

def load_top_weeks_hits():
    df_weeks_bar_data = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/top_10_weeks_hits.csv')

    bar_weeks_chart = alt.Chart(df_weeks_bar_data).mark_bar().encode(
                        x="title",
                        y="weeks",
                        color="title",
                        tooltip="weeks"
                        ).properties(
                        width=400,
                        height=450,
                        )
    return bar_weeks_chart

def load_labels_evol_hits():
    df_label_10 = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/labels_hits.csv')
    df_labels_bar_data = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/labels_bar_hits.csv')

    select_type = alt.selection(type="single",encodings=["x"])

    line_labels = alt.Chart(df_label_10).mark_line().encode(
        x='year_chart:T',
        y='count',
        color='label'
    ).properties(
        width=650,
        height=300,
    ).interactive().transform_filter(select_type)

    bar_labels = alt.Chart(df_labels_bar_data).mark_bar().encode(
        x="label",
        y="id",
        tooltip="id",
        color="label"
    ).add_selection(select_type)

    chart_labels = (bar_labels|line_labels)
    return chart_labels

def load_collabs_time():
    df_collabs_time = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/collabs_time.csv')

    bar_collabs_chart = alt.Chart(df_collabs_time).mark_bar().encode(
                        x="year_chart:T",
                        y="collaboration",
                        color='year_chart',
                        tooltip=["collaboration", "year_chart"]
                        ).properties(
                        width=600,
                        height=450,
                        )
    return bar_collabs_chart

def load_artists_collabs_hits():
    df_collabs_artists = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/artists_collabs_hits.csv')

    bar_artist_collabs = alt.Chart(df_collabs_artists).mark_bar().encode(
                        x="artist",
                        y="collaboration",
                        color='artist',
                        tooltip="collaboration"
                        ).properties(
                        width=400,
                        height=450,
                        )
    return bar_artist_collabs

def load_albums_hits():
    df_albums_hits = pd.read_csv('https://raw.githubusercontent.com/luislgm/Music_Hit_Predictor_TFM/master/Data/top_albums_hits.csv')

    bar_albums_hits = alt.Chart(df_albums_hits).mark_bar().encode(
                        x="album",
                        y="title",
                        color='album',
                        tooltip=["title","album","artist"]
                        ).properties(
                        width=500,
                        height=550,
                        )
    return bar_albums_hits


def load_prediction_models(model_file):
    loaded_model = joblib.load(open(os.path.join(model_file),"rb"))
    return loaded_model


def main():
    """Music Hit Predictor ML Streamlit App"""

    st.title("Music Hit Predictor")
    st.subheader("Streamlit ML App")
    # st.image(load_image("cars_images/car1.jpg"),width=300, caption='Images')

    activities = ['Prediction','Graphics']
    choices = st.sidebar.selectbox("Select Activity",activities)

    if choices == 'Graphics':
        st.subheader("Graphics")

        st.markdown('A continuación se mostrarán gráficos interactivos obtenidos del análisis de los *hits* musicales.')
        
        st.markdown('### Top 10: artistas con más *hits*')
        bar_artists_chart = load_top_artists_hits()
        st.write(bar_artists_chart)
        st.markdown('### Top 10: canciones más semanas en *hot-100*')
        bar_weeks_chart = load_top_weeks_hits()
        st.write(bar_weeks_chart)
        st.markdown('### Evolución de sellos en el tiempo')
        st.markdown('Seleccionando sobre el gráfico de barras podemos ver el gráfico en el tiempo por separado')
        chart_labels = load_labels_evol_hits()
        st.write(chart_labels)
        st.markdown('### Evolución de géneros en el tiempo')
        st.markdown('Seleccionando sobre el gráfico de barras podemos ver el gráfico en el tiempo por separado')
        chart_genres = load_genres_graph()
        st.write(chart_genres)
        st.markdown('### Evolución de colaboraciones en el tiempo')
        bar_collabs_chart = load_collabs_time()
        st.write(bar_collabs_chart)
        st.markdown('### Top 10: artistas con más colaboraciones')
        bar_artist_collabs = load_artists_collabs_hits()
        st.write(bar_artist_collabs)
        st.markdown('### Top álbumes con más *hits*')
        bar_albums_hits = load_albums_hits()
        st.write(bar_albums_hits)


    elif choices == 'Prediction':
        st.subheader("Prediction")

        sp  = init_sp()

        model_choice = st.selectbox("Model Type",['RandomForest', 'AdaBoost','LightGBM','RandomForest_Year','AdaBoost_Year',
                                                  'LightGBM_Year','RandomForest_93_20','AdaBoost_93_20','LightGBM_93_20',
                                                  'RandomForest_93_20_year','AdaBoost_93_20_year','LightGBM_93_20_year'])
        artist = st.text_input('Input Artist:')
        title = st.text_input('Input title:') 
        
        if artist and title:
            if model_choice == 'LightGBM' or model_choice == 'AdaBoost' or model_choice == 'RandomForest' or \
             model_choice == 'LightGBM_93_20' or model_choice == 'AdaBoost_93_20' or \
             model_choice == 'RandomForest_93_20':   
                song = find_song(sp, artist,title)
            elif model_choice == 'LightGBM_Year' or model_choice == 'AdaBoost_Year' or \
            model_choice == 'RandomForest_Year' or model_choice == 'LightGBM_93_20_year' or \
            model_choice == 'AdaBoost_93_20_year' or model_choice == 'RandomForest_93_20_year':
                song = find_song_year(sp, artist,title)   
        
        if st.button('Evaluate'):
            if model_choice == 'RandomForest':
                predictor = load_prediction_models("Models/forest_model_random.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))   
            elif model_choice == 'AdaBoost':
                predictor = load_prediction_models("Models/ada_boost_model_random.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2)) 
            elif model_choice == 'LightGBM':
                predictor = load_prediction_models("Models/light_gbm_model_random.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))  
            elif model_choice == 'RandomForest_Year':
                predictor = load_prediction_models("Models/forest_model_random_year.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))  
            elif model_choice == 'AdaBoost_Year':
                predictor = load_prediction_models("Models/ada_boost_model_random_year.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))   
            elif model_choice == 'LightGBM_Year':
                predictor = load_prediction_models("Models/light_gbm_model_random_year.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))    
            elif model_choice == 'RandomForest_93_20':
                predictor = load_prediction_models("Models/forest_model_random_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))   
            elif model_choice == 'AdaBoost_93_20':
                predictor = load_prediction_models("Models/ada_boost_model_random_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2)) 
            elif model_choice == 'LightGBM_93_20':
                predictor = load_prediction_models("Models/light_gbm_model_random_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))  
            elif model_choice == 'RandomForest_93_20_year':
                predictor = load_prediction_models("Models/forest_model_random_year_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))  
            elif model_choice == 'AdaBoost_93_20_year':
                predictor = load_prediction_models("Models/ada_boost_model_random_year_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))   
            elif model_choice == 'LightGBM_93_20_year':
                predictor = load_prediction_models("Models/light_gbm_model_random_year_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))  

            st.success("Done")


if __name__ == '__main__':
    main()