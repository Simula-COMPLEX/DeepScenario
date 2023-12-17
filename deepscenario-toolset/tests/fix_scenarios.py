#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 07/08/2023 14:25
# @Author  : Chengjie
# @File    : fix_scenarios.py
# @Software: PyCharm
import os

import lgsvl

runner = lgsvl.scenariotoolset.ScenarioRunner()
for strategy in ['greedy-strategy', 'random-strategy', 'rl_based-strategy']:
    for reward in ['reward-dto', 'reward-jerk', 'reward-ttc']:
        for road in ['road1', 'road2', 'road3', 'road4']:
            for weather in ['rain_day', 'rain_night', 'sunny_night', 'sunny_day']:
                filepath = '../deepscenario-dataset/{}/{}/{}-{}-scenarios'.format(strategy, reward, road, weather)
                fileList = os.listdir(filepath)
                for f_n in fileList:
                    print(filepath + '/' + f_n)
                    runner.load_scenario_file(
                        scenario_filepath_or_buffer=filepath + '/' + f_n)
                    runner.reset_entities_names()
                    runner.reset_initialization_names()
                    runner.reset_actions()
                    fp = open(filepath + '/' + f_n, "w")
                    runner.doc.writexml(fp, encoding="utf-8")
                    fp.close()


# runner.load_scenario_file(
#     scenario_filepath_or_buffer='../deepscenario-dataset/rl_based-strategy/reward-jerk/road4-rain_day-scenarios/5_scenario_10_npc_vehicle.deepscenario')
#
# runner.reset_entities_names()
# runner.reset_initialization_names()
# runner.reset_actions()
#
# fp = open('./save_path.deepscenario', "w")
# runner.doc.writexml(fp, encoding="utf-8")
# fp.close()
