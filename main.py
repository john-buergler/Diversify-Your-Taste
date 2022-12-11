from BuildData import buildUser, genre
from Model import cosSimAVGModel

if __name__ == '__main__':
    buildUser.get_top_song_features('1d6352ee10744e4ab561e5e8939638a6',
                                    'ef24ee95968f45db88c25e8116efe83f',
                                    'http://localhost:8080/callback')

    buildUser.user_saved_tracks('1d6352ee10744e4ab561e5e8939638a6',
                                'ef24ee95968f45db88c25e8116efe83f',
                                'http://localhost:8080/callback')

    genre.get_subgenres('UserData/user_tracks.csv',
                        '1d6352ee10744e4ab561e5e8939638a6',
                        'ef24ee95968f45db88c25e8116efe83f')

    cosSimAVGModel.cos_sim_top_40('SpotifyFeatures.csv',
                                  '1d6352ee10744e4ab561e5e8939638a6',
                                  'ef24ee95968f45db88c25e8116efe83f')
