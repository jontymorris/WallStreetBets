import json, os, re, nltk, tqdm, multiprocessing, datetime
from nltk.sentiment import SentimentIntensityAnalyzer
from matplotlib import pyplot
from itertools import groupby

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')

analyzer = SentimentIntensityAnalyzer()

symbols = {
    'spy',
    'gme',
    'tsla'
}

class StockToken:
    ''' Helper struct for storing token info '''

    def __init__(self, stock, text, sentiment, date):
        self.stock = stock
        self.text = text
        self.sentiment = sentiment
        self.date = datetime.datetime.fromtimestamp(date).date()

def ensure_data_exists():
    ''' Ensures the data directory exists '''

    if not os.path.exists('data'):
        print('Error: Data directory is missing.')
        print('\tThis is required for the program to run.')

        exit(-1)

def load_comments():
    ''' Loads the Reddit comments '''

    print('> Loading comments from json')

    with open('data/comments.json') as handle:
        return json.loads(handle.read())

def load_stock_history(symbol):
    ''' Loads the closing price for given stock '''

    history = []

    with open(f'data/{symbol}.csv') as handle:    
        lines = handle.read().split('\n')

        for line in lines[1:]:
            columns = line.split(',')
            
            if len(columns) < 5:
                continue

            date = datetime.date.fromisoformat(columns[0])
            close = float(columns[4])

            history.append([date, close])
    
    return history

def get_relative_score(text):
    ''' Calculates a relative sentiment score betweeen 0 and 1 '''

    polarity = analyzer.polarity_scores(text)
    return polarity['pos'] + (polarity['neu'] * 0.5)

def get_tokens_from_comment(comment):
    ''' Find and tokenizes stocks in the comment '''

    try:
        tokens = []
        sentences = nltk.sent_tokenize(comment['body'])

        for sentence in sentences:
            words = nltk.word_tokenize(sentence.lower())
            tags = nltk.pos_tag(words)

            for tag in tags:
                # must in stock list
                if not tag[0] in symbols:
                    continue

                # must be used a noun
                if not re.match(r'N.*', tag[1]):
                    continue

                token = StockToken(
                    tag[0], sentence,
                    get_relative_score(sentence),
                    comment['created_utc']
                )
                
                tokens.append(token)
        
        return tokens
    except:
        return []

def find_stock_tokens(comments):
    ''' Find and tokenize comments that mention a stock '''

    print('> Tokenizing the comments')

    tokens = []

    with multiprocessing.Pool() as pool:
        processes = pool.imap_unordered(get_tokens_from_comment, comments)

        for results in tqdm.tqdm(processes, total=len(comments)):
            tokens += results

    return tokens

def setup_pyplot(title):
    ''' Customizses pyplot for our graphs '''

    pyplot.title(title)
    fig = pyplot.gcf()
    fig.set_size_inches(18.5, 10.5)
    axs = pyplot.gca()
    axs.set_title(title)

def plot_relative_numbers(x_axis, y_axis, title, color):
    ''' Plots the numbers in a relative graph between 0 and 1 '''

    maximum = max(y_axis)
    y_axis = [num / maximum for num in y_axis]

    pyplot.plot(x_axis, y_axis, color=color, label=title)

def plot_stock_history(stock, dates):
    ''' Plots the stock history '''

    # load the stock history
    history = load_stock_history(stock)
    history_dates = [item[0] for item in history]
    history_closes = [item[1] for item in history]

    # fit to the oldest date
    for i in range(0, len(history)):
        if history_dates[i] >= dates[0]:
            history_dates = history_dates[i:]
            history_closes = history_closes[i:]
            break

    plot_relative_numbers(history_dates, history_closes, 'Relative Stock Price', 'b')

def plot_daily_frequency(tokens):
    ''' Plots the daily frequency of each stock '''

    sorted_stocks = sorted(tokens, key=lambda x: x.stock)
    for stock, stock_tokens in groupby(sorted_stocks, lambda x: x.stock):
        days = []
        freq = []

        # group tokens into days
        sorted_days = sorted(stock_tokens, key=lambda x: x.date)
        for day, day_tokens in groupby(sorted_days, lambda x: x.date):
            days.append(day)
            freq.append(len(list(day_tokens)))

        setup_pyplot(f'{stock.upper()} daily comments vs price')

        plot_stock_history(stock, days)
        plot_relative_numbers(days, freq, 'Relative Daily Comments', 'r')
        pyplot.legend(loc='best')
        pyplot.show()

def plot_daily_sentiment(tokens):
    ''' Plots the average daily sentiment of each stock '''

    sorted_stocks = sorted(tokens, key=lambda x: x.stock)
    for stock, stock_tokens in groupby(sorted_stocks, lambda x: x.stock):
        days = []
        sentiment = []

        # group tokens into days
        sorted_days = sorted(stock_tokens, key=lambda x: x.date)
        for day, day_tokens in groupby(sorted_days, lambda x: x.date):
            days.append(day)
            
            # average the days sentiment
            day_tokens = list(day_tokens)
            sentiment_sum = sum([token.sentiment for token in day_tokens])
            sentiment.append(sentiment_sum / len(day_tokens))

        setup_pyplot(f'{stock.upper()} daily sentiment vs price')

        plot_stock_history(stock, days)
        pyplot.plot(days, sentiment, label='Average Sentiment', color='r')
        pyplot.legend(loc='best')
        pyplot.show()

def main():
    # load the data
    ensure_data_exists()
    comments = load_comments()

    # tokenize the comments
    tokens = find_stock_tokens(comments)
    
    # now do some plotting
    plot_daily_frequency(tokens)
    plot_daily_sentiment(tokens)

if __name__ == '__main__':
    main()
