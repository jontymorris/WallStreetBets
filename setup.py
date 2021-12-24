import requests, json, tqdm


def save_comments(days_to_get=90):
    ''' Saves comments from WallStreetBets '''

    print(f'> Downloading comments for past {days_to_get} days')

    comments = []
    baseurl = 'https://api.pushshift.io/reddit/search/comment/?subreddit=wallstreetbets&size=100'

    # download the comments
    for i in tqdm.tqdm(range(0, days_to_get)):
        url = baseurl + f'&before={i}d'

        response = requests.get(url)
        content = str(response.content, 'utf-8')

        comments += json.loads(content)['data']

    # write comments to json file
    with open('data/comments.json', 'w') as handle:
        handle.write(json.dumps(comments, indent=4))
        print(f'> Saved {len(comments)} comments')

if __name__ == '__main__':
    save_comments()
