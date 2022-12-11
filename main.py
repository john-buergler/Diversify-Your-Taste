from BuildData import buildUser, genre
from Model import cosSimAVGModel

if __name__ == '__main__':
    cli_id = 'ID'

    cli_secret = 'Secret'

    buildUser.get_top_song_features(cli_id,
                                    cli_secret,
                                    'http://localhost:8080/callback')

    buildUser.user_saved_tracks(cli_id,
                                cli_secret,
                                'http://localhost:8080/callback')

    genre.get_subgenres('UserData/user_tracks.csv',
                        cli_id,
                        cli_secret)

    cosSimAVGModel.cos_sim_top_40('SpotifyFeatures.csv',
                                  cli_id,
                                  cli_secret)
