import json, os, re
from nltk.tokenize import word_tokenize
#from nltk.corpus import stopwords

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
        contents = json.loads(handle.read())
        return contents['data']

def find_stock_comments(stocks, comments):
    ''' Finds comments that mention a stock name '''
    
    #english_stopwords = stopwords.words('english')

    stock_comments = []

    for comment in comments:
        text = word_tokenize(comment['body'].lower())
        
        if any((word in stocks) for word in text):
            print('Found stock!')
            print(text)

def main():
    ensure_data_exists()

    stocks = load_stocks()
    comments = load_comments()

    comments = find_stock_comments(stocks, comments)

if __name__ == '__main__':
    main()
