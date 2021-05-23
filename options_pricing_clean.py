import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statistics
import random 
import math

## black sholes might no apply here because we are not dealing with geometric brownian motion since
## there is economic incentive between europe and the US to maintain the exchange rate between a certain level,
## i.e 0.5 -2. Otherwise trade between these two nations/continents would be very negatively impacted
## Whilst this is clearly not the case with stocks or crypto currencies, where price can keep trending indefinetely,
## for example where the basic black scholes model is more applicable. 
data = pd.read_csv('EURUSD15.csv')

def diff(i):
    return round((data.iloc[i,5] - data.iloc[i,2])*10000,1)

list_diff = []
for i in range(0,len(data)):
    list_diff +=[round((data.iloc[i,5] - data.iloc[i,2])*10000,1)]

mean = statistics.mean(list_diff)
stdev = statistics.stdev(list_diff)

plt.hist(list_diff, bins= [-40 +i/2 for i in range(0,160)])
plt.title("mean: " + str(round(mean,3)) + ", standard deviation: " + str(round(stdev,3)))
plt.xlabel('size of real body of 15min candlesticks of EURUSD/pip')
plt.ylabel('frequency')
plt.show()

start_price = data.iloc[len(data)-1,5]

random_walk = [start_price]

def random_walk_generator(initial_price,steps):
    random_walk = [start_price]
    for i in range(0,steps):
        random_walk += [random_walk[-1] + random.choice(list_diff)/10000]
    return random_walk

for i in range(1,5):
    plt.plot(random_walk_generator(start_price,252*24*4))
plt.title("5 random walks for EURUSD from June 2019 until June 2020")
plt.show()


## style refers to whether the option is American or European call option, duration is given in working days, r is the
##risk free interest rate, andspread is given in pips. 
def price_option(style,initial_price,strike_price,duration,num_monte_carlo,money,r,spread):
    random_walks = []
    for i in range(0,num_monte_carlo):
        random_walks +=[random_walk_generator(initial_price,duration*96)] ## 96 is the number of 15min candlesticks in a day.
    if style == "European":
        end_prices = []
        pay_off = 0
        pay_off_discounted = []
        discount = math.exp((-duration/252)*(r/100))
        for i in range(0,num_monte_carlo):
            end_prices += [random_walks[i][-1]]
        for i in range(0,num_monte_carlo):
            pay_off = max(0,end_prices[i] - strike_price -(spread/10000))
            pay_off_discounted +=[pay_off*discount]
        value_of_option = (sum(pay_off_discounted)/num_monte_carlo)*money ##note that I assume each random walk path is equally likely
    elif style == "American":
## notice this is technically not a American call option since you can only exercise your option at the midpoint or at maturity.
## I.e the number of steps = 2. As num_steps gets large this will increasingly well model an American style call option, but due to
## the computational strain I have left thatfor now.
        pay_off = 0
        pay_off_discounted = []
        mid_discount = math.exp((-duration/(252*2))*(r/100))
        discount = math.exp((-duration/252)*(r/100))
        for i in range(0,num_monte_carlo):
            mid_pay_off = max(0,random_walks[i][duration*48] - strike_price -(spread/10000))
            mid_pay_off_discounted = mid_pay_off*mid_discount
            if mid_pay_off_discounted ==0:
                pay_off_discounted += [discount*max(0,random_walks[i][-1] - strike_price -(spread/10000))]
            elif mid_pay_off_discounted > 0:
                pay_off_discounted += [max(mid_pay_off*mid_discount,price_option("European",random_walks[i][duration*48],
                strike_price,int(duration/2),num_monte_carlo,1,r,spread))]
        value_of_option = (sum(pay_off_discounted)/num_monte_carlo)*money
    return (value_of_option)


##I need to make sure that in my model the price increases when one of the following occures: duration increases; strike price decreases, if spread decreases, if interest rate decreases;
##if its a american call option instead of a european call option. And also the variance of the price of the option estimated by the monte carlo simulation does
##indeed decrease as the number of monte carlo iterations increases. 
        


## price_option("European",start_price,1.125,20,100,100000,3,5)
