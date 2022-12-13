from math import floor

import pandas as pd
from numpy import dot
from numpy.linalg import norm
from sklearn.cluster import KMeans
from Models import helpers


def cluster_model(csv, e_factor):
    df_songs = pd.read_csv(csv)

    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence']

    x = df_songs.loc[:, features].values

    kmeans = KMeans(n_clusters=5)
    kmeans.fit(x)
    y = kmeans.predict(x)

    df_songs['cluster'] = y

    centroids = kmeans.cluster_centers_

    v_short = pd.read_csv('UserData/short.csv')[features].mean().values

    cent_cos_sim = {}

    projected_v = helpers.build_top_vector()

    for idx, cent in enumerate(centroids):
        cent_cos_sim[idx] = dot(projected_v, cent) / (norm(v_short) * norm(cent))

    fit_cent = max(cent_cos_sim, key=cent_cos_sim.get)

    s_bool = df_songs.loc[:, 'cluster'] == fit_cent
    df_songs = df_songs.loc[s_bool, :]

    return df_songs
