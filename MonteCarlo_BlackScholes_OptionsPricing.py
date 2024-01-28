import numpy as np

class OptionPricing:

    def __init__(self, S0, E, T, rf, sigma, iterations):
        self.S0 = S0 # current stock price
        self.E = E # strike price
        self.T = T # number of days from current stock price
        self.rf = rf # risk-free rate
        self.sigma = sigma # standard deviation of stock price
        self.iterations = iterations # monte carlo iterations

    def call_option_simulation(self):
        # 2 columns: first with 0s, second with the payoff

        option_data = np.zeros([self.iterations, 2])

        # Wiener process?
        rand = np.random.normal(0, 1, [1, self.iterations])

        # equation for stock price S(t) at T
        stock_price = self.S0 * np.exp(self.T * (self.rf - 0.5*self.sigma**2)
                                       + self.sigma * np.sqrt(self.T) * rand)

        # we need S-E because we need to calculate max(S-E,0)
        option_data[:, 1] = stock_price - self.E

        # now need to average the Monte Carlo simulation
        average = np.sum(np.amax(option_data, axis=1))/float(self.iterations)

        # now have to use the exp(-rT) discount factor to decay future payout
        return np.exp(-1.0*self.rf*self.T)*average


    def put_option_simulation(self):
        # 2 columns: first with 0s, second with the payoff

        option_data = np.zeros([self.iterations, 2])

        # Wiener process?
        rand = np.random.normal(0, 1, [1, self.iterations])

        # equation for stock price S(t) at T
        stock_price = self.S0 * np.exp(self.T * (self.rf - 0.5*self.sigma**2)
                                       + self.sigma * np.sqrt(self.T) * rand)

        # we need E-S because we need to calculate max(E-S,0)
        option_data[:, 1] = self.E - stock_price

        # now need to average the Monte Carlo simulation
        average = np.sum(np.amax(option_data, axis=1))/float(self.iterations)

        # now have to use the exp(-rT) discount factor to decay future payout
        return np.exp(-1.0*self.rf*self.T)*average


if __name__ == '__main__':
    model = OptionPricing(100, 100, 1, 0.05, 0.2, iterations=10000)
    print("Call option price is: £%s"%(str(np.round(model.call_option_simulation(),2))))
    print("Put option price is: £%s"%(str(np.round(model.put_option_simulation(),2))))
