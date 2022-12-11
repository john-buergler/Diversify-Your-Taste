import spotipy
from sklearn.preprocessing import MinMaxScaler
from spotipy import SpotifyOAuth, SpotifyClientCredentials
import pandas as pd
from pathlib import Path


def get_top_song_features(client_id, client_secret, redirect_uri):
    """Takes in the identification of the API user in order to generate the top tracks over the three ranges allowed,
    short, medium, and long. Then gathers the song features for each track into a separate dataframe for each range,
    stored in a list."""

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope='user-top-read'))

    ranges = ['short_term', 'medium_term', 'long_term']

    top_ids = []

    for sp_range in ranges:
        results = sp.current_user_top_tracks(time_range=sp_range, limit=50)

        term_ids = []

        for item in results['items']:
            term_ids.append(item['id'])

        top_ids.append(term_ids)

    client_cred_manager = SpotifyClientCredentials(client_id=client_id,
                                                   client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_cred_manager)
    sp.trace = False

    features = []

    for term in top_ids:
        features.append(sp.audio_features(term))

    df_short = pd.DataFrame()
    df_medium = pd.DataFrame()
    df_long = pd.DataFrame()

    for idx, term in enumerate(features):
        feature_removal = ['key', 'analysis_url', 'duration_ms', 'mode', 'track_href', 'type', 'uri',
                           'time_signature']
        df = pd.DataFrame()

        med_ids = []
        long_ids = []

        for idxt, track in enumerate(term):
            for remove in feature_removal:
                track.pop(remove)

            df = pd.concat([df, pd.DataFrame(data=track, index=[idxt])])

            if idx == 0:
                df_short = df
            if idx == 1:
                df_medium = df
                med_ids.append(track['id'])
            if idx == 2:
                df_long = df
                long_ids.append(track['id'])

    for idl in long_ids:
        s_boolm = df_medium.loc[:, 'id'] != idl
        s_bools = df_short.loc[:, 'id'] != idl
        df_medium = df_medium.loc[s_boolm, :]
        df_short = df_short.loc[s_bools, :]

    for idm in med_ids:
        s_bools = df_short.loc[:, 'id'] != idm
        df_short = df_short.loc[s_bools, :]

    user_track_features = [df_short, df_medium, df_long]

    scaler = MinMaxScaler()

    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence', 'tempo']

    norm_tracks = []

    for df in user_track_features:
        temp_data = [scaler.fit_transform(df[features])]
        new_df = pd.DataFrame(columns=features, data=temp_data[0])
        norm_tracks.append(new_df)

    norm_tracks[0].to_csv(Path('UserData/short.csv'))
    norm_tracks[1].to_csv(Path('UserData/med.csv'))
    norm_tracks[2].to_csv(Path('UserData/long.csv'))


def user_saved_tracks(client_id, client_secret, redirect_uri):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope='user-library-read'))

    offset = 0

    all_saved_tracks = []

    grab_50 = sp.current_user_saved_tracks(50, offset=offset)['items']

    while len(grab_50) == 50:
        for track in grab_50:
            all_saved_tracks.append(track['track']['id'])
        offset = offset + 50
        grab_50 = sp.current_user_saved_tracks(50, offset)['items']

    for track in grab_50:
        id = track['track']['id']
        all_saved_tracks.append(id)

    user_tracks_dict = {'id': all_saved_tracks}

    pd.DataFrame(user_tracks_dict).to_csv('UserData/user_tracks.csv')

    return all_saved_tracks
