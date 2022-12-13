import numpy as np
import spotipy
from numpy import dot
from numpy.linalg import norm
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from spotipy import SpotifyClientCredentials
from Models import helpers


def cos_sim_top_40(csv, client_id, client_secret):
    csv_data = csv
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

    cos_sim_score = []

    projected_v = helpers.build_top_vector(tempo=True)

    for id in vector_dict:
        track = vector_dict[id]
        cos_sim_score.append(dot(projected_v, track) / (norm(projected_v) * norm(track)))

    cos_sim_score = pd.Series(cos_sim_score)

    client_cred_manager = SpotifyClientCredentials(client_id=client_id,
                                                   client_secret=client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_cred_manager)

    audio_feat['cos_sim_score'] = cos_sim_score

    audio_feat = audio_feat.sort_values(by=['cos_sim_score'], ascending=False)

    top40 = audio_feat.head(n=40)

    tracks = []

    for idx, track in top40.iterrows():
        urn = 'spotify:track:' + track['track_id']
        track_data = sp.track(urn)
        tracks.append(track_data['name'] + ' by ' + track_data['artists'][0]['name'])

    print(tracks)
