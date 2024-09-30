from BuildData import buildUser
from api_ref import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

if __name__ == '__main__':
    buildUser.get_top_song_features('short_term', CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
