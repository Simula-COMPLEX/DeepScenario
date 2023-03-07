#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 07/03/2023 13:11
# @Author  : Chengjie
# @File    : preprocess.py
# @Software: PyCharm


import pandas as pd

strategies = ['greedy-strategy', 'random-strategy', 'rl_based-strategy']
rewards = ['reward-dto', 'reward-jerk', 'reward-ttc']
roads = ['road1', 'road2', 'road3', 'road4']
weathers = ['rain_day', 'rain_night', 'sunny_day', 'sunny_night']


def preprocess_ttc():
    for strategy in strategies:
        for reward in rewards:
            for road in roads:
                for weather in weathers:
                    f_n = './deepscenario-dataset/{}/{}/{}-{}-scenario-attributes.csv'.format(strategy, reward, road, weather)
                    print(f_n)
                    data = pd.read_csv(filepath_or_buffer=f_n, sep=',')

                    for i in range(len(data)):
                        if bool(data['Attribute[COL]'][i]) is True:

                            data['Attribute[TTC]'][i] = 0

                    data.to_csv(f_n, mode='w', header=True, index=False)

                    # return


preprocess_ttc()