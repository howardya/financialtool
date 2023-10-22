import yfinance as yf

TICKERS = [
    '^GSPC', #S&P500
    '^TNX', # Treasury 10Y
    'CL=F', # Crude Oil
]

def get_general_market_data():
    latest_data_1d = yf.download(
        TICKERS,
        period='1d',
        interval='1m'
    )

    latest_data_1d = latest_data_1d.iloc[:, latest_data_1d.columns.get_level_values(0) == 'Adj Close']
    latest_data_1d.columns = latest_data_1d.columns.get_level_values(1)

    latest_level = latest_data_1d.ffill().tail(1).transpose().iloc[:,0]
    level_df = latest_level.loc[TICKERS].to_frame('Latest')

    level_df['1D'] = yf.download(
        TICKERS,
        period='2d',
        interval='1d'
    ).xs('Adj Close', level=0, axis=1)[TICKERS] .iloc[0, :2].values

    level_df['1W'] = yf.download(
        TICKERS,
        period='7d',
        interval='1d'
    ).iloc[1, :2].values

    level_df['1M'] = yf.download(
        TICKERS,
        period='1mo',
        interval='1d'
    ).iloc[0, :2].values

    level_df['3M'] = yf.download(
        TICKERS,
        period='3mo',
        interval='1d'
    ).iloc[0, :2].values


