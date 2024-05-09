from AlgorithmImports import *
from datetime import timedelta

class MyOptionAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2022, 1, 1)  # Set Start Date
        self.SetEndDate(2022, 2, 1)    # Set End Date
        self.SetCash(100000)           # Set Strategy Cash
        
        option = self.AddOption("AAPL") # Subscribe to Apple options
        option.SetFilter(-2, 2, timedelta(0), timedelta(180)) # Filter options
        
    def OnData(self, slice):
        if not self.Portfolio.Invested:
            for option_chain in slice.OptionChains:
                for contract in option_chain.Value:
                    if contract.Right == OptionRight.Put: # Check if it's a put option
                        self.MarketOrder(contract.Symbol, 1) # Buy the put option
                        break

# Instantiate the algorithm
algo = MyOptionAlgorithm()
# Get historical data
historical_puts = algo.History(algo.Symbol("AAPL"), timedelta(days=30))
print(historical_puts.head())

