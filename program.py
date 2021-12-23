import json, os, re, nltk
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
#from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')


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

    grammer = r'action: {<V.*><N.*>}'
    parser = nltk.RegexpParser(grammer)

    analyzer = SentimentIntensityAnalyzer()

    for comment in comments:
        print(analyzer.polarity_scores(comment['body']))

        
        #words = word_tokenize(comment['body'].lower())
        #pos_tokens = nltk.pos_tag(words)

        #parsed_text = parser.parse(pos_tokens)
        #chunks = [subtree for subtree in parsed_text.subtrees() if subtree.label() == 'action']

        #for chunk in chunks:
            #print(chunk)

def main():
    ensure_data_exists()

    stocks = load_stocks()
    comments = load_comments()

    comments2 = [
        {
            'body': 'I want to buy TSLA.'
        }
    ]

    comments = find_stock_comments(stocks, comments)

if __name__ == '__main__':
    main()
