import matplotlib.pyplot as plot
import datetime
import quandl, math
import numpy as np
import pandas
from sklearn import preprocessing, model_selection, svm
from sklearn.linear_model import LinearRegression
from matplotlib import style

# Get the stock data from Quandl API
def getStock(ticker):
	dataFrame = quandl.get(f"WIKI/{ticker}")

	dataFrame = dataFrame[['Open',  'High',  'Low',  'Close', 'Volume']]
	
	# Calculate the High Low Percent
	dataFrame['HL%'] = (dataFrame['High'] - dataFrame['Low']) / dataFrame['Close'] * 100.0
	
	# Calculate the percent change over the day
	dataFrame[r'% Change'] = (dataFrame['Close'] - dataFrame['Open']) / dataFrame['Open'] * 100.0
	dataFrame = dataFrame[['Close', 'HL%', r'% Change', 'Volume']]
	
	return dataFrame

# Generate a raw forecast of the data in the specified column
def genRawForecast(dataFrame, column, percent):

	forecast_col = column
	dataFrame.fillna(value=-99999, inplace=True)
	forecast_len = int(math.ceil(percent/100 * len(dataFrame)))
	dataFrame['label'] = dataFrame[forecast_col].shift(-forecast_len)

	return dataFrame, forecast_len

# Splits up dataframe and isolates the forecast
def splitDF(dataFrame, forecast_len):

	X = np.array(dataFrame.drop(['label'], 1))
	X = preprocessing.scale(X)
	Xpost = X[-forecast_len:]
	X = X[:-forecast_len]
	dataFrame.dropna(inplace=True)
	y = np.array(dataFrame['label'])

	return X, Xpost, y, dataFrame

# Performs the regression to formulate a forecast.
def performRegression(X, Xpost, y, dataFrame):
	X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2)
	clf = LinearRegression(n_jobs=-1)
	clf.fit(X_train, y_train)
	confidence = clf.score(X_test, y_test)
	forecastSet = clf.predict(Xpost)

	dataFrame['Forecast'] = np.nan

	return dataFrame, forecastSet, round(100*confidence,2)


# Handle the timing of the dataframe
def manageTime(dataFrame, forecastSet):
	finalday = dataFrame.iloc[-1].name
	lastU = finalday.timestamp()
	dayLength = 86400
	nextU = lastU + dayLength

	for i in forecastSet:
	    nextday = datetime.datetime.fromtimestamp(nextU)
	    nextU += 86400
	    dataFrame.loc[nextday] = [np.nan for _ in range(len(dataFrame.columns)-1)]+[i]

	
	return dataFrame


# Displays the graph of the prediction
def displayPrediction(dataFrame):
	dataFrame['Close'].plot()
	dataFrame['Forecast'].plot()
	plot.legend(loc=4)
	plot.xlabel('Date'); plot.ylabel('Price')
	plot.show()

# Function to figure out max potential profit given closing prices.
def maxPossibleProfit(data,shareCount=1):
    prices = list(data)

    maxProfit = 0

    for i in range(len(prices)-1):
        if prices[i] < prices[i+1]:
            maxProfit += prices[i+1] - prices[i]

    return round(shareCount*maxProfit, 2)


def main():
	# Set the API key
	quandl.ApiConfig.api_key = "AwrSw2Tnoo2wqtHjfHss"

	# Specify the plot style
	style.use('ggplot')
	

	# Take input for stock
	ticker = str(input("Enter the stock ticker: "))

	# Get the raw stock data and clean it
	dataFrame = getStock(ticker)
	
	# Prepare the dataframe for forecasting to be made
	dataFrame, forecast_len = genRawForecast(dataFrame, 'Close', 1)
	
	# Perform the linear regression on the unpacked dataframe that was split up
	dataFrame, forecastSet, confidence = performRegression(*splitDF(dataFrame, forecast_len))

	# Set up the time interval for the data
	dataFrame = manageTime(dataFrame, forecastSet)

	maxProfit = maxPossibleProfit(dataFrame['Close'])

	print(f'The confidence of the {ticker.upper()} stock prediction is {confidence}%')
	print(f'The max possible profit/share assuming one transaction per day is: ${maxProfit}')
	trigger = int(input('Press 1 to display the graph: '))
	# plot the data
	if trigger: displayPrediction(dataFrame)


if __name__ == "__main__":
	main()