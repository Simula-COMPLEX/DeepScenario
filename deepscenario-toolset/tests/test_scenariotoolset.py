#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/01/2023 20:26
# @Author  : Chengjie
# @File    : test_scenariotoolset.py
# @Software: PyCharm
import time
import unittest
import lgsvl
from environs import Env
import datetime


class TestScenarioToolset(unittest.TestCase):
    def test_get_entities(self):
        runner = lgsvl.scenariotoolset.ScenarioRunner()
        runner.load_scenario_file(scenario_filepath_or_buffer='../deepscenario-dataset/rl_based-strategy/reward-jerk/road4-rain_day-scenarios/5_scenario_10_npc_vehicle.deepscenario')
        print(runner.get_entities_info())

    def test_get_scene_by_timestep(self):
        runner = lgsvl.scenariotoolset.ScenarioRunner()
        # runner.load_scenario_file(scenario_filepath_or_buffer='../deepscenario-dataset/rl_based-strategy/reward-jerk/road4-rain_day-scenarios/5_scenario_10_npc_vehicle.deepscenario')
        runner.load_scenario_file(scenario_filepath_or_buffer='./save_path.deepscenario')

        print(runner.get_scene_by_timestep(timestep=2))

    def test_scenario_runner(self):
        runner = lgsvl.scenariotoolset.ScenarioRunner()
        runner.load_scenario_file(scenario_filepath_or_buffer='./deepscenario/overtake.deepscenario')
        runner.connect_simulator_ads(simulator_host='10.211.55.3', simulator_port=8181, bridge_port=9090)

        runner.run(mode=0)

    def test_scenario_collector(self):
        print("Python API Quickstart #10: NPC following the lane")
        env = Env()

        sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host),
                              env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
        if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
            sim.reset()
        else:
            sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

        spawns = sim.get_spawn()

        state = lgsvl.AgentState()
        state.transform = spawns[0]
        ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5),
                            lgsvl.AgentType.EGO, state)

        # ego.connect_bridge(env.str("LGSVL__AUTOPILOT_0_HOST", lgsvl.wise.SimulatorSettings.bridge_host),
        #                    env.int("LGSVL__AUTOPILOT_0_PORT", lgsvl.wise.SimulatorSettings.bridge_port))

        state = lgsvl.AgentState()

        forward = lgsvl.utils.transform_to_forward(spawns[0])
        right = lgsvl.utils.transform_to_right(spawns[0])

        # 10 meters ahead, on left lane
        state.transform.position = spawns[0].position + 10.0 * forward
        state.transform.rotation = spawns[0].rotation

        npc1 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

        state = lgsvl.AgentState()

        # 10 meters ahead, on right lane
        state.transform.position = spawns[0].position + 4.0 * right + 10.0 * forward
        state.transform.rotation = spawns[0].rotation

        npc2 = sim.add_agent("SUV", lgsvl.AgentType.NPC, state, lgsvl.Vector(1, 1, 0))

        # If the passed bool is False, then the NPC will not moved
        # The float passed is the maximum speed the NPC will drive
        # 11.1 m/s is ~40 km/h
        npc1.follow_closest_lane(True, 11.1)
        # 5.6 m/s is ~20 km/h
        npc2.follow_closest_lane(True, 5.6)

        controllables = sim.get_controllables("signal")
        control_policy = "green=3;loop"
        for con in controllables:
            # Control this traffic light with a new control policy
            con.control(control_policy)

        agents = sim.get_agents()
        sc_collector = lgsvl.scenariotoolset.ScenarioCollector(city_map='BorregasAve')  # BorregasAve, SanFrancisco
        sc_collector.initialize_story(agents, datatime=str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
                                      v_date=str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                                      timestamp=int(time.time()), weatherdataset="None")

        for i in range(20):
            sc_collector.create_story_by_timestamp(i + 1, agents, sim)
            sim.run(0.5)

        sc_collector.save_scenario(0.5, './deepscenario/npc-follow-the-lane.deepscenario')

