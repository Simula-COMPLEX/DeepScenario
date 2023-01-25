#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

# See PLC_SN_15.py for a commented script

import time
import logging
from environs import Env
import lgsvl

FORMAT = "[%(levelname)6s] [%(name)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
log = logging.getLogger(__name__)

env = Env()

MAX_SPEED = 15.556  # (56 km/h, 35mph)
SPEED_VARIANCE = 4
TIME_LIMIT = 15   # seconds

LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
LGSVL__AUTOPILOT_0_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)

print("PLC_B_35 - ", end='')

sim = lgsvl.Simulator(LGSVL__SIMULATOR_HOST, LGSVL__SIMULATOR_PORT)
scene_name = env.str("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_straight2lanesame)
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name)

# spawn EGO in the 2nd to right lane
egoState = lgsvl.AgentState()
# A point close to the desired lane was found in Editor.
# This method returns the position and orientation of the closest lane to the point.
egoState.transform = sim.map_point_on_lane(lgsvl.Vector(3.68, 0, -50))
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5_full_analysis), lgsvl.AgentType.EGO, egoState)
forward = lgsvl.utils.transform_to_forward(egoState.transform)
right = lgsvl.utils.transform_to_right(egoState.transform)

ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__AUTOPILOT_0_PORT)

dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__AUTOPILOT_0_HOST)
dv.set_hd_map(env.str("LGSVL__AUTOPILOT_HD_MAP", 'Straight2LaneSame'))
dv.set_vehicle(env.str("LGSVL__AUTOPILOT_0_VEHICLE_CONFIG", 'Lincoln2017MKZ'))
try:
    modules = env.list("LGSVL__AUTOPILOT_0_VEHICLE_MODULES", subcast=str)
    if len(modules) == 0:
        log.warning("LGSVL__AUTOPILOT_0_VEHICLE_MODULES is empty, using default list: {0}".format(modules))
        modules = [
            'Recorder',
            'Localization',
            'Perception',
            'Transform',
            'Routing',
            'Prediction',
            'Planning',
            'Traffic Light',
            'Control'
        ]
except Exception:
    modules = [
        'Recorder',
        'Localization',
        'Perception',
        'Transform',
        'Routing',
        'Prediction',
        'Planning',
        'Traffic Light',
        'Control'
    ]
    log.warning("LGSVL__AUTOPILOT_0_VEHICLE_MODULES is not set, using default list: {0}".format(modules))

destination = egoState.position + 120 * forward + 3.6 * right
dv.setup_apollo(destination.x, destination.z, modules)


def on_collision(agent1, agent2, contact):
    raise lgsvl.evaluator.TestException("Ego collided with {}".format(agent2))


ego.on_collision(on_collision)

try:
    t0 = time.time()
    while True:
        egoCurrentState = ego.state
        if egoCurrentState.speed > MAX_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "Ego speed exceeded limit, {} > {} m/s".format(egoCurrentState.speed, MAX_SPEED + SPEED_VARIANCE)
            )
        sim.run(0.5)
        if time.time() - t0 > TIME_LIMIT:
            break
except lgsvl.evaluator.TestException as e:
    exit("FAILED: {}".format(e))

finalEgoState = ego.state
try:
    if lgsvl.evaluator.right_lane_check(sim, finalEgoState.transform):
        print("PASSED")
    else:
        raise lgsvl.evaluator.TestException("Ego did not change lanes")
except lgsvl.evaluator.TestException as e:
    exit("FAILED: {}".format(e))
