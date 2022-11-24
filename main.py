import json

import numpy as np
from numpy import dot
from numpy.linalg import norm
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from collections import defaultdict


def get_subgenres(csv, client_id, client_secret):
    """Takes in the csv file of the user's library and creates a count of the subgenres in the user's library"""

    client_cred_manager = SpotifyClientCredentials(client_id=client_id,
                                                   client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_cred_manager)

    song_lib = pd.read_csv(csv)

    genre_count_dict = defaultdict(int)

    for idx, song in song_lib.iterrows():
        song_urn = 'spotify:track:' + song['id']
        artist_urn = 'spotify:artist:' + sp.track(song_urn)['artists'][0]['uri']
        artist_genres = sp.artist(artist_urn)['genres']

        for genre in artist_genres:
            genre_count_dict[genre] += 1

    return genre_count_dict


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

    return [df_short, df_medium, df_long]


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

    return all_saved_tracks


def build_library_cluster(csv):
    csv_data = pd.read_csv(csv)
    """
    s_bool = csv_data.loc[:, 'country'] == 'US'

    csv_data = csv_data.loc[s_bool, :]

    print(csv_data)
    """
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence', 'tempo']
    with_id = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
               'valence', 'tempo', 'track_id', 'genre']

    audio_feat = csv_data[with_id]

    scaler = MinMaxScaler()

    temp_data = scaler.fit_transform(audio_feat[features])

    ids = audio_feat['track_id']

    vector_dict = {}

    for idx, id in enumerate(ids):
        vector_dict[id] = temp_data[idx]

    v_short = pd.read_csv('UserData/short.csv')[features].mean().values
    v_med = pd.read_csv('UserData/med.csv')[features].mean().values
    v_long = pd.read_csv('UserData/long.csv')[features].mean().values

    v_long_to_short = np.subtract(v_short, v_long)
    v_med_to_short = np.subtract(v_short, v_med)

    v_weighted_change = np.add(v_long_to_short, v_med_to_short) / 2

    projected_v = np.add(v_short, v_weighted_change)

    cos_sim_score = []

    for id in vector_dict:
        track = vector_dict[id]
        cos_sim_score.append(dot(projected_v, track) / (norm(projected_v) * norm(track)))

    cos_sim_score = pd.Series(cos_sim_score)

    audio_feat['cos_sim_score'] = cos_sim_score

    audio_feat = audio_feat.sort_values(by=['cos_sim_score'], ascending=False)

    return audio_feat


if __name__ == '__main__':
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence', 'tempo']

    """
    user_track_features = get_top_song_features([ID],
                                                [SECRET],
                                                'http://localhost:8080/callback')

    scaler = MinMaxScaler()

    norm_tracks = []

    for df in user_track_features:
        temp_data = [scaler.fit_transform(df[features])]
        new_df = pd.DataFrame(columns=features, data=temp_data[0])
        norm_tracks.append(new_df)

    norm_tracks[0].to_csv(Path('UserData/short.csv'))
    norm_tracks[1].to_csv(Path('UserData/med.csv'))
    norm_tracks[2].to_csv(Path('UserData/long.csv'))

    user_tracks = user_saved_tracks([ID],
                                                [SECRET],,
                                    'http://localhost:8080/callback')

    user_tracks_dict = {'id': user_tracks}

    pd.DataFrame(user_tracks_dict).to_csv('UserData/user_tracks.csv')
    """

    client_cred_manager = SpotifyClientCredentials(client_id='[ID]',
                                                   client_secret='[SECRET]')

    sp = spotipy.Spotify(client_credentials_manager=client_cred_manager)

    cos_sim = build_library_cluster('SpotifyFeatures.csv')

    s_bool = cos_sim.loc[:, 'genre'] == 'Alternative'
    top40 = cos_sim.loc[s_bool, :].head(n=40)

    tracks = []

    for idx, track in top40.iterrows():
        urn = 'spotify:track:' + track['track_id']
        track_data = sp.track(urn)
        tracks.append(track_data['name'] + ' by ' + track_data['artists'][0]['name'])

    print(tracks)

    # genres = get_subgenres('UserData/user_tracks.csv',
    #                        [ID],
    #                        [SECRET])
    #
    # with open('UserData/genre_count.json', 'w') as outfile:
    #     json.dump(genres, outfile)
    #
    # print(genres)
    # with open('UserData/genre_count.json') as json_file:
    #     genre_dict = json.load(json_file)
    #
    # del_list = []
    #
    # for genre in genre_dict.keys():
    #     if genre_dict[genre] <= 5:
    #         del_list.append(genre)
    #
    # for genre in del_list:
    #     del genre_dict[genre]
    #
    # print(genre_dict)

