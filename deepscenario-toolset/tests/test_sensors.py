#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import unittest
import os
import lgsvl
from .common import SimConnection, spawnState, notAlmostEqual

# TODO add tests for bridge to check if enabled sensor actually sends data


class TestSensors(unittest.TestCase):
    def test_apollo_5_sensors(self):  # Check that Apollo 3.5 sensors are created and are positioned reasonably
        with SimConnection(60) as sim:
            agent = self.create_EGO(sim, lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5)
            expectedSensors = ['Lidar', 'GPS', 'Telephoto Camera', \
                'Main Camera', 'IMU', 'CAN Bus', 'Radar']
            sensors = agent.get_sensors()
            sensorNames = [s.name for s in sensors]

            for sensor in expectedSensors:
                with self.subTest(sensor):
                    self.assertIn(sensor, sensorNames)

            for s in sensors:
                msg = "Apollo 3.0 Sensor " + s.name
                with self.subTest(msg):
                    self.valid_sensor(s, msg)

    @unittest.skip("No SF vehicle")
    def test_santafe_sensors(self):  # Check that Apollo Santa Fe sensors are created and are positioned reasonably
        with SimConnection() as sim:
            agent = self.create_EGO(sim, lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5)
            expectedSensors = ['velodyne', 'GPS', 'Telephoto Camera', 'Main Camera', \
                'IMU', 'RADAR', 'CANBUS', 'Segmentation Camera', 'Left Camera', 'Right Camera']
            sensors = agent.get_sensors()
            sensorNames = [s.name for s in sensors]

            for sensor in expectedSensors:
                with self.subTest(sensor):
                    self.assertIn(sensor, sensorNames)

            for s in sensors:
                msg = "Lincoln Apollo Sensor " + s.name
                with self.subTest(msg):
                    self.valid_sensor(s, msg)

    @unittest.skip("No LGSVL Vehicle")
    def test_lgsvl_sensors(self):  # Check that LGSVL sensors are created and are positioned reasonably
        with SimConnection() as sim:
            agent = self.create_EGO(sim, lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5)
            expectedSensors = ['velodyne', 'GPS', 'Telephoto Camera', 'Main Camera', \
                'IMU', 'RADAR', 'CANBUS', 'Segmentation Camera', 'Left Camera', 'Right Camera']
            sensors = agent.get_sensors()
            sensorNames = [s.name for s in sensors]

            for sensor in expectedSensors:
                with self.subTest(sensor):
                    self.assertIn(sensor, sensorNames)

            for s in sensors:
                msg = "lgsvl Sensor " + s.name
                with self.subTest(msg):
                    self.valid_sensor(s, msg)

    @unittest.skip("No EP Vehicle")
    def test_ep_sensors(self):  # Check that Apollo EP sensors are created and are positioned reasonably
        with SimConnection() as sim:
            agent = self.create_EGO(sim, "EP_Rigged-apollo")
            expectedSensors = ['velodyne', 'GPS', 'Telephoto Camera', 'Main Camera', \
            'IMU', 'RADAR', 'CANBUS', 'Segmentation Camera', 'Left Camera', 'Right Camera']
            sensors = agent.get_sensors()
            sensorNames = [s.name for s in sensors]

            for sensor in expectedSensors:
                with self.subTest(sensor):
                    self.assertIn(sensor, sensorNames)

            for s in sensors:
                msg = "EP Sensor " + s.name
                with self.subTest(msg):
                    self.valid_sensor(s, msg)

    def test_apollo_sensors(self):  # Check that all the Apollo sensors are there
        with SimConnection() as sim:
            agent = self.create_EGO(sim, lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5)
            expectedSensors = ["Lidar", "GPS", "Telephoto Camera", "Main Camera", "IMU", \
                 "CAN Bus", "Radar"]

            sensors = agent.get_sensors()
            sensorNames = [s.name for s in sensors]

            for sensor in expectedSensors:
                with self.subTest(sensor):
                    self.assertIn(sensor, sensorNames)

            for s in sensors:
                msg = "Apollo Sensor " + s.name
                with self.subTest(msg):
                    self.valid_sensor(s, msg)

    def test_autoware_sensors(self):  # Check that all Autoware sensors are there
        with SimConnection() as sim:
            agent = self.create_EGO(sim, lgsvl.wise.DefaultAssets.ego_jaguae2015xe_autowareai)
            expectedSensors = ["Lidar", "GPS", "Main Camera", "IMU"]

            sensors = agent.get_sensors()
            sensorNames = [s.name for s in sensors]

            for sensor in expectedSensors:
                with self.subTest(sensor):
                    self.assertIn(sensor, sensorNames)

            for s in sensors:
                msg = "Autoware Sensor " + s.name
                with self.subTest(msg):
                    self.valid_sensor(s, msg )

    def test_save_sensor(self):  # Check that sensor results can be saved
        with SimConnection(120) as sim:

            path = "main-camera.png"
            islocal = os.environ.get("LGSVL__SIMULATOR_HOST", "127.0.0.1") == "127.0.0.1"

            if islocal:
                path = os.getcwd() + path
                if os.path.isfile(path):
                    os.remove(path)

            agent = self.create_EGO(sim, lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5)
            sensors = agent.get_sensors()

            savedSuccess = False

            for s in sensors:
                if s.name == "Main Camera":
                    savedSuccess = s.save(path)
                    break

            self.assertTrue(savedSuccess)

            if islocal:
                self.assertTrue(os.path.isfile(path))
                self.assertGreater(os.path.getsize(path), 0)
                os.remove(path)

    def test_save_lidar(self):  # Check that LIDAR sensor results can be saved
        with SimConnection(240) as sim:
            path = "lidar.pcd"
            islocal = os.environ.get("LGSVL__SIMULATOR_HOST", "127.0.0.1") == "127.0.0.1"

            if islocal:
                path = os.getcwd() + path
                if os.path.isfile(path):
                    os.remove(path)

            agent = self.create_EGO(sim, lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5)
            sensors = agent.get_sensors()
            savedSuccess = False

            for s in sensors:
                if s.name == "Lidar":
                    savedSuccess = s.save(path)
                    break

            self.assertTrue(savedSuccess)

            if islocal:
                self.assertTrue(os.path.isfile(path))
                self.assertGreater(os.path.getsize(path), 0)
                os.remove(path)

    def test_GPS(self):  # Check that the GPS sensor works
        with SimConnection() as sim:
            state = lgsvl.AgentState()
            state.transform = sim.get_spawn()[0]
            right = lgsvl.utils.transform_to_right(state.transform)
            state.velocity = -50 * right
            agent = sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)
            sensors = agent.get_sensors()
            initialGPSData = None
            gps = None
            for s in sensors:
                if s.name == "GPS":
                    gps = s
                    initialGPSData = gps.data
            sim.run(1)
            finalGPSData = gps.data

            latChanged = notAlmostEqual(initialGPSData.latitude, finalGPSData.latitude)
            lonChanged = notAlmostEqual(initialGPSData.longitude, finalGPSData.longitude)
            northingChanged = notAlmostEqual(initialGPSData.northing, finalGPSData.northing)
            eastingChanged = notAlmostEqual(initialGPSData.easting, finalGPSData.easting)
            self.assertTrue(latChanged or lonChanged)
            self.assertTrue(northingChanged or eastingChanged)
            self.assertNotAlmostEqual(gps.data.latitude, 0)
            self.assertNotAlmostEqual(gps.data.longitude, 0)
            self.assertNotAlmostEqual(gps.data.northing, 0)
            self.assertNotAlmostEqual(gps.data.easting, 0)
            self.assertNotAlmostEqual(gps.data.altitude, 0)
            self.assertNotAlmostEqual(gps.data.orientation, 0)

    def test_sensor_disabling(self):  # Check if sensors can be enabled
        with SimConnection() as sim:
            agent = sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, spawnState(sim))
            for s in agent.get_sensors():
                if s.name == "Lidar":
                    s.enabled = False

            for s in agent.get_sensors():
                with self.subTest(s.name):
                    if (s.name == "Lidar"):
                        self.assertFalse(s.enabled)
                    else:
                        self.assertTrue(s.enabled)

    def test_sensor_equality(self):  # Check that sensor == operator works
        with SimConnection() as sim:
            agent = sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, spawnState(sim))
            prevSensor = None
            for s in agent.get_sensors():
                self.assertTrue(s == s)
                if prevSensor is not None:
                    self.assertFalse(s == prevSensor)
                prevSensor = s

    def create_EGO(self, sim, name):  # Creates the speicified EGO and removes any others
        return sim.add_agent(name, lgsvl.AgentType.EGO, spawnState(sim))

    def valid_sensor(self, sensor, msg):  # Checks that the sensor is close to the EGO and not overly rotated
        self.assertBetween(sensor.transform.rotation, 0, 360, msg)
        self.assertBetween(sensor.transform.position, -10, 10, msg)

    def assertBetween(self, vector, min, max, msg):  # Tests that the given vectors components are within the min and max
        self.assertGreaterEqual(vector.x, min, msg)
        self.assertLessEqual(vector.x, max, msg)

        self.assertGreaterEqual(vector.y, min, msg)
        self.assertLessEqual(vector.y, max, msg)

        self.assertGreaterEqual(vector.z, min, msg)
        self.assertLessEqual(vector.z, max, msg)
