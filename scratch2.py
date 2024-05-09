from random import randint
import matplotlib.pyplot as plt

cash = 100
cash_over_time = [100]
for i in range(10000):
    positivetrade = randint(0,10)<=7 # 70% success ratio
    if positivetrade:
        cash+=0.1*cash
    else:
        cash-=0.1*cash
    cash_over_time.extend([cash])

plt.plot(cash_over_time)
plt.show()