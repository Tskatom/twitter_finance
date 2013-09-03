countries <- c("Argentina", "Brazil", "Chile", "Colombia", "CostaRica", "Mexico", "Peru", "Panama", "Venezuela")
#countries <- c("Argentina")
country_index <- list()
country_index[["Argentina"]] = "MERVAL"
country_index[["Brazil"]] = "IBOV"
country_index[["Chile"]] = "CHILE65"
country_index[["Colombia"]] = "COLCAP"
country_index[["CostaRica"]] = "CRSMBCT"
country_index[["Mexico"]] = "MEXBOL"
country_index[["Panama"]] = "BVPSBVPS"
country_index[["Venezuela"]] = "IBVC"
country_index[["Peru"]] = "IGBVL"

gsr <- list()
gsr[["Argentina"]] <- c('2012-12-18', '2013-01-29', '2013-02-21', '2013-05-09', '2013-05-15')
gsr[["Brazil"]] <- c('2013-03-06', '2013-04-15')
gsr[["Chile"]] <- c('2013-02-20', '2013-03-06', '2013-04-15', '2013-06-20')
gsr[["Colombia"]] <- c('2013-04-15', '2013-05-31', '2013-06-28')
gsr[["Mexico"]] <- c('2013-02-13', '2013-04-15', '2013-06-20')
gsr[["Panama"]] <- c('2012-12-12', '2012-12-13', '2013-03-19', '2013-03-26', '2013-04-03', '2013-04-04', '2013-07-08', '2013-07-19', '2013-07-22')
gsr[["CostaRica"]] <- c('2013-01-09', '2013-01-14', '2013-01-15', '2013-02-01', '2013-02-04', '2013-02-07', '2013-02-12', '2013-02-13', '2013-03-19', '2013-03-27', '2013-04-09', '2013-04-16', '2013-06-06', '2013-06-07', '2013-06-12')
gsr[["Peru"]] <- c('2013-02-05', '2013-04-15', '2013-04-17', '2013-05-16', '2013-06-13', '2013-06-20')
gsr[["Venezuela"]] <- c('2012-12-07', '2012-12-12', '2013-05-14', '2013-06-10', '2013-06-17', '2013-06-26', '2013-06-27', '2013-06-28', '2013-07-17')


load_data <- function(country)
{
  price_file <- paste("/media/datastorage/correlation/price_",country,".csv",sep="")
  feature_file <- paste("/media/datastorage/correlation/feature_",country,".csv",sep="")
  price <- read.csv(price_file, header=TRUE)
  feature <- read.csv(feature_file, header=TRUE)
  return (list(price, feature))
}

plot_series <- function(country)
{
  info <- load_data(country)
  price <- data.frame(info[1])
  features <- data.frame(info[2])
  #normalized
  min_price <- min(price$Return)
  max_price <- max(price$Return)
  norm_price <- (price$Return - min_price) / (max_price - min_price)
  gsr_date <- gsr[[country]]
  gsr_idx <- NULL
  for(d in gsr_date)
  {
    print(d)
    gsr_idx <- c(gsr_idx, which(price$date == d))
  }
  print (gsr_idx)
  for (col in names(features))
  {
    if (col != "date")
    {
      min_fea <- min(features[col])
      max_fea <- max(features[col])
      norm_fea <- data.matrix((features[col] - min_fea) / (max_fea - min_fea))
      plot(as.Date(price$date), norm_price, type="l", col="red", xlab="Date", ylab="", main=paste(country_index[country], "vs", col))
      lines(as.Date(price$date),norm_fea, type="l", col="black")
      points(as.Date(price$date)[gsr_idx],norm_price[gsr_idx], pch=19, col="red",)
      legend("topright",c("price", col), col=c("red","black"), lty=1,merge = TRUE)
    }
  }
}

plot_country <- function()
{
  for (country in countries)
  {
    par(mfrow=c(2,2))
    plot_series(country)
  }
}

plot_country()
