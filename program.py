import json, os, re, nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime
from matplotlib import pyplot
from itertools import groupby


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')
nltk.download('stopwords')

stopwords = nltk.corpus.stopwords.words('english')
analyzer = SentimentIntensityAnalyzer()

class StockToken:
    ''' Helper struct for storing token info '''

    def __init__(self, stock, text, sentiment, date):
        self.stock = stock
        self.text = text
        self.sentiment = sentiment
        self.date = datetime.fromtimestamp(date).date()

def ensure_data_exists():
    ''' Ensures the data directory exists '''

    if not os.path.exists('data'):
        print('Error: Data directory is missing.')
        print('\tThis is required for the program to run.')

        exit(-1)

def load_stocks():
    ''' Loads the Nasdaq listed stocks '''

    with open('data/nasdaqlisted.txt') as handle:
        lines = handle.read().strip().split('\n')

        stocks = {}

        for line in lines[1:]:
            parts = line.split('|')

            # clean the name and symbol
            stock_symbol = parts[0].lower()
            stock_name = re.split(r'\,|( -)', parts[1])[0]
            stock_name = stock_name.replace('.', '').lower()

            # map name and symbol to symbol
            stocks[stock_symbol] = stock_symbol
            stocks[stock_name] = stock_symbol
        
        return stocks

def load_comments():
    ''' Loads the Reddit comments '''

    with open('data/comments.json') as handle:
        return json.loads(handle.read())

def get_relative_score(text):
    ''' Calculates a relative sentiment score betweeen 0 and 1 '''

    polarity = analyzer.polarity_scores(text)
    return polarity['pos'] + (polarity['neu'] * 0.5)

def get_tokens_from_comment(comment, stocks):
    ''' Find and tokenizes stocks in the comment '''

    try:
        sentences = nltk.sent_tokenize(comment['body'])

        for sentence in sentences:
            words = nltk.word_tokenize(sentence.lower())
            tags = nltk.pos_tag(words)

            for tag in tags:
                # must in stock list
                if not tag[0] in stocks:
                    continue

                # must not be a stopword
                if tag[0] in stopwords:
                    continue

                # must be used a noun
                if not re.match(r'N.*', tag[1]):
                    continue

                yield StockToken(
                    tag[0], sentence,
                    get_relative_score(sentence),
                    comment['created_utc'])
    except:
        return []

def find_stock_tokens(comments, stocks):
    ''' Find and tokenize comments that mention a stock '''

    tokens = []

    for comment in comments:
        for token in get_tokens_from_comment(comment, stocks):
            tokens.append(token)
    
    return tokens

def plot_daily_frequency(tokens):
    ''' Plots the daily frequency of each stock '''

    sorted_stocks = sorted(tokens, key=lambda x: x.stock)
    for stock, stock_tokens in groupby(sorted_stocks, lambda x: x.stock):
        days = []
        freq = []

        sorted_days = sorted(stock_tokens, key=lambda x: x.date)
        if len(sorted_days) < 5:
            continue

        for day, day_tokens in groupby(sorted_days, lambda x: x.date):
            days.append(day)
            freq.append(len(list(day_tokens)))

        pyplot.title(stock)
        pyplot.plot(days, freq)
        pyplot.show()

def main():
    # load the data
    ensure_data_exists()
    comments = load_comments()
    stocks = load_stocks()

    # tokenize the comments
    tokens = find_stock_tokens(comments, stocks)
    
    # now do some plotting
    plot_daily_frequency(tokens)

if __name__ == '__main__':
    main()
