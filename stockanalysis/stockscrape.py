import requests
from bs4 import BeautifulSoup as BS
import pandas


class Stock:
    def __init__(self, ticker):
        self.name = ticker
        self.link = f'https://www.nasdaq.com/symbol/{ticker}/historical'

        self.response = requests.get(self.link, 'html.parser')
        self.soup = BS(self.response.content, 'html.parser')

    # Scrape a table from the website, removing any unnecessary white spaces.
    @property
    def raw_data(self):
        div = self.soup.find('div', id='historicalContainer')
        table = [data.text.strip() for data in div.findAll('td')]
        return [data for data in table if data]


    # Originally, I had self.raw_data in place of every 'A', but I found out that I could increase efficiency 
    # if I just stored the raw data in a variable.
    @property
    def clean_data(self):
        A = self.raw_data
        dates  = [A[i] if not i%6 else float(A[i].replace(',','')) for i in range(0, len(A))]
        # openP  = [float(A[i].replace(',','')) for i in range(1, len(A), 6)]
        # highP  = [float(A[i].replace(',','')) for i in range(2, len(A), 6)]
        # lowP   = [float(A[i].replace(',','')) for i in range(3, len(A), 6)]
        # closeP = [float(A[i].replace(',','')) for i in range(4, len(A), 6)]
        # vol    = [float(A[i].replace(',','')) for i in range(5, len(A), 6)]
        return dates

def newStock(ticker, filename):
    if not isinstance(ticker, str): 
        raise Exception('Error, ticker must be a string.')

    stock = Stock(ticker)

    # Wanted to try manually writing data to a csv file for a challenge.
    with open(filename, 'w') as f:
        data = stock.clean_data
        f.write('Dates,Opens,Highs,Lows,Closes,Volumes')
        counter = 0
        for datum in data:
            if not counter % 6:
                f.write('\n' + str(datum + ','))
            else:
                 f.write(str(datum) + (',' if counter % 6 != 5 else ''))
            counter += 1

####### WHERE THE PANDAS ANALYSIS BEGINS ############

# This function generates a table for a stock.
def gen_table(ticker):
    filename = "stockdata.csv"
    stock = newStock(ticker, filename)
    data = pandas.read_csv(filename)
    return data

data = gen_table('aapl')


max_price = data['Highs'].max()