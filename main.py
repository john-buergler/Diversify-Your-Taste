from BuildData import buildUser, genre
from Models import cosSimAVGModel, clusterModel

if __name__ == '__main__':
    cli_id = 'id'

    cli_secret = 'secret'

    # buildUser.get_top_song_features(cli_id,
    #                                 cli_secret,
    #                                 'http://localhost:8080/callback')
    #
    # buildUser.user_saved_tracks(cli_id,
    #                             cli_secret,
    #                             'http://localhost:8080/callback')
    #
    # genre.get_subgenres('UserData/user_tracks.csv',
    #                     cli_id,
    #                     cli_secret)

    df_cluster = clusterModel.cluster_model('SpotifyFeatures.csv', 0.5)

    cosSimAVGModel.cos_sim_top_40(df_cluster, cli_id, cli_secret)

