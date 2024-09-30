from BuildData import buildUser
import secrets

if __name__ == '__main__':
    buildUser.get_top_song_features('short_term', secrets.CLIENT_ID, secrets.CLIENT_SECRET, secrets.REDIRECT_URI)
