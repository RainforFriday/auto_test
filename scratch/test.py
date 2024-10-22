import os
import sys
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def oldx(t_mins):
    p_hour = 8.0
    cx = t_mins/60.0
    if cx < 0.5:
        px = 0
    else:
        px = math.ceil(cx)
    price = px*p_hour
    return price


def newx(t_mins):
    p_quar = 2.0
    cx = t_mins/15.0
    if cx < 2.0:
        px = 0
    else:
        px = math.ceil(cx)
    price = px*p_quar
    return price


def check_sum(l_t_mins):
    sum_old = 0
    sum_new = 0
    for t_mins in l_t_mins:
        # t_mins = random.randint(0, 840)
        sum_old = sum_old + oldx(t_mins)
        sum_new = sum_new + newx(t_mins)
    print("sum_old = {}".format(sum_old))
    print("sum_new = {}".format(sum_new))
    print("sum_new/sum_old = {}".format(sum_new/sum_old))


def checkx(t_mins):
    print("old price: {}".format(oldx(t_mins)))
    print("new price: {}".format(newx(t_mins)))


def pltx():
    lam = 2
    data_poisson = np.random.poisson(lam=lam, size=1000)
    mu = lam
    sigma = np.sqrt(lam)
    data_normal = np.random.normal(loc=mu, scale=sigma, size=1000)
    sns.histplot(data_poisson, label="Poisson")
    sns.histplot(data_normal, label="Normal")
    plt.legend()
    plt.show()


def plty():
    data = np.random.poisson(lam=3, size=10000)
    sns.histplot(data)
    plt.show()


if __name__ == "__main__":
    plty()
    #checkx(119)
    #print(numpy.random.poisson(65, 10000).mean())

