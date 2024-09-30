import spotipy
from sklearn.preprocessing import MinMaxScaler
from spotipy import SpotifyOAuth, SpotifyClientCredentials
import pandas as pd


def get_top_song_features(time_range, client_id, client_secret, redirect_uri):
    """Takes in the identification of the API user in order to generate the top tracks over the three ranges allowed,
    short, medium, and long. Then gathers the song features for each track into a separate dataframe for each range,
    stored in a list."""

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope='user-top-read'))

    top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=50)
    top_ids = []
    while top_tracks is not None:
        top_ids.append([i['id'] for i in top_tracks['items']])
        top_tracks = sp.next(top_tracks)

    client_cred_manager = SpotifyClientCredentials(client_id=client_id,
                                                   client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_cred_manager)
    sp.trace = False

    audio_features = []

    for batch in top_ids:
        audio_features.extend(sp.audio_features(batch))

    df_audio_features = pd.DataFrame(audio_features)

    scaler = MinMaxScaler()

    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
                'instrumentalness', 'liveness', 'valence', 'tempo']
    temp_data = [scaler.fit_transform(df_audio_features[features])]
    df_scaled = pd.DataFrame(columns=features, data=temp_data[0])
    return df_scaled


def user_saved_tracks(client_id, client_secret, redirect_uri):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope='user-library-read'))

    offset = 0

    all_saved_tracks = []

    saved_tracks = sp.current_user_saved_tracks(50, offset=offset)

    while saved_tracks is not None:
        all_saved_tracks.append([i['id'] for i in saved_tracks['items']])
        saved_tracks = sp.next(saved_tracks)

    user_tracks_dict = {'id': all_saved_tracks}

    pd.DataFrame(user_tracks_dict).to_csv('UserData/user_tracks.csv')

    return all_saved_tracks
