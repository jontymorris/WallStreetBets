import requests


def save_comments():
    ''' Saves the last 500 WallStreetBets comments '''

    response = requests.get('https://api.pushshift.io/reddit/search/comment/?subreddit=wallstreetbets&suze=500')

    with open('data/comments.json', 'w') as handle:
        handle.write(str(response.content, 'utf-8'))
    
    print('> Saved latest WSB comments')


if __name__ == '__main__':
    save_comments()
