import streamlit as st
import os
import joblib
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials  
import altair as alt
import pandas as pd
import requests
from io import StringIO

@st.cache(allow_output_mutation=True)
def init_sp():
    # Sustituir 'sp_cid' y 'sp_secret' por los tokens generados según enlace
    # https://developer.spotify.com/documentation/general/guides/app-settings/
    client_credentials_manager = SpotifyClientCredentials(client_id='sp_cid', client_secret='sp_secret') 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=50)
    return sp

def find_song(sp, artist, title, year):

    Searched = str (title + " " + artist)
    track = sp.search(Searched)
    try:
        if year == False:
            id_track = track["tracks"]["items"][0]["uri"]
            track = sp.track(id_track)
            track_feat = sp.audio_features(id_track)
            song = [[track_feat[0]["danceability"], track_feat[0]["energy"], track_feat[0]["key"],
            track_feat[0]["loudness"], track_feat[0]["mode"], track_feat[0]["speechiness"],
            track_feat[0]["acousticness"], track_feat[0]["instrumentalness"], track_feat[0]["liveness"],
            track_feat[0]["valence"], track_feat[0]["tempo"],track_feat[0]["time_signature"],
                    track["duration_ms"]]]
        else:
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

@st.cache
def load_genres_graph():
    orig_url='https://drive.google.com/file/d/1wH2rOa92PLzx6eE_8yewKzuGt7Wzn9Gp/view?usp=sharing'
    file_id = orig_url.split('/')[-2]
    dwn_url='https://drive.google.com/uc?export=download&id=' + file_id
    url = requests.get(dwn_url).text
    csv_raw = StringIO(url)
    df_count_genres_10 = pd.read_csv(csv_raw)
    orig_url='https://drive.google.com/file/d/1RzD4L5i8NhEd9p4ez1sP5UOI9zb21JJa/view?usp=sharing'
    file_id = orig_url.split('/')[-2]
    dwn_url='https://drive.google.com/uc?export=download&id=' + file_id
    url = requests.get(dwn_url).text
    csv_raw = StringIO(url)
    df_genres_10 = pd.read_csv(csv_raw)

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
        color="genre"
    ).add_selection(select_type)

    chart_genres = (bar_genres|line_genres)

    return chart_genres

def load_prediction_models(model_file):
    loaded_model = joblib.load(open(os.path.join(model_file),"rb"))
    return loaded_model


def main():
    """Music Hit Predictor ML Streamlit App"""

    st.title("Music Hit Predictor")
    st.subheader("Streamlit ML App")
    # st.image(load_image("cars_images/car1.jpg"),width=300, caption='Images')

    activities = ['Prediction','Gallery']
    choices = st.sidebar.selectbox("Select Activity",activities)

    if choices == 'Gallery':
        st.subheader("Gallery")

        chart_genres = load_genres_graph()
        st.write(chart_genres)
        
        st.image('Figures/top_10_hits.png')
        st.image('Figures/top_10_weeks.png')
        st.image('Figures/top_albums_hit.png')
        st.image('Figures/top_artist_collabs.png')
        st.image('Figures/collabs_time.png')


    elif choices == 'Prediction':
        st.subheader("Prediction")

        sp  = init_sp()

        model_choice = st.selectbox("Model Type",['RandomForest', 'AdaBoost','LightGBM','RandomForest_Year','AdaBoost_Year',
                                                  'LightGBM_Year','RandomForest_93_20','AdaBoost_93_20','LightGBM_93_20',
                                                  'RandomForest_93_20_year','AdaBoost_93_20_year','LightGBM_93_20_year'])
        artist = st.text_input('Input Artist:')
        title = st.text_input('Input title:') 
        
        if artist and title:
            if model_choice == 'LightGBM' or model_choice == 'AdaBoost' or model_choice == 'RandomForest':   
                song = find_song(sp, artist,title,False)
            elif model_choice == 'LightGBM_Year' or model_choice == 'AdaBoost_Year' or model_choice == 'RandomForest_Year':
                song = find_song(sp, artist,title,True)   
        
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
                predictor = load_prediction_models("Models/ada_boost_random_year_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))   
            elif model_choice == 'LightGBM_93_20_year':
                predictor = load_prediction_models("Models/light_gbm_model_random_year_93_20.pkl")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))  

            st.success("Done")


if __name__ == '__main__':
    main()