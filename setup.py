import requests, json, tqdm, datetime, threading, queue, time

baseurl = 'https://api.pushshift.io/reddit/search/comment/?subreddit=wallstreetbets&size=100'

def get_start_of_day():
    ''' Gets a datetime object from the start of the day '''

    now = datetime.datetime.today()
    return datetime.datetime(now.year, now.month, now.day)

def format_download_url(day_offset, hour_offset):
    ''' Formats a download URL for the given day/hour offset '''

    now = get_start_of_day()
    offset = datetime.timedelta(days=-day_offset, hours=hour_offset)
    target = now + offset

    timestamp = int(datetime.datetime.timestamp(target))
    
    return baseurl + f'&before={timestamp}'

def get_urls_to_download(days_to_get):
    ''' Create a list of URLS to download '''

    urls = []

    for day in range(1, days_to_get):
        for hour in range(1, 24):
            urls.append(format_download_url(day, hour))
    
    return urls

class RedditWorker:
    ''' Downloads 1 day of data in a background thread '''

    def __init__(self, urls_queue, progress_bar):
        self.urls_queue = urls_queue
        self.progress_bar = progress_bar
        
        self.comments = []

        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        #self.run()
    
    def run(self):
        ''' Downloads the given urls '''

        try:
            url = self.urls_queue.get_nowait()

            while True:
                try:
                    # download the response
                    response = requests.get(url)
                    content = str(response.content, 'utf-8')
                    self.comments += json.loads(content)['data']

                    # progress to next url
                    self.progress_bar.update()
                    url = self.urls_queue.get_nowait()
                
                except json.decoder.JSONDecodeError:
                    # wait a bit and retry
                    time.sleep(2)
        
        except queue.Empty:
            # no more to download
            pass

def save_comments(days_to_get=180):
    ''' Saves comments from WallStreetBets '''

    print(f'> Downloading comments for past {days_to_get} days')

    # add the urls to download to the queue
    urls_queue = queue.Queue()
    for url in get_urls_to_download(days_to_get):
        urls_queue.put(url)

    # make a progress bar to keep track
    progress_bar = tqdm.tqdm(range(urls_queue.qsize()))

    # kick off the worker threads
    workers = []
    for _ in range(12):
        worker = RedditWorker(urls_queue, progress_bar)
        workers.append(worker)

    # collect comments as they finish
    comments = []
    for worker in workers:
        worker.thread.join()
        comments += worker.comments

    # now write comments to json file
    with open('data/comments.json', 'w') as handle:
        handle.write(json.dumps(comments, indent=4))

        progress_bar.close()
        print(f'> Saved {len(comments)} comments')

if __name__ == '__main__':
    save_comments(days_to_get=2)
