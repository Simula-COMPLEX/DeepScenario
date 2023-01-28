#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/01/2023 16:05
# @Author  : Chengjie
# @File    : scenario_runner.py
# @Software: PyCharm
import datetime
import json
import time

from environs import Env
import sys
import xml.dom.minidom
import lgsvl


def set_color(color_v):
    color = lgsvl.Vector(0, 0, 0)
    if color_v == 'black':
        color = lgsvl.Vector(0, 0, 0)
    elif color_v == 'white':
        color = lgsvl.Vector(1, 1, 1)
    elif color_v == 'yellow':
        color = lgsvl.Vector(1, 1, 0)
    elif color_v == 'pink':
        color = lgsvl.Vector(1, 0, 1)
    elif color_v == 'skyblue':
        color = lgsvl.Vector(0, 1, 1)
    elif color_v == 'red':
        color = lgsvl.Vector(1, 0, 0)
    elif color_v == 'green':
        color = lgsvl.Vector(0, 1, 0)
    elif color_v == 'blue':
        color = lgsvl.Vector(0, 0, 1)
    return color


def on_collision(agent1, agent2, contact):
    name1 = agent1.__dict__.get('name')
    name2 = agent2.__dict__.get('name') if agent2 is not None else "OBSTACLE"
    print("{} collided with {} at {}".format(name1, name2, contact))
    try:
        sys.exit(1)
    except SystemExit:
        pass


class ScenarioRunner:
    def __init__(self):
        self.sim = None
        self.bridge_port = None
        self.bridge_host = None
        self.simulator_port = None
        self.simulator_host = None
        self.env = Env()

        self.scenario_file = None
        self.scenario = None
        self.entities_actions = None
        self.story_board = None
        self.entities_initialization = None
        self.entities = None
        self.operating_environment = None

        self.ads = 'Apollo'
        self.ads_version = 5.0
        self.enable_ads = False
        self.ads_connection_type = 'bridge'

    def load_scenario_file(self, scenario_filepath_or_buffer):
        self.scenario_file = scenario_filepath_or_buffer
        self.scenario = xml.dom.minidom.parse("./{}".format(self.scenario_file)).documentElement
        self.entities = self.scenario.getElementsByTagName('Entities')[0].getElementsByTagName('ScenarioObject')
        self.story_board = self.scenario.getElementsByTagName('StoryBoard')
        self.entities_initialization = self.story_board[0].getElementsByTagName('Initialization')[
            0].getElementsByTagName('ObjectInitialization')
        self.entities_actions = self.story_board[0].getElementsByTagName('Story')[0].getElementsByTagName(
            'ObjectAction')
        self.operating_environment = self.scenario.getElementsByTagName('Environment')[0]

    def connect_simulator_ads(self, simulator_host='127.0.0.1', simulator_port=8181, bridge_host='127.0.0.1', bridge_port=9090):
        self.simulator_host = lgsvl.wise.SimulatorSettings.simulator_host if simulator_host is None else simulator_host
        self.simulator_port = lgsvl.wise.SimulatorSettings.simulator_port if simulator_port is None else simulator_port
        self.bridge_host = lgsvl.wise.SimulatorSettings.bridge_host if bridge_host is None else bridge_host
        self.bridge_port = lgsvl.wise.SimulatorSettings.bridge_port if bridge_port is None else bridge_port
        self.sim = lgsvl.Simulator(self.env.str("LGSVL__SIMULATOR_HOST", self.simulator_host),
                                   self.env.int("LGSVL__SIMULATOR_PORT", self.simulator_port))

        hd_map = lgsvl.wise.DefaultAssets.map_sanfrancisco
        print(self.operating_environment.getElementsByTagName('HDMap')[0].getAttribute('city'))
        if self.operating_environment.getElementsByTagName('HDMap')[0].getAttribute('city') == 'SanFrancisco':
            hd_map = lgsvl.wise.DefaultAssets.map_sanfrancisco
        elif self.operating_environment.getElementsByTagName('HDMap')[0].getAttribute('city') == 'BorregasAve':
            hd_map = lgsvl.wise.DefaultAssets.map_borregasave

        if self.sim.current_scene == hd_map:
            self.sim.reset()
        else:
            self.sim.load(hd_map)

    def __get_entity_info(self, entity):
        """
        return attributes and initial states for a single entity
        """
        entity_dict = {}
        entity_dict.update({'model': "Sedan" if entity.getAttribute('name').__contains__('Ego')
        else entity.getAttribute('model'),
                            # 'name': entity.getAttribute('name'),
                            'color': entity.getElementsByTagName('ObjectParameter')[0].
                           getAttribute('ObjectColor'),
                            'type': entity.getElementsByTagName('ObjectParameter')[0].
                           getAttribute('ObjectType'),
                            'uid': entity.getAttribute('uid')})
        initialize = None
        for objectInitial in self.entities_initialization:
            if objectInitial.getAttribute('objectRef') == entity.getAttribute('name'):
                initialize = objectInitial
                break
        objectInitialPosition = initialize.getElementsByTagName('ObjectInitialPosition')
        objectInitialRotation = initialize.getElementsByTagName('ObjectInitialRotation')
        objectInitialVelocity = initialize.getElementsByTagName('ObjectInitialVelocity')
        objectInitialAngularVelocity = initialize.getElementsByTagName('ObjectInitialAngularVelocity')

        position = lgsvl.Vector(float(objectInitialPosition[0].getAttribute('positionX')),
                                float(objectInitialPosition[0].getAttribute('positionY')),
                                float(objectInitialPosition[0].getAttribute('positionZ')))
        rotation = lgsvl.Vector(float(objectInitialRotation[0].getAttribute('rotationX')),
                                float(objectInitialRotation[0].getAttribute('rotationY')),
                                float(objectInitialRotation[0].getAttribute('rotationZ')))
        velocity = lgsvl.Vector(float(objectInitialVelocity[0].getAttribute('velocityX')),
                                float(objectInitialVelocity[0].getAttribute('velocityY')),
                                float(objectInitialVelocity[0].getAttribute('velocityZ')))
        angular_velocity = lgsvl.Vector(float(objectInitialAngularVelocity[0].getAttribute('angularVelocityX')),
                                        float(objectInitialAngularVelocity[0].getAttribute('angularVelocityY')),
                                        float(objectInitialAngularVelocity[0].getAttribute('angularVelocityZ')))

        return entity_dict, position, rotation, velocity, angular_velocity

    def get_entities_info(self):
        """
        return attributes and initial states for all entities
        """
        entities_dict = {}
        for entity in self.entities:
            entity_dict, position, rotation, velocity, angular_velocity = self.__get_entity_info(entity)
            entity_dict.update({'initialization': {'position': {'x': position.x, 'y': position.y, 'z': position.z},
                                                   'rotation': {'x': rotation.x, 'y': rotation.y, 'z': rotation.z},
                                                   'velocity': {'x': velocity.x, 'y': velocity.y, 'z': velocity.z},
                                                   'angular_velocity': {'x': angular_velocity.x,
                                                                        'y': angular_velocity.y,
                                                                        'z': angular_velocity.z}}})
            entities_dict.update({entity.getAttribute('name'): entity_dict})
        return json.dumps(entities_dict, indent=4)

    def get_scene_by_timestep(self, timestep: int):
        """
        return a single scene in the scenario by timestep
        """
        scene_timestep = {}
        scene_timestep.update({'timestep': timestep})
        for objectAction in self.entities_actions:
            object_dict = {}
            objectRef = objectAction.getElementsByTagName('objectRef')[0].getAttribute('objectRef')
            wayPoints = objectAction.getElementsByTagName('WayPoint')
            # if len(wayPoints) < timestep:
            #     return
            try:
                wayPoint = wayPoints[timestep - 1]
            except IndexError as message:
                print(message, '([{}, {}])'.format(1, len(wayPoints)))
                # print('Maximum allowed: {}'.format(len(wayPoints)))
                return
            object_dict.update({'dynamic_parameters': {'speed': wayPoint.getElementsByTagName('DynamicParameters')[0].
                               getElementsByTagName('Speed')[0].getAttribute('speed'), 'velocity': {
                'x': wayPoint.getElementsByTagName('DynamicParameters')[0].
                               getElementsByTagName('Velocity')[0].getAttribute('velocityX'),
                'y': wayPoint.getElementsByTagName('DynamicParameters')[0].
                               getElementsByTagName('Velocity')[0].getAttribute('velocityY'),
                'z': wayPoint.getElementsByTagName('DynamicParameters')[0].
                               getElementsByTagName('Velocity')[0].getAttribute('velocityZ')}, 'angular_velocity': {
                'x': wayPoint.getElementsByTagName('DynamicParameters')[0].
                               getElementsByTagName('AngularVelocity')[0].getAttribute('angularVelocityX'),
                'y': wayPoint.getElementsByTagName('DynamicParameters')[0].
                               getElementsByTagName('AngularVelocity')[0].getAttribute('angularVelocityY'),
                'z': wayPoint.getElementsByTagName('DynamicParameters')[0].
                               getElementsByTagName('AngularVelocity')[0].getAttribute('angularVelocityZ')}},
                                'geographic_parameters': {'position': {
                                    'x': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectPosition')[0].getAttribute('positionX'),
                                    'y': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectPosition')[0].getAttribute('positionY'),
                                    'z': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectPosition')[0].getAttribute('positionZ')},
                                    'rotation': {
                                        'x': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectRotation')[0].getAttribute('rotationX'),
                                        'y': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectRotation')[0].getAttribute('rotationY'),
                                        'z': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectRotation')[0].getAttribute('rotationZ')},
                                    'gps': {
                                        'altitude': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectGPS')[0].getAttribute('altitude'),
                                        'easting': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectGPS')[0].getAttribute('easting'),
                                        'latitude': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectGPS')[0].getAttribute('latitude'),
                                        'longitude': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectGPS')[0].getAttribute('longitude'),
                                        'northing': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectGPS')[0].getAttribute('northing'),
                                        'orientation': wayPoint.getElementsByTagName('GeographicParameters')[0].
                               getElementsByTagName('ObjectGPS')[0].getAttribute('orientation'),
                                    }
                                }})

            scene_timestep.update({objectRef: object_dict})
        return json.dumps(scene_timestep, indent=4)

    def __get_time_stamp(self):
        timeofday = round(self.sim.time_of_day)
        if timeofday == 24:
            timeofday = 0
        dt = self.sim.current_datetime
        # print(dt)
        dt = dt.replace(hour=timeofday, minute=0, second=0)
        # print(int(time.mktime(dt.timetuple())))
        return json.dumps(int(time.mktime(dt.timetuple())))

    def run(self, mode=0):
        for scenarioObject in self.entities:
            entity_dict, position, rotation, velocity, angular_velocity = self.__get_entity_info(scenarioObject)
            state = lgsvl.AgentState()
            state.transform.position = position
            state.transform.rotation = rotation
            state.velocity = velocity
            state.angular_velocity = angular_velocity

            if entity_dict['type'] == 'Ego':
                ego = self.sim.add_agent(
                    self.env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5),
                    lgsvl.AgentType.EGO, state)
                ego.on_collision(on_collision)
                ego.old_uid = entity_dict['uid']
                scenarioObject.setAttribute('uid', ego.uid)
            elif entity_dict['type'] == 'NPC':
                npc = self.sim.add_agent(entity_dict['model'], lgsvl.AgentType.NPC, state,
                                         set_color(entity_dict['color']))
                # npc.on_collision(on_collision)
                npc.old_uid = entity_dict['uid']
                scenarioObject.setAttribute('uid', npc.uid)
            elif entity_dict['type'] == 'Pedestrian':
                p = self.sim.add_agent(entity_dict['model'], lgsvl.AgentType.PEDESTRIAN, state)
                p.old_uid = entity_dict['uid']
                scenarioObject.setAttribute('uid', p.uid)

        action_dict = {}

        for objectAction in self.entities_actions:
            objectRef = objectAction.getElementsByTagName('objectRef')[0].getAttribute('objectRef')
            objectUid = None
            for scenarioObject in self.entities:
                if scenarioObject.getAttribute('name') == objectRef:
                    objectUid = scenarioObject.getAttribute('uid')
                    break

            wayPoints = objectAction.getElementsByTagName('WayPoint')
            wp_list = []
            state_list = []
            for wayPoint in wayPoints:
                speed = float(
                    wayPoint.getElementsByTagName('DynamicParameters')[0].getElementsByTagName('Speed')[0].
                    getAttribute('speed'))

                coefficient = 1

                velocity = wayPoint.getElementsByTagName('DynamicParameters')[0].getElementsByTagName('Velocity')[0]
                velocity = lgsvl.Vector(float(velocity.getAttribute('velocityX')) * coefficient,
                                        float(velocity.getAttribute('velocityY')) * coefficient,
                                        float(velocity.getAttribute('velocityZ')) * coefficient)
                angular_velocity = \
                    wayPoint.getElementsByTagName('DynamicParameters')[0].getElementsByTagName('AngularVelocity')[0]
                angular_velocity = lgsvl.Vector(float(angular_velocity.getAttribute('angularVelocityX')),
                                                float(angular_velocity.getAttribute('angularVelocityY')),
                                                float(angular_velocity.getAttribute('angularVelocityZ')))

                position = \
                    wayPoint.getElementsByTagName('GeographicParameters')[0].getElementsByTagName('ObjectPosition')[
                        0]
                position = lgsvl.Vector(float(position.getAttribute('positionX')),
                                        float(position.getAttribute('positionY')),
                                        float(position.getAttribute('positionZ')))
                rotation = \
                    wayPoint.getElementsByTagName('GeographicParameters')[0].getElementsByTagName('ObjectRotation')[
                        0]
                rotation = lgsvl.Vector(float(rotation.getAttribute('rotationX')),
                                        float(rotation.getAttribute('rotationY')),
                                        float(rotation.getAttribute('rotationZ')))

                if objectRef.__contains__('Pedestrian'):
                    wp = lgsvl.WalkWaypoint(position, 0)
                else:
                    wp = lgsvl.DriveWaypoint(position, 12 if speed < 1 else speed, rotation)
                wp_list.append(wp)

                state = lgsvl.AgentState()
                state.transform.position = position
                state.transform.rotation = rotation
                state.velocity = velocity
                state.angular_velocity = angular_velocity
                state_list.append(state)

            action_dict.update({objectUid: {'objectRef': objectRef, 'wayPoints': wp_list, 'states': state_list}})

        controllables = self.sim.get_controllables("signal")
        control_policy = "green=3;loop"
        for con in controllables:
            # Control this traffic light with a new control policy
            con.control(control_policy)

        agents = self.sim.get_agents()

        timestep = float(self.scenario.getAttribute('timestep'))
        if self.enable_ads:
            print('connected')
            keys = action_dict.keys()
            for i in range(1, len(agents)):
                if agents[i].uid in keys:
                    agents[i].follow(action_dict[agents[i].uid]['wayPoints'])

            agents[0].connect_bridge(self.env.str("LGSVL__AUTOPILOT_0_HOST", str(self.bridge_host)),
                                     self.env.int("LGSVL__AUTOPILOT_0_PORT", self.bridge_port))

        env_init = self.operating_environment.getElementsByTagName('EnvironmentInitialization')[0]
        dt = datetime.datetime.strptime(env_init.getAttribute('dateTime'), "%Y-%m-%d %H:%M:%S")
        fix_time = bool(env_init.getAttribute('fixTime'))
        self.sim.set_date_time(datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second), fix_time)

        if mode == 1:
            print('connected to autonomous driving system (Apollo 5.0) successfully, running with Apollo...')
            self.sim.run(len(action_dict[agents[0].uid]['wayPoints']) * timestep)
        else:
            print('ADS is not enabled, replaying the scenario {}...'.format(self.scenario_file))

            keys = action_dict.keys()
            for i in range(1, len(agents)):
                if agents[i].uid in keys:
                    agents[i].follow(action_dict[agents[i].uid]['wayPoints'])

            for i in range(len(action_dict[agents[0].uid]['wayPoints'])):
                state = action_dict[agents[0].uid]['states'][i]
                agents[0].state = state
                self.sim.run(timestep)

    # def run_multiple_scenarios(self, fn):
    #     root = self.scenario.documentElement
    #
    #     entities = root.getElementsByTagName('Entities')
    #     scenarioObjects = entities[0].getElementsByTagName('ScenarioObject')
    #
    #     storyboard = root.getElementsByTagName('StoryBoard')
    #     initialization = storyboard[0].getElementsByTagName('Initialization')
    #     objectInitialization = initialization[0].getElementsByTagName('ObjectInitialization')
    #
    #     story = storyboard[0].getElementsByTagName('Story')
    #     objectActions = story[0].getElementsByTagName('ObjectAction')
    #
    #     for scenarioObject in scenarioObjects:
    #         objectParameter = scenarioObject.getElementsByTagName('ObjectParameter')[0]
    #
    #         object_model = scenarioObject.getAttribute('model')
    #         object_name = scenarioObject.getAttribute('name')
    #         object_uid = scenarioObject.getAttribute('uid')
    #         object_color = set_color(objectParameter.getAttribute('ObjectColor'))
    #         object_type = objectParameter.getAttribute('ObjectType')
    #
    #         create = True
    #         for agent in self.sim.get_agents():
    #             if agent.old_uid == object_uid:
    #                 # print(agent.uid, object_uid)
    #                 create = False
    #                 break
    #         if not create:
    #             continue
    #
    #         initialize = None
    #         for objectInitial in objectInitialization:
    #             if objectInitial.getAttribute('objectRef') == object_name:
    #                 initialize = objectInitial
    #                 break
    #
    #         objectInitialPosition = initialize.getElementsByTagName('ObjectInitialPosition')
    #         objectInitialRotation = initialize.getElementsByTagName('ObjectInitialRotation')
    #         objectInitialVelocity = initialize.getElementsByTagName('ObjectInitialVelocity')
    #         objectInitialAngularVelocity = initialize.getElementsByTagName('ObjectInitialAngularVelocity')
    #
    #         position = lgsvl.Vector(float(objectInitialPosition[0].getAttribute('positionX')),
    #                                 float(objectInitialPosition[0].getAttribute('positionY')),
    #                                 float(objectInitialPosition[0].getAttribute('positionZ')))
    #         rotation = lgsvl.Vector(float(objectInitialRotation[0].getAttribute('rotationX')),
    #                                 float(objectInitialRotation[0].getAttribute('rotationY')),
    #                                 float(objectInitialRotation[0].getAttribute('rotationZ')))
    #         velocity = lgsvl.Vector(float(objectInitialVelocity[0].getAttribute('velocityX')),
    #                                 float(objectInitialVelocity[0].getAttribute('velocityY')),
    #                                 float(objectInitialVelocity[0].getAttribute('velocityZ')))
    #         angular_velocity = lgsvl.Vector(float(objectInitialAngularVelocity[0].getAttribute('angularVelocityX')),
    #                                         float(objectInitialAngularVelocity[0].getAttribute('angularVelocityY')),
    #                                         float(objectInitialAngularVelocity[0].getAttribute('angularVelocityZ')))
    #         state = lgsvl.AgentState()
    #         state.transform.position = position
    #         state.transform.rotation = rotation
    #         state.velocity = velocity
    #         state.angular_velocity = angular_velocity
    #
    #         if object_type == 'Ego':
    #             ego = self.sim.add_agent(
    #                 self.env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5),
    #                 lgsvl.AgentType.EGO, state)
    #             ego.on_collision(on_collision)
    #             ego.old_uid = object_uid
    #             scenarioObject.setAttribute('uid', ego.uid)
    #             # scenarioObject.setAttribute('old_uid', object_uid)
    #         elif object_type == 'NPC':
    #             npc = self.sim.add_agent(object_model, lgsvl.AgentType.NPC, state, object_color)
    #             npc.old_uid = object_uid
    #             scenarioObject.setAttribute('uid', npc.uid)
    #             # scenarioObject.setAttribute('old_uid', object_uid)
    #         elif object_type == 'Pedestrian':
    #             p = self.sim.add_agent(object_model, lgsvl.AgentType.PEDESTRIAN, state)
    #             p.old_uid = object_uid
    #             scenarioObject.setAttribute('uid', p.uid)
    #             # scenarioObject.setAttribute('old_uid', object_uid)
    #         # print(scenarioObject.getAttribute('uid'), scenarioObject.getAttribute('old_uid'))
    #
    #     action_dict = {}
    #
    #     for objectAction in objectActions:
    #         # print('in')
    #         objectRef = objectAction.getElementsByTagName('objectRef')[0].getAttribute('objectRef')
    #         objectUid = None
    #         for scenarioObject in scenarioObjects:
    #             if scenarioObject.getAttribute('name') == objectRef:
    #                 objectUid = scenarioObject.getAttribute('uid')
    #
    #                 for agent in self.sim.get_agents():
    #                     if agent.old_uid == objectUid:
    #                         objectUid = agent.uid
    #                         # print('here')
    #                         break
    #         # print('objectUid', objectUid)
    #         wayPoints = objectAction.getElementsByTagName('WayPoint')
    #         wp_list = []
    #         state_list = []
    #         for wayPoint in wayPoints:
    #             # print('in')
    #             speed = float(
    #                 wayPoint.getElementsByTagName('DynamicParameters')[0].getElementsByTagName('Speed')[0].getAttribute(
    #                     'speed'))
    #
    #             # print(speed)
    #             # modified = modified_speed[int(wayPoint.getAttribute('timeStamp')) - 1]
    #             # coefficient = modified / speed
    #             coefficient = 1
    #
    #             velocity = wayPoint.getElementsByTagName('DynamicParameters')[0].getElementsByTagName('Velocity')[0]
    #             velocity = lgsvl.Vector(float(velocity.getAttribute('velocityX')) * coefficient,
    #                                     float(velocity.getAttribute('velocityY')) * coefficient,
    #                                     float(velocity.getAttribute('velocityZ')) * coefficient)
    #             angular_velocity = \
    #                 wayPoint.getElementsByTagName('DynamicParameters')[0].getElementsByTagName('AngularVelocity')[0]
    #             angular_velocity = lgsvl.Vector(float(angular_velocity.getAttribute('angularVelocityX')),
    #                                             float(angular_velocity.getAttribute('angularVelocityY')),
    #                                             float(angular_velocity.getAttribute('angularVelocityZ')))
    #
    #             position = \
    #                 wayPoint.getElementsByTagName('GeographicParameters')[0].getElementsByTagName('ObjectPosition')[
    #                     0]
    #             position = lgsvl.Vector(float(position.getAttribute('positionX')),
    #                                     float(position.getAttribute('positionY')),
    #                                     float(position.getAttribute('positionZ')))
    #             rotation = \
    #                 wayPoint.getElementsByTagName('GeographicParameters')[0].getElementsByTagName('ObjectRotation')[
    #                     0]
    #             rotation = lgsvl.Vector(float(rotation.getAttribute('rotationX')),
    #                                     float(rotation.getAttribute('rotationY')),
    #                                     float(rotation.getAttribute('rotationZ')))
    #
    #             if objectRef.__contains__('Pedestrian'):
    #                 wp = lgsvl.WalkWaypoint(position, 0)
    #             else:
    #                 wp = lgsvl.DriveWaypoint(position, 12 if speed < 1 else speed, rotation)
    #             wp_list.append(wp)
    #
    #             state = lgsvl.AgentState()
    #             state.transform.position = position
    #             state.transform.rotation = rotation
    #             state.velocity = velocity
    #             state.angular_velocity = angular_velocity
    #             state_list.append(state)
    #         # print(objectUid)
    #         action_dict.update({objectUid: {'objectRef': objectRef, 'wayPoints': wp_list, 'states': state_list}})
    #
    #     # print(action_dict)
    #     controllables = self.sim.get_controllables("signal")
    #     control_policy = "green=3;loop"
    #     for con in controllables:
    #         # Control this traffic light with a new control policy
    #         con.control(control_policy)
    #
    #     agents = self.sim.get_agents()
    #
    #     for agent in agents:
    #         print(agent, agent.uid)
    #
    #     timestep = float(root.getAttribute('timestep'))
    #     if self.enable_ads:
    #         print('connected')
    #         keys = action_dict.keys()
    #         for i in range(1, len(agents)):
    #             if agents[i].uid in keys:
    #                 agents[i].follow(action_dict[agents[i].uid]['wayPoints'])
    #         agents[0].connect_bridge(self.env.str("LGSVL__AUTOPILOT_0_HOST", self.bridge_host),
    #                                  self.env.int("LGSVL__AUTOPILOT_0_PORT", self.bridge_port))
    #
    #     print(len(action_dict[agents[0].uid]['wayPoints']))
    #     if agents[0].bridge_connected:
    #         print('connected to autonomous driving system (Apollo 5.0) successfully, running with Apollo...')
    #         self.sim.run(len(action_dict[agents[0].uid]['wayPoints']) * timestep)
    #     else:
    #         print('ADS is not enabled, replaying the scenario {}...'.format(self.scenario_file))
    #
    #         # print(action_dict)
    #         keys = action_dict.keys()
    #         for i in range(1, len(agents)):
    #             if agents[i].uid in keys:
    #                 agents[i].follow(action_dict[agents[i].uid]['wayPoints'])
    #
    #         for i in range(len(action_dict[agents[0].uid]['wayPoints'])):
    #             state = action_dict[agents[0].uid]['states'][i]
    #             agents[0].state = state
    #             print('---------- ', i, ' ----------')
    #             self.sim.run(0.5)
