import spotipy
from spotipy import SpotifyClientCredentials
import pandas as pd
from collections import defaultdict
import json


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

    with open('UserData/genre_count.json', 'w') as outfile:
        json.dump(genre_count_dict, outfile)

    with open('UserData/genre_count.json') as json_file:
        genre_dict = json.load(json_file)

    del_list = []

    for genre in genre_dict.keys():
        if genre_dict[genre] <= 5:
            del_list.append(genre)

    for genre in del_list:
        del genre_dict[genre]

