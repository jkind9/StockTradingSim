    
def a_grad(ticker, live_stats):
        
    """
    Determine buy, sell, or hold based on the latest price, moving average,
    gradient (first derivative), and second derivative.

    :param latest_price: The most recent stock price.
    :param moving_average: The current moving average of the stock price.
    :param gradient: The first derivative of the stock price.
    :param second_derivative: The second derivative of the stock price.
    :return: A string indicating 'buy', 'sell', or 'hold'.
    """

    # gradient of >0 meands a is increasing leading to spike in stock val
    # gradient <0 either means stock increase is slowing down or about to heavily decrease
    if live_stats[ticker]["a_grad"] <0.00025 or live_stats[ticker]["d2y"]<0.002:
        return "buy"
    elif live_stats[ticker]["a_grad"]>-0.00025:
        return "sell"

def grad(ticker, live_stats):
    if live_stats[ticker]["gradient"]>0.2:
        return "buy"
    if live_stats[ticker]["gradient"]<0.2:
        return "sell"

def options(predictedCallValue, callValue, predictedPutValue, putValue, threshold =0.9):
    # open, high, low, close, adj close, volume
    output_commands = []
    if callValue>=threshold*predictedCallValue:
        output_commands.extend(["buycall"])
    if putValue>=threshold*predictedPutValue:
        output_commands.extend(["buyput"])
    return output_commands

