import pandas_datareader as pdr

# Get a list of all symbols from a specific exchange
symbols = pdr.get_nasdaq_symbols()

# Print the first few symbols
print(symbols.head())
