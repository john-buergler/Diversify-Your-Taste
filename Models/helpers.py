import numpy as np
import pandas as pd


def build_top_vector(tempo=False):
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence']

    if tempo:
        features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                    'valence', 'tempo']

    v_short = pd.read_csv('UserData/short.csv')[features].mean().values
    v_med = pd.read_csv('UserData/med.csv')[features].mean().values
    v_long = pd.read_csv('UserData/long.csv')[features].mean().values

    v_long_to_short = np.subtract(v_short, v_long)
    v_med_to_short = np.subtract(v_short, v_med)

    v_weighted_change = np.add(v_long_to_short, v_med_to_short) / 2

    projected_v = np.add(v_short, v_weighted_change)

    return projected_v
