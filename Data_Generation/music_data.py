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
        self._sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) 
        self._genius = lyricsgenius.Genius(client_access_token=ge_token,verbose=False,
                                remove_section_headers=True, timeout=50)
        
    def Get_Billboard_Data (self, start_date_str, end_date_str):  
        """ function that allows to obtain in a date range,
        the billboard hot-100, with its musical parameters obtained from the Spotify API
        and the lyrics of each song obtained through the Genius API.
        Arguments:
            start_date_str {[str]} -- In format "dd-mm-YYYY"
            end_date_str {[str]} -- In format "dd-mm-YYYY"
        Returns:
            [pd.DataFrame] -- dataframe that contains all the information described.
        """
        # We define dataframe structure
        df = pd.DataFrame(columns=("artist", "title","id","year_chart","date_chart","release_date","collaboration","rank",
                                   "weeks","isNew","peakPos","lastPos","danceability","energy","key","loudness","mode",
                                   "speechiness","acousticness","instrumentalness","liveness", "valence", "tempo",
                                   "time_signature","duration_ms","popularity_artist", "popularity_song", "genres","album", 
                                   "label", "song_lyrics"))
        
        # We define function to know if song has collaboration.        
        collab = lambda a : True if len(a) > 1 else False
        # we define function to take year of date
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
                # On Billboard the name of the artists is followed by other artists who collaborate on the song.
                # On Spotify it appears differently, so with the name of the main artist it will be enough to find the
                # song.
                artist = entry.artist.split("Featuring")[0]
                artist = artist.split (",")[0]
                artist_sp = artist.split (" & ")[0]
                artist_sp = artist_sp.split(" X ")[0]
                artist_sp = artist_sp.split(" x ")[0]
                # We remove those words in parentheses. Since they cause problems in search in Genius
                title_ge = re.sub(r'\([^)]*\)', '', entry.title)
                # Due to the excess of requests made, in case of denial of the request, we waited long enough to request it
                # again.
                try:
                    song = self._genius.search_song(title_ge,artist=artist_sp)
                except:
                    time.sleep(5*60)
                    song = self._genius.search_song(title_ge,artist=artist_sp)
                if not song:
                    # If we can't find the song, it may be that the search contains "*" characters. Genius does not usually
                    # contain the ones in the name songs or name artist, but the explicit word appears. We eliminate the
                    # word, since the search will give correct, with the other information.
                        artist_ge = re.sub(r'\w*[*]\w*', '', artist_sp)
                        title_ge = re.sub(r'\w*[*]\w*', '', title_ge)
                        song = self._genius.search_song(title_ge,artist=artist_ge)
                        if song:
                            lyric = song.lyrics
                        else:
                            # Certain main artists can be difficult to find in genius because of how they appear on
                            # billboard, so we are left with the first word of the artist in case the previous searches
                            # have not worked.
                            artist_ge = artist_ge.split (" ")[0]
                            song = self._genius.search_song(title_ge,artist=artist_ge)
                            if song:
                                lyric = song.lyrics
                            else:
                                lyric = np.nan
                else:
                    lyric = song.lyrics
                # we create the search string that spotify needs
                Searched = str (entry.title + " " + artist_sp)
                track = self._sp.search(Searched)
                if track["tracks"]["total"] == 0:
                    title_sp = re.sub(r'\w*[*]\w*', '', entry.title)
                    title_sp = re.sub(r'\([^)]*\)', '', title_sp)
                    title_sp = title_sp.split("/")[0]
                    Searched = str (title_sp + " " + artist_sp)
                    track = self._sp.search(Searched)
                # In case the title was not found, a error message is displayed and is not added to the dataframe.
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
            # To search on the following week
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
        df = pd.DataFrame(columns=('artist','title',"id", "release_date","collaboration",
                                   "danceability","energy","key","loudness",
                                   "mode","speechiness","acousticness","instrumentalness","liveness", "valence",
                                   "tempo","time_signature","duration_ms","popularity_artist",
                                   "popularity_song","genres","album","label"))
        
        # We define function to know if song has collaboration.        
        collab = lambda a : True if len(a) > 1 else False

        # All user playlists are obtained
        playlists = self._sp.user_playlists(user)
        while playlists:
            # For each playlist, all the songs will be taken to obtain the information of each one of them.
            for i, playlist in enumerate(playlists['items']):
                print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))  
                tracks = self._sp.playlist_tracks(playlists["items"][i]["id"])
                for i, track in enumerate(tracks['items']):
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
        df = pd.DataFrame(columns=('artist','title',"id", "release_date", "collaboration",
                                   "danceability","energy","key","loudness", "mode", "speechiness", 
                                   "acousticness","instrumentalness","liveness", "valence",
                                   "tempo","time_signature","duration_ms","popularity_artist","popularity_song",
                                   "genres","album","label","song_lyrics"))
        
        # We define function to know if song has collaboration.        
        collab = lambda a : True if len(a) > 1 else False

        # All user playlists are obtained
        playlists = self._sp.user_playlists(user)
        while playlists:
            # For each playlist, all the songs will be taken to obtain the information of each one of them.
            for i, playlist in enumerate(playlists['items']):
                print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))  
                tracks = self._sp.playlist_tracks(playlists["items"][i]["id"])
                for i, track in enumerate(tracks['items']):
                    id_track = track["track"]["id"]
                    track = self._sp.track(track["track"]["id"])
                    collabs = collab(track["artists"])
                    album = self._sp.album(track["album"]["uri"])
                    release_date = track["album"]["release_date"]
                    popularity_song = track['popularity']
                    artist_info = self._sp.artist(track["album"]['artists'][0]["uri"])
                    track_feat= self._sp.audio_features (id_track)
                    
                    # We remove those words in parentheses. Since they cause problems in search in Genius
                    title_ge = re.sub(r'\([^)]*\)', '', track["name"])
                    # Due to the excess of requests made, in case of denial of the request, we waited long enough to request it
                    # again.
                    try:
                        song = self._genius.search_song(title_ge,artist=track["artists"][0]["name"])
                    except:
                        time.sleep(5*60)
                        song = self._genius.search_song(title_ge,artist=track["artists"][0]["name"])
                        
                    if not song:
                    # If we can't find the song, it may be that the search contains "*" characters. Genius does not usually
                    # contain the ones in the name songs or name artist, but the explicit word appears. We eliminate the
                    # word, since the search will give correct, with the other information.
                        artist_ge = re.sub(r'\w*[*]\w*', '', track["artists"][0]["name"])
                        title_ge = re.sub(r'\w*[*]\w*', '', title_ge)
                        song = self._genius.search_song(title_ge,artist=artist_ge)
                        if song:
                            lyric = song.lyrics
                        else:
                            # Certain main artists can be difficult to find in genius because of how they appear on
                            # billboard, so we are left with the first word of the artist in case the previous searches
                            # have not worked.
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
                    
                    print ("Added song:", track["name"], "Artist:", track["artists"][0]["name"])
            
            if playlists['next']:
                playlists = self._sp.next(playlists)
            else:
                playlists = None
        return df
    def Get_Lyrics (self, df):
        """ function that given a dataframe with songs previously generated with Get_User_Playlist_Data,
        adds the lyrics of the songs to each one of them.
        Arguments:
            df {[pd.DataFrame]} -- Dataframe previously generated with the function Get_User_Playlist_Data.
        Returns:
             [pd.DataFrame] -- Dataframe with added song lyrics.
        """
        df_lyrics = pd.DataFrame.copy(df)
        df_lyrics.assign(lyric=None)

        for i, item in df.iterrows():
            # We remove those words in parentheses. Since they cause problems in search in Genius
            title_ge = re.sub(r'\([^)]*\)', '', item["title"])
            # Due to the excess of requests made, in case of denial of the request, we waited long enough to request it
            # again.
            try:
                song = self._genius.search_song(title_ge,artist=item["artist"])
            except:
                time.sleep(5*60)
                song = self._genius.search_song(title_ge,artist=item["artist"])

            if not song:
            # If we can't find the song, it may be that the search contains "*" characters. Genius does not usually
            # contain the ones in the name songs or name artist, but the explicit word appears. We eliminate the
            # word, since the search will give correct, with the other information.
                artist_ge = re.sub(r'\w*[*]\w*', '', item["artist"])
                title_ge = re.sub(r'\w*[*]\w*', '', title_ge)
                song = self._genius.search_song(title_ge,artist=artist_ge)
                if song:
                    lyric = song.lyrics
                else:
                # Certain main artists can be difficult to find in genius because of how they appear on
                # billboard, so we are left with the first word of the artist in case the previous searches
                # have not worked.
                    artist_ge = artist_ge.split (" ")[0]
                    song = self._genius.search_song(title_ge,artist=artist_ge)
                    if song:
                        lyric = song.lyrics
                    else:
                        lyric = np.nan
            else:
                lyric = song.lyrics

            if song:
                print ("Added lyric:", item["title"],"Artist:",item["artist"])
            else:
                print ("\033[0;00;41mNot found lyric:", item["title"],"Artist:",item["artist"],"\033[0;00;00m")
            df_lyrics.loc[i,"song_lyrics"]=lyric
        return df_lyrics