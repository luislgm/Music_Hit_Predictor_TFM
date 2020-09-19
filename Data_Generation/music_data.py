import pandas as pd
import numpy as np
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import billboard
import datetime
import lyricsgenius
import re
import time
from dateutil.parser import parse

class Music_Data:
    def __init__ (self,sp_cid,sp_secret,ge_token):
        """
        :param sp_cid: client_id required to initialize spotify API
        :param sp_secret: secret_id required to initialize spotify API
        :param ge_token: client_id required to initialize Genius API
        
        To create a client_id for spotify API (spotipy):
        https://developer.spotify.com/documentation/general/guides/app-settings
        To create a client_id for genius API (lyricsgenius):
        https://docs.genius.com/#/getting-started-h1
        """
        client_credentials_manager = SpotifyClientCredentials(client_id=sp_cid, client_secret=sp_secret) 
        self._sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=50) 
        self._genius = lyricsgenius.Genius(client_access_token=ge_token,verbose=False, timeout=50)
        
    def Get_Billboard_Data (self, start_date_str, end_date_str):  
        """ function that allows to obtain in a date range,
        the billboard hot-100, with its musical parameters obtained from the Spotify API.
        Arguments:
            start_date_str {[str]} -- In format "dd-mm-YYYY"
            end_date_str {[str]} -- In format "dd-mm-YYYY"
        Returns:
            [pd.DataFrame] -- dataframe that contains all the information described.
        """
        # Se define dataframe con estructura
        df = pd.DataFrame(columns=("artist", "title","id","year_chart","date_chart","release_date","collaboration","rank",
                                   "weeks","isNew","peakPos","lastPos","danceability","energy","key","loudness","mode",
                                   "speechiness","acousticness","instrumentalness","liveness", "valence", "tempo",
                                   "time_signature","duration_ms","popularity_artist", "popularity_song", "genres","album", 
                                   "label"))
        
        # Se define función que indica si una canción es colaboración.
        collab = lambda a : True if len(a) > 1 else False
        # Se define función que extrae año de una fecha
        year = lambda date: parse(date, fuzzy=True).year

        start_date = datetime.datetime.strptime(start_date_str, '%d-%m-%Y')
        end_date = datetime.datetime.strptime(end_date_str, '%d-%m-%Y')
        delta = datetime.timedelta(days=7)
        while start_date <= end_date:
            formatted_date = start_date.strftime('%Y-%m-%d')
            try:
                chart = billboard.ChartData('hot-100', date = formatted_date, timeout=300)
            except:
                time.sleep(3*60)
                chart = billboard.ChartData('hot-100', date = formatted_date, timeout=300) 
            for entry in chart.entries:
                # En Billboard el nombre de los artistas que colaboran en la canción aparecen de manera diferente
                # a como se encuentran en spotify por lo que las búsquedas dan muchos errores y es por ello que nos
                # quedamos con el artista principal de la canción.
                artist = entry.artist.split("Featuring")[0]
                artist = artist.split (",")[0]
                artist_sp = artist.split (" & ")[0]
                artist_sp = artist_sp.split(" X ")[0]
                artist_sp = artist_sp.split(" x ")[0]
                # Creamos un string de búsqueda con el título y artista
                Searched = str (entry.title + " " + artist_sp)
                track = self._sp.search(Searched)
                if track["tracks"]["total"] == 0:
                # En caso de que no se encuentre búsqueda, procedemos a limpiar el título de caracteres y partes que puedan 
                # dificultar la búsqueda
                    title_sp = re.sub(r'\w*[*]\w*', '', entry.title)
                    title_sp = re.sub(r'\([^)]*\)', '', title_sp)
                    title_sp = title_sp.split("/")[0]
                    Searched = str (title_sp + " " + artist_sp)
                    track = self._sp.search(Searched)
                # En caso de que no se encuentre canción, se mostrara un error y no se añadirá al dataframe.
                if track["tracks"]["total"] > 0:
                    id_track = track["tracks"]["items"][0]["uri"]
                    track = self._sp.track(id_track)
                    collabs = collab(track["artists"])
                    album = self._sp.album(track["album"]["uri"])
                    label = album["label"]
                    release_date = track["album"]["release_date"]
                    popularity_song = track['popularity']
                    artist_info = self._sp.artist(track["album"]['artists'][0]["uri"])
                    track_feat = self._sp.audio_features(id_track)
                    year_chart = year(chart.date)
                    df.loc[len(df)] = [track["artists"][0]["name"],track["name"],track["id"], year_chart,chart.date, 
                                       release_date,collabs, entry.rank,entry.weeks,entry.isNew, entry.peakPos,
                                       entry.lastPos,track_feat[0]["danceability"],track_feat[0]["energy"],
                                       track_feat[0]["key"],track_feat[0]["loudness"],track_feat[0]["mode"],
                                       track_feat[0]["speechiness"],track_feat[0]["acousticness"],
                                       track_feat[0]["instrumentalness"],track_feat[0]["liveness"],
                                       track_feat[0]["valence"],track_feat[0]["tempo"],
                                       track_feat[0]["time_signature"],track["duration_ms"],
                                       artist_info['popularity'],popularity_song, artist_info["genres"],
                                       track["album"]["name"],label]
                    print ("Added song:", entry.title, "Artist:", artist)
                else:
                    print ("\033[0;00;41m", Searched, "not found on spotify\033[0;00;00m")
            print("\033[0;00;42mDownloaded: ", chart.date, "\033[0;00;00m")
            # Aumentamos la fecha de búsqueda una semana
            start_date += delta
        return df

    def Get_Billboard_Data_Lyrics (self, start_date_str, end_date_str):  
        """ function that allows to obtain in a date range,
        the billboard hot-100, with its musical parameters obtained from the Spotify API
        and the lyrics of each song obtained through the Genius API.
        Arguments:
            start_date_str {[str]} -- In format "dd-mm-YYYY"
            end_date_str {[str]} -- In format "dd-mm-YYYY"
        Returns:
            [pd.DataFrame] -- dataframe that contains all the information described.
        """
        # Se define dataframe con estructura
        df = pd.DataFrame(columns=("artist", "title","id","year_chart","date_chart","release_date","collaboration","rank",
                                   "weeks","isNew","peakPos","lastPos","danceability","energy","key","loudness","mode",
                                   "speechiness","acousticness","instrumentalness","liveness", "valence", "tempo",
                                   "time_signature","duration_ms","popularity_artist", "popularity_song", "genres","album", 
                                   "label", "song_lyrics"))
        
        # Se define función que indica si una canción es colaboración.       
        collab = lambda a : True if len(a) > 1 else False
        # Se define función que extrae año de una fecha
        year = lambda date: parse(date, fuzzy=True).year

        start_date = datetime.datetime.strptime(start_date_str, '%d-%m-%Y')
        end_date = datetime.datetime.strptime(end_date_str, '%d-%m-%Y')
        delta = datetime.timedelta(days=7)
        while start_date <= end_date:
            formatted_date = start_date.strftime('%Y-%m-%d')
            try:
                chart = billboard.ChartData('hot-100', date = formatted_date, timeout=300)
            except:
                time.sleep(3*60)
                chart = billboard.ChartData('hot-100', date = formatted_date, timeout=300) 
            for entry in chart.entries:
                # En Billboard el nombre de los artistas que colaboran en la canción aparecen de manera diferente
                # a como se encuentran en spotify por lo que las búsquedas dan muchos errores y es por ello que nos
                # quedamos con el artista principal de la canción.
                artist = entry.artist.split("Featuring")[0]
                artist = artist.split (",")[0]
                artist_sp = artist.split (" & ")[0]
                artist_sp = artist_sp.split(" X ")[0]
                artist_sp = artist_sp.split(" x ")[0]
                # Eliminamos contenido entre paréntesis en títulos de canciones, ya que origina problemas en la búsqueda
                # en genius
                title_ge = re.sub(r'\([^)]*\)', '', entry.title)
                # Debido al exceso de peticiones realizadas, en caso de que se nos deniegue la petición, esperamos un tiempo
                # suficiente para volver a realizar la petición.
                try:
                    song = self._genius.search_song(title_ge,artist=artist_sp)
                except:
                    time.sleep(5*60)
                    song = self._genius.search_song(title_ge,artist=artist_sp)
                if not song:
                    # Si no podemos encontrar la canción, uno de los errores comunes es que la búsqueda contenga caracteres
                    # "*" que ocurre en nombres explícitos de la canción. En genius los nombres suelen encontrarse de forma
                    # explicita por lo que la mejor manera de solventar este error es eliminando aquellas palabras que lo 
                    # contengan y realizar de nuevo la búsqueda
                        artist_ge = re.sub(r'\w*[*]\w*', '', artist_sp)
                        title_ge = re.sub(r'\w*[*]\w*', '', title_ge)
                        song = self._genius.search_song(title_ge,artist=artist_ge)
                        if song:
                            lyric = song.lyrics
                        else:
                        # Ciertos artistas principales pueden ser difíciles de encontrar en genius debido a cómo aparecen
                        # así que nos quedamos con la primera palabra del artista en caso de que las búsquedas anteriores
                        # no hayan funcionado.
                            artist_ge = artist_ge.split (" ")[0]
                            song = self._genius.search_song(title_ge,artist=artist_ge)
                            if song:
                                lyric = song.lyrics
                            else:
                                lyric = np.nan
                else:
                    lyric = song.lyrics
                # Creamos un string de búsqueda con el título y artista
                Searched = str (entry.title + " " + artist_sp)
                track = self._sp.search(Searched)
                if track["tracks"]["total"] == 0:
                # En caso de que no se encuentre búsqueda, procedemos a limpiar el título de caracteres y partes que puedan 
                # dificultar la búsqueda
                    title_sp = re.sub(r'\w*[*]\w*', '', entry.title)
                    title_sp = re.sub(r'\([^)]*\)', '', title_sp)
                    title_sp = title_sp.split("/")[0]
                    Searched = str (title_sp + " " + artist_sp)
                    track = self._sp.search(Searched)
                # En caso de que no se encuentre canción, se mostrara un error y no se añadirá al dataframe.
                if track["tracks"]["total"] > 0:
                    id_track = track["tracks"]["items"][0]["uri"]
                    track = self._sp.track(id_track)
                    collabs = collab(track["artists"])
                    album = self._sp.album(track["album"]["uri"])
                    label = album["label"]
                    release_date = track["album"]["release_date"]
                    popularity_song = track['popularity']
                    artist_info = self._sp.artist(track["album"]['artists'][0]["uri"])
                    track_feat = self._sp.audio_features(id_track)
                    year_chart = year(chart.date)
                    df.loc[len(df)] = [track["artists"][0]["name"],track["name"],track["id"], year_chart,chart.date, 
                                       release_date,collabs, entry.rank,entry.weeks,entry.isNew, entry.peakPos,
                                       entry.lastPos,track_feat[0]["danceability"],track_feat[0]["energy"],
                                       track_feat[0]["key"],track_feat[0]["loudness"],track_feat[0]["mode"],
                                       track_feat[0]["speechiness"],track_feat[0]["acousticness"],
                                       track_feat[0]["instrumentalness"],track_feat[0]["liveness"],
                                       track_feat[0]["valence"],track_feat[0]["tempo"],
                                       track_feat[0]["time_signature"],track["duration_ms"],
                                       artist_info['popularity'],popularity_song, artist_info["genres"],
                                       track["album"]["name"],label,lyric]
                    print ("Added song:", entry.title, "Artist:", artist)
                else:
                    print ("\033[0;00;41m", Searched, "not found on spotify\033[0;00;00m")
            print("\033[0;00;42mDownloaded: ", chart.date, "\033[0;00;00m")
            # Aumentamos la fecha de búsqueda una semana
            start_date += delta
        return df
    
    def Get_User_Playlist_Data (self, user):
        """ function that allows to obtain from a specific user all the information of his songs
        that appear in his public playlist.
        Arguments:
            user {[str]} -- User from whom you want to get all the data from your playlists.
        Returns:
             [pd.DataFrame] -- dataframe that contains all the information described.
        """
        # Se define dataframe con estructura
        df = pd.DataFrame(columns=('artist','title',"id", "release_date","collaboration",
                                   "danceability","energy","key","loudness",
                                   "mode","speechiness","acousticness","instrumentalness","liveness", "valence",
                                   "tempo","time_signature","duration_ms","popularity_artist",
                                   "popularity_song","genres","album","label"))
        
        # Se define función que indica si una canción es colaboración.        
        collab = lambda a : True if len(a) > 1 else False

        # Se obtienen todas las playlists públicas del usuario
        playlists = self._sp.user_playlists(user)
        while playlists:
            # Para cada playlist, sé ira cogiendo cada una de las canciones para obtener la información de cada una
            # de ellas.
            for i, playlist in enumerate(playlists['items']):
                print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))  
                tracks = self._sp.playlist_tracks(playlists["items"][i]["id"])
                for i, track in enumerate(tracks['items']):
                    # Puede haber canciones en la playlist que no estén más disponibles aunque sigan en la playlist, así que
                    # la obviamos y vamos a la siguiente
                    try:  
                        id_track = track["track"]["id"]
                        track = self._sp.track(track["track"]["id"])
                        collabs = collab(track["artists"])
                        album = self._sp.album(track["album"]["uri"])
                        release_date = track["album"]["release_date"]
                        popularity_song = track['popularity']
                        artist_info = self._sp.artist(track["album"]['artists'][0]["uri"])
                        track_feat= self._sp.audio_features (id_track)

                        df.loc[len(df)] = (track["artists"][0]["name"],track["name"],track["id"],
                                           release_date, collabs, track_feat[0]["danceability"],
                                           track_feat[0]["energy"], track_feat[0]["key"],
                                           track_feat[0]["loudness"],track_feat[0]["mode"],
                                           track_feat[0]["speechiness"],track_feat[0]["acousticness"],
                                           track_feat[0]["instrumentalness"],track_feat[0]["liveness"],
                                           track_feat[0]["valence"],track_feat[0]["tempo"],
                                           track_feat[0]["time_signature"],track["duration_ms"],
                                           artist_info['popularity'], popularity_song,
                                           artist_info["genres"],track["album"]["name"],album["label"])
                    except:
                        pass           
            if playlists['next']:
                playlists = self._sp.next(playlists)
            else:
                playlists = None
        return df
    def Get_User_Playlist_Data_Lyrics (self, user):
        """ function that allows to obtain from a specific user all the information of his songs
        that appear in his public playlists and his lyrics.
        Arguments:
            user {[str]} -- User from whom you want to get all the data from your playlists.
        Returns:
             [pd.DataFrame] -- dataframe that contains all the information described.
        """
        # Se define dataframe con estructura
        df = pd.DataFrame(columns=('artist','title',"id", "release_date", "collaboration",
                                   "danceability","energy","key","loudness", "mode", "speechiness", 
                                   "acousticness","instrumentalness","liveness", "valence",
                                   "tempo","time_signature","duration_ms","popularity_artist","popularity_song",
                                   "genres","album","label","song_lyrics"))
        
       # Se define función que indica si una canción es colaboración.          
        collab = lambda a : True if len(a) > 1 else False

        # Se obtienen todas las playlists públicas del usuario
        playlists = self._sp.user_playlists(user)
        while playlists:
            # Para cada playlist, sé ira cogiendo cada una de las canciones para obtener la información de cada una
            # de ellas.
            for i, playlist in enumerate(playlists['items']):
                print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))  
                tracks = self._sp.playlist_tracks(playlists["items"][i]["id"])
                for i, track in enumerate(tracks['items']):
                    # Puede haber canciones en la playlist que no estén más disponibles aunque sigan en la playlist, así que
                    # la obviamos y vamos a la siguiente
                    try:   
                        id_track = track["track"]["id"]
                        track = self._sp.track(track["track"]["id"])
                        collabs = collab(track["artists"])
                        album = self._sp.album(track["album"]["uri"])
                        release_date = track["album"]["release_date"]
                        popularity_song = track['popularity']
                        artist_info = self._sp.artist(track["album"]['artists'][0]["uri"])
                        track_feat= self._sp.audio_features (id_track)

                        # Eliminamos contenido entre paréntesis en títulos de canciones, ya que origina problemas en 
                        # la búsqueda en genius
                        title_ge = re.sub(r'\([^)]*\)', '', track["name"])
                        # Debido al exceso de peticiones realizadas, en caso de que se nos deniegue la petición,
                        # esperamos un tiempo suficiente para volver a realizar la petición.
                        try:
                            song = self._genius.search_song(title_ge,artist=track["artists"][0]["name"])
                        except:
                            time.sleep(5*60)
                            song = self._genius.search_song(title_ge,artist=track["artists"][0]["name"])

                        if not song:
                        # Si no podemos encontrar la canción, uno de los errores comunes es que la búsqueda contenga
                        # caracteres "*" que ocurre en nombres explícitos de la canción. En genius los nombres suelen
                        # encontrarse de forma explicita por lo que la mejor manera de solventar este error es eliminando
                        # aquellas palabras que lo contengan y realizar de nuevo la búsqueda
                            artist_ge = re.sub(r'\w*[*]\w*', '', track["artists"][0]["name"])
                            title_ge = re.sub(r'\w*[*]\w*', '', title_ge)
                            song = self._genius.search_song(title_ge,artist=artist_ge)
                            if song:
                                lyric = song.lyrics
                            else:
                                # Ciertos artistas principales pueden ser difíciles de encontrar en genius debido a
                                # cómo aparecen, así que nos quedamos con la primera palabra del artista en caso de que
                                # las búsquedas anteriores no hayan funcionado.
                                artist_ge = artist_ge.split (" ")[0]
                                song = self._genius.search_song(title_ge,artist=artist_ge)
                                if song:
                                    lyric = song.lyrics
                                else:
                                    lyric = np.nan
                        else:
                            lyric = song.lyrics

                        df.loc[len(df)] = (track["artists"][0]["name"],track["name"],track["id"],
                                           release_date, collabs, track_feat[0]["danceability"],
                                           track_feat[0]["energy"], track_feat[0]["key"],
                                           track_feat[0]["loudness"],track_feat[0]["mode"],
                                           track_feat[0]["speechiness"],track_feat[0]["acousticness"],
                                           track_feat[0]["instrumentalness"],track_feat[0]["liveness"],
                                           track_feat[0]["valence"],track_feat[0]["tempo"],
                                           track_feat[0]["time_signature"],track["duration_ms"],
                                           artist_info['popularity'], popularity_song,
                                           artist_info["genres"],track["album"]["name"],
                                           album["label"], lyric)
                    except:
                        pass    
            
            if playlists['next']:
                playlists = self._sp.next(playlists)
            else:
                playlists = None
        return df
    def Get_Lyrics (self, df):
        """ function that given a dataframe with songs previously generated with Get_User_Playlist_Data or             
        Get_Billboard_Data, adds the lyrics of the songs to each one of them.
        Arguments:
            df {[pd.DataFrame]} -- Dataframe previously generated with the function Get_User_Playlist_Data or 
            Get_Billboard_Data.
        Returns:
             [pd.DataFrame] -- Dataframe with added song lyrics.
             [pd.DataFrame] -- Dataframe with songs found by manipulating the titles and artists and not found for review
             In Dataframe to_review = True It means that it has been found manipulating the titles and artist
             to_review = False It means that it has been not found
        """
        df_lyrics = pd.DataFrame.copy(df)
        df_lyrics.assign(lyric=None)
        df_review = pd.DataFrame(columns=('artist','title','id','found'))
        j = 0

        for i, item in df.iterrows():
            # Eliminamos contenido entre paréntesis en títulos de canciones, ya que origina problemas en la búsqueda
            # en genius
            title_ge = re.sub(r'\([^)]*\)', '', item["title"])
            # Debido al exceso de peticiones realizadas, en caso de que se nos deniegue la petición,
            # esperamos un tiempo suficiente para volver a realizar la petición.          
            try:
                song = self._genius.search_song(title_ge,artist=item["artist"])
            except:
                time.sleep(5*60)
                song = self._genius.search_song(title_ge,artist=item["artist"])

            # Aunque podamos hacer la petición, se ha visto para este caso, ya que el número de llamadas por segundo es
            # mayor que en los demás casos, que la búsqueda falla aunque si se exista la información, por lo que para
            # tratar de solventar este problema, se prueba a realizar la llamada un máximo de 4 veces,
            # para intentar conseguir la información si es debido a esta casuística.
            k = 1
            while not song:
                try:
                    song = self._genius.search_song(title_ge,artist=item["artist"])
                except:
                    time.sleep(5*60)
                    song = self._genius.search_song(title_ge,artist=item["artist"])
                if k== 4:
                    break
                k += 1

            if not song:
            # Sino podemos encontrar la canción, uno de los errores comunes es que la búsqueda contenga caracteres "*"
            # que ocurre en nombres explícitos de la canción. En genius los nombres suelen encontrarse de forma explicita
            # por lo que la mejor manera de solventar este error es eliminando aquellas palabras que lo contengan y
            # realizar de nuevo la búsqueda

                artist_ge = re.sub(r'\w*[*]\w*', '', item["artist"])
                title_ge = re.sub(r'\w*[*]\w*', '', title_ge)
                try:
                    song = self._genius.search_song(title_ge,artist=artist_ge)
                except:
                    time.sleep(5*60)
                    song = self._genius.search_song(title_ge,artist=artist_ge)
                    
                if song:
                    lyric = song.lyrics
                    to_review = True
                else:
                    # Ciertos artistas principales pueden ser difíciles de encontrar en genius debido a cómo aparecen,
                    # así que nos quedamos con la primera palabra del artista en caso de que las búsquedas anteriores no
                    # hayan funcionado.
                    artist_ge = artist_ge.split (" ")[0]
                    title_ge = title_ge.split("-")[0]
                    try:
                        song = self._genius.search_song(title_ge,artist=artist_ge)
                    except:
                        time.sleep(5*60)
                        song = self._genius.search_song(title_ge,artist=artist_ge)
                    if song:
                        lyric = song.lyrics
                        to_review = True
                    else:
                        lyric = np.nan
                        to_review = False
            else:
                lyric = song.lyrics
                to_review = False

            if song:
                print ("Added lyric:", item["title"],"Artist:",item["artist"]) 
                # En caso de que se haya encontrado el título, pero a partir de manipulación, lo incluimos en el Dataframe 
                # de revisión.
                if to_review == True:
                    df_review.loc[j,'artist'] = item["artist"]
                    df_review.loc[j,'title'] = item["title"]
                    df_review.loc[j,'id'] = item["id"]
                    df_review.loc[j,'found'] = to_review
                    j += 1
            # En caso de titulo no encontrado, se muestra error y se añade a Dataframe de revisión
            else:
                df_review.loc[j,'artist'] = item["artist"]
                df_review.loc[j,'title'] = item["title"]
                df_review.loc[j,'id'] = item["id"]
                df_review.loc[j,'found'] = to_review
                j += 1
                print ("\033[0;00;41mNot found lyric:", item["title"],"Artist:",item["artist"],"\033[0;00;00m")

                
            df_lyrics.loc[i,"song_lyrics"]=lyric
        return df_lyrics, df_review