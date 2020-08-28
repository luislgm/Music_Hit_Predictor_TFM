import streamlit as st
import os
import joblib
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

#@st.cache
def find_song(artist, title):

    client_credentials_manager = SpotifyClientCredentials(client_id='spotipy_id', client_secret='secret_id') 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=50)
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

def load_prediction_models(model_file):
    loaded_model = joblib.load(open(os.path.join(model_file),"rb"))
    return loaded_model


def main():
    """Music Hit Predictor ML Streamlit App"""

    st.title("Music Hit Predictor")
    st.subheader("Streamlit ML App")
    # st.image(load_image("cars_images/car1.jpg"),width=300, caption='Images')

    activities = ['EDA','Prediction','Gallery','About']
    choices = st.sidebar.selectbox("Select Activity",activities)

    if choices == 'Prediction':
        st.subheader("Prediction")
        artist = st.text_input('Input Artist:')
        title = st.text_input('Input title:') 
        
        if artist and title:
            song = find_song(artist,title)      
        
        model_choice = st.selectbox("Model Type",['LightGBM'])
        if st.button('Evaluate'):
            if model_choice == 'LightGBM':
                predictor = load_prediction_models("finalized_model.sav")
                prediction = predictor.predict_proba(song)
                st.write("Hit: ",round(prediction[0][1]*100,2))                

            st.success("Done")


if __name__ == '__main__':
    main()