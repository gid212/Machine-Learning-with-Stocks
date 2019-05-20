data <- read.csv(file='stockdata.csv', header=TRUE, sep=',', strip.white= TRUE)
# print(data)

vectorData <- as.vector(data)
# print(vectorData)

print(colnames(vectorData)[1])
a <- paste('1','.png',sep='')
print(a)

# Make sure it only pays attention to weekdays.
X <- seq( as.Date("2019/2/19", format="%Y/%m/%d"), as.Date("2019/5/17", format="%Y/%m/%d"),"days")
weekdays.X <- X[ ! weekdays(X) %in% c("Saturday", "Sunday") ]


# Loop through the columns, create a time series for each of them
i = 2
for (col in vectorData){
	datum.timeseries <- ts(vectorData[i], start=weekdays.X[1],end=weekdays.X[length(weekdays.X)])
	png(file = paste(colnames(vectorData)[i],'.png', sep=''))
	plot(datum.timeseries)
	i <- i + 1
}

