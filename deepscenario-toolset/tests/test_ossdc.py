#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 15/06/2023 14:41
# @Author  : Chengjie
# @File    : test_ossdc.py
# @Software: PyCharm
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import socket
import time

from environs import Env

import lgsvl

#######################################################################################
#####################    SVL Simulator Environment    #################################
#######################################################################################

# Create the environment variable
env = Env()

SIMULATOR_HOST = env.str("OSSDC__SIMULATOR_HOST", '10.211.55.3')
if SIMULATOR_HOST is None:
    print("Set env OSSDC__SIMULATOR_HOST")
    exit()

SIMULATOR_API_PORT = env.str("OSSDC__SIMULATOR_API_PORT", '8181')
if SIMULATOR_API_PORT is None:
    print("Set env OSSDC__SIMULATOR_API_PORT")
    exit()

SIMULATOR_BRIDGE_HOST_1 = env.str("OSSDC__SIMULATOR_BRIDGE_HOST_1", '192.168.1.35')
if SIMULATOR_BRIDGE_HOST_1 is None:
    print("Set env OSSDC__SIMULATOR_BRIDGE_HOST_1")

# SIMULATOR_BRIDGE_HOST_2 = env.str("OSSDC__SIMULATOR_BRIDGE_HOST_2", '192.168.1.35')
# if SIMULATOR_BRIDGE_HOST_2 is None:
#     print("Set env OSSDC__SIMULATOR_BRIDGE_HOST_2")

SIMULATOR_BRIDGE_PORT_1 = env.str("OSSDC__SIMULATOR_BRIDGE_PORT_1", "9090")
if SIMULATOR_BRIDGE_PORT_1 is None:
    print("Set env OSSDC__SIMULATOR_BRIDGE_PORT_1")

# SIMULATOR_BRIDGE_PORT_2 = env.str("OSSDC__SIMULATOR_BRIDGE_PORT_2", "9091")
# if SIMULATOR_BRIDGE_PORT_2 is None:
#     print("Set env OSSDC__SIMULATOR_BRIDGE_PORT_2")

# Create the sim instance and connect to the SVL Simulator
sim = lgsvl.Simulator(SIMULATOR_HOST, int(SIMULATOR_API_PORT))
# map_uuid = "781b04c8-43b4-431e-af55-1ae2b2efc873" # RedBull
# map_uuid = "a3be7bf6-b5a6-4e48-833d-a1f1dd6d7a1e" #LVMS
# map_uuid = "431292c2-f6f6-4f5a-ae62-0964f6018d20" #Highway101GLE
map_uuid = "aae03d2a-b7ca-4a88-9e41-9035287a12cc"  # BorregasAve

if sim.current_scene == map_uuid:
    sim.reset()
else:
    sim.load(map_uuid)

spawns = sim.get_spawn()

# Load the EGO vehicle and spawn it on the track
state = lgsvl.AgentState()
state.transform = spawns[0]

sensorsConfig = "5ab8175f-e1f1-427c-a86e-e882fa842977"  # AWFLexus2016RXHybrid b22952f6-f82b-4eeb-ac28-2067e88569a1 - Autoware.Auto

ego = sim.add_agent(name=sensorsConfig, agent_type=lgsvl.AgentType.EGO, state=state)

if SIMULATOR_BRIDGE_HOST_1 is not None:
    ego.connect_bridge(SIMULATOR_BRIDGE_HOST_1, int(SIMULATOR_BRIDGE_PORT_1))  # connect to LGSVL bridge
    print("EGO1 Waiting for connection to ROS2 bridge ...")
    while not ego.bridge_connected:
        time.sleep(1)

# # Load an NPC and spawn it on the track
# ego2 = sim.add_agent(name = sensorsConfig, agent_type =lgsvl.AgentType.EGO, state = None)

# if SIMULATOR_BRIDGE_HOST_2 is not None:
#     ego2.connect_bridge(SIMULATOR_BRIDGE_HOST_2, int(SIMULATOR_BRIDGE_PORT_2)) #connect to LGSVL bridge
#     print("EGO2 Waiting for connection to ROS2 bridge ...")
#     while not ego2.bridge_connected:
#         time.sleep(1)


# Set a new daytime for the simulator, Time of day can be set from 0 ... 24
print("Current time:", sim.time_of_day)
sim.set_time_of_day(18)
print(sim.time_of_day)

# The simulator can be run for a set amount of time.
# time_limit is optional and if omitted or set to 0, then the simulator will run indefinitely
# Create Steps for running the simulation step by step
step_time = 0.1
duration = 10000000

step_rate = int(1.0 / step_time)
steps = duration * step_rate
print("Stepping forward for {} steps of {}s per step".format(steps, step_time))

# # Initial Ego Position - needs to be special because of our coordinate system
# s = ego.state
# x=125.231+8;
# y=122.0;
# z=-138.280
# s.position.x = x    # equals original x in our raceline data
# s.rotation.y = y      # 270 =- original value from raceline heading, if statement for pi and -pi
# s.position.z = z    # equals original (-)y in our raceline data
# ego.state = s


# s2 = ego2.state
# x2=125.231;
# y2=122.0;
# z2=-138.280
# s2.position.x = x2    # equals original x in our raceline data
# s2.rotation.y = y2      # 270 =- original value from raceline heading, if statement for pi and -pi
# s2.position.z = z2    # equals original (-)y in our raceline data
# ego2.state = s2


# sim.run(0) #time_limit=step_time)

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_IP_ADDRESS = "192.168.1.243"
UDP_PORT_NO = 6789

simid = "ego1"
for i in range(steps):
    sim.run(time_limit=step_time)
    # Get the current Information from the vehicle State
    state = ego.state  # Create a state variable for the vehicle
    pos = state.position  # Get vehicle position: X,Y,Y
    # rot= state.rotation         # Get vehicle rotation/heading: X,Y,Y
    speed = state.speed  # Get vehicle speed: X,Y,Y

    # Make correct transformation for the usage with the F1TENTH coordination
    pp_vehicle_x = pos.x
    pp_vehicle_y = pos.z
    message = simid + "," + str(pp_vehicle_x) + "," + str(pp_vehicle_y) + "," + str(speed) + ";"
    clientSock.sendto(message.encode('utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))
