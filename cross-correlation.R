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
load_data <- function(country)
{
  price_file <- paste("/media/datastorage/correlation/price_",country,".csv",sep="")
  feature_file <- paste("/media/datastorage/correlation/feature_",country,".csv",sep="")
  price <- read.csv(price_file, header=TRUE)
  feature <- read.csv(feature_file, header=TRUE)
  return (list(price, feature))
}

corr_analysis <- function(country, price, features)
{
  score <- NULL
  feas <- NULL
  for (f in names(features))
  {
    if(f != "date")
    {
      feas <- c(feas, f)
      score <- c(score, ccf(price$Return, features[f], ylab = "cross-correlation", main=paste(country_index[country],"/",f,sep="")))
    }
  }
  return (list(feas, score))
}

analysis_country <- function()
{
  for (country in countries)
  {
    par(mfrow=c(4,3))
    info <- load_data(country)
    price <- data.frame(info[1])
    features <- data.frame(info[2])
    results <- corr_analysis(country, price, features)
  }
}

analysis_country()
