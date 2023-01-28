#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import unittest

import lgsvl

from .common import SimConnection, spawnState

PROBLEM = "Object reference not set to an instance of an object"


class TestSimulator(unittest.TestCase):

    def test_scene(self):  # Check if the right scene was loaded
        with SimConnection() as sim:
            self.assertEqual(sim.current_scene, "BorregasAve")

    def test_unload_scene(self):  # Check if a different scene gets loaded
        with SimConnection() as sim:
            self.assertEqual(sim.current_scene, "BorregasAve")
            sim.load("CubeTown")
            self.assertEqual(sim.current_scene, "CubeTown")

    def test_spawns(self):  # Check if there is at least 1 spawn point for Ego Vehicles
        with SimConnection() as sim:
            spawns = sim.get_spawn()
            self.assertGreater(len(spawns), 0)

    def test_run_time(self):  # Check if the simulator runs 2 seconds
        with SimConnection() as sim:
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, spawnState(sim))
            time = 2.0
            initial_time = sim.current_time

            sim.run(time)
            self.assertAlmostEqual(sim.current_time - initial_time, time, delta=0.1)

    def test_non_realtime(self):  # Check if non-realtime simulation runs
        with SimConnection() as sim:
            initial_time = sim.current_time
            sim.run(time_limit=3, time_scale=2)

            self.assertAlmostEqual(sim.current_time-initial_time, 3, delta=0.1)

    def test_reset(self):  # Check if sim.reset resets the time and frame
        with SimConnection() as sim:
            sim.run(1.0)

            sim.reset()

            self.assertAlmostEqual(sim.current_time, 0)
            self.assertEqual(sim.current_frame, 0)

    def test_raycast(self):  # Check if raycasting works
        with SimConnection() as sim:
            spawns = sim.get_spawn()
            state = lgsvl.AgentState()
            state.transform = spawns[0]
            forward = lgsvl.utils.transform_to_forward(state.transform)
            right = lgsvl.utils.transform_to_right(state.transform)
            up = lgsvl.utils.transform_to_up(state.transform)
            sim.add_agent(lgsvl.wise.DefaultAssets.ego_jaguar2015xe_apollo5, lgsvl.AgentType.EGO, state)

            p = spawns[0].position
            p.y += 1
            layer_mask = 0
            for bit in [0, 4, 13, 14, 18]:  # do not put 8 here, to not hit EGO vehicle itself
                layer_mask |= 1 << bit

            # Right
            hit = sim.raycast(p, right, layer_mask)
            self.assertTrue(hit)
            self.assertAlmostEqual(hit.distance, 15.089282989502, places=3)

            # Left
            hit = sim.raycast(p, -right, layer_mask)
            self.assertTrue(hit)
            self.assertAlmostEqual(hit.distance, 19.7292556762695, places=3)

            # Back
            hit = sim.raycast(p, -forward, layer_mask)
            self.assertFalse(hit)

            # Front
            hit = sim.raycast(p, forward, layer_mask)
            self.assertFalse(hit)

            # Up
            hit = sim.raycast(p, up, layer_mask)
            self.assertFalse(hit)

            # Down
            hit = sim.raycast(p, -up, layer_mask)
            self.assertTrue(hit)
            self.assertAlmostEqual(hit.distance, 1.0837641954422, places=3)

    def test_weather(self):  # Check that the weather state can be read properly and changed
        with SimConnection() as sim:
            rain = sim.weather.rain
            fog = sim.weather.fog
            wetness = sim.weather.wetness

            self.assertAlmostEqual(rain, 0)
            self.assertAlmostEqual(fog, 0)
            self.assertAlmostEqual(wetness, 0)

            sim.weather = lgsvl.WeatherState(rain=0.5, fog=0.3, wetness=0.8, cloudiness=0, damage=0)

            rain = sim.weather.rain
            fog = sim.weather.fog
            wetness = sim.weather.wetness

            self.assertAlmostEqual(rain, 0.5)
            self.assertAlmostEqual(fog, 0.3)
            self.assertAlmostEqual(wetness, 0.8)

    def test_invalid_weather(self):  # Check that the API/Unity properly handles unexpected inputs
        with SimConnection() as sim:
            rain = sim.weather.rain
            fog = sim.weather.fog
            wetness = sim.weather.wetness

            self.assertAlmostEqual(rain, 0)
            self.assertAlmostEqual(fog, 0)
            self.assertAlmostEqual(wetness, 0)

            sim.weather = lgsvl.WeatherState(rain=1.4, fog=-3, wetness="a", cloudiness=0, damage=0)

            rain = sim.weather.rain
            fog = sim.weather.fog
            wetness = sim.weather.wetness

            self.assertAlmostEqual(rain, 1)
            self.assertAlmostEqual(fog, 0)
            self.assertAlmostEqual(wetness, 0)

            sim.weather = lgsvl.WeatherState(rain=True, fog=0, wetness=0, cloudiness=0, damage=0)

            rain = sim.weather.rain
            self.assertAlmostEqual(rain, 0)

    def test_time_of_day(self):  # Check that the time of day is reported properly and can be set
        with SimConnection() as sim:
            # self.assertAlmostEqual(sim.time_of_day, 9, delta=0.5)
            sim.set_time_of_day(18.00)
            self.assertAlmostEqual(sim.time_of_day, 18, delta=0.5)

            sim.set_time_of_day(13.5, False)
            self.assertAlmostEqual(sim.time_of_day, 13.5, delta=0.5)
            sim.run(3)
            self.assertGreater(sim.time_of_day, 13.5)

    def test_wrong_time_of_day(self):  # Check that the time of day is not broken with inappropriate inputs
        with SimConnection() as sim:
            sim.set_time_of_day(40)
            self.assertAlmostEqual(sim.time_of_day, 0)
            with self.assertRaises(TypeError):
                sim.set_time_of_day("asdf")

    def test_reset_weather(self):  # Check that reset sets the weather variables back to 0
        with SimConnection() as sim:
            rain = sim.weather.rain
            fog = sim.weather.fog
            wetness = sim.weather.wetness
            self.assertAlmostEqual(rain, 0)
            self.assertAlmostEqual(fog, 0)
            self.assertAlmostEqual(wetness, 0)

            sim.weather = lgsvl.WeatherState(rain=0.5, fog=0.3, wetness=0.8, cloudiness=0, damage=0)
            rain = sim.weather.rain
            fog = sim.weather.fog
            wetness = sim.weather.wetness
            self.assertAlmostEqual(rain, 0.5)
            self.assertAlmostEqual(fog, 0.3)
            self.assertAlmostEqual(wetness, 0.8)

            sim.reset()
            rain = sim.weather.rain
            fog = sim.weather.fog
            wetness = sim.weather.wetness
            self.assertAlmostEqual(rain, 0)
            self.assertAlmostEqual(fog, 0)
            self.assertAlmostEqual(wetness, 0)

    def test_reset_time(self):  # Check that reset sets time back to the default
        with SimConnection() as sim:
            default_time = sim.time_of_day
            sim.set_time_of_day((default_time+5)%24)
            sim.reset()
            self.assertAlmostEqual(default_time, sim.time_of_day)

    # THIS TEST RUNS LAST
    def test_ztypo_map(self):  # Check if an exception is raised with a misspelled map name is loaded
        #with self.assertRaises(TestTimeout):
            with SimConnection() as sim:
                with self.assertRaises(Exception) as e:
                    sim.load("SF")
                self.assertFalse(repr(e.exception).startswith(PROBLEM))

    def test_negative_time(self):  # Check that a negative time can be handled properly
        with SimConnection() as sim:
            initial_time = sim.current_time
            sim.run(-5)
            post_time = sim.current_time
            self.assertAlmostEqual(initial_time, post_time)

    def test_get_gps(self):  # Checks that GPS reports the correct values
        with SimConnection() as sim:
            spawn = sim.get_spawn()[0]
            gps = sim.map_to_gps(spawn)
            self.assertAlmostEqual(gps.latitude, 37.4173601699318)
            self.assertAlmostEqual(gps.longitude, -122.016132757826)
            self.assertAlmostEqual(gps.northing, 4141627.34000015)
            self.assertAlmostEqual(gps.easting, 587060.970000267)
            self.assertAlmostEqual(gps.altitude, -1.03600001335144)
            self.assertAlmostEqual(gps.orientation, -104.823394775391)

    def test_from_northing(self):  # Check that position vectors are correctly generated given northing and easting
        with SimConnection() as sim:
            spawn = sim.get_spawn()[0]
            location = sim.map_from_gps(northing=4141627.34000015, easting=587060.970000267)
            self.assertAlmostEqual(spawn.position.x, location.position.x, places=1)
            self.assertAlmostEqual(spawn.position.z, location.position.z, places=1)

    def test_from_latlong(self):  # Check that position vectors are correctly generated given latitude and longitude
        with SimConnection() as sim:
            spawn = sim.get_spawn()[0]
            location = sim.map_from_gps(latitude=37.4173601699318, longitude=-122.016132757826)
            self.assertAlmostEqual(spawn.position.x, location.position.x, places=1)
            self.assertAlmostEqual(spawn.position.z, location.position.z, places=1)

    def test_from_alt_orient(self):  # Check that position vectors are correctly generated with altitude and orientation
        with SimConnection() as sim:
            spawn = sim.get_spawn()[0]
            location = sim.map_from_gps(northing=4141627.34000015, easting=587060.970000267, altitude=-1.03600001335144, orientation=-104.823371887207)
            self.assertAlmostEqual(spawn.position.y, location.position.y, places=1)
            self.assertAlmostEqual(spawn.rotation.y, location.rotation.y, places=1)

    def test_false_latlong(self):  # Check that exceptions are thrown when inputting invalid lat long values
        with SimConnection() as sim:
            with self.assertRaises(ValueError):
                sim.map_from_gps(latitude=91, longitude=0)

            with self.assertRaises(ValueError):
                sim.map_from_gps(latitude=0, longitude=200)

    def test_false_easting(self):  # Check that exceptions are thrown when inputting invalid northing easting values
        with SimConnection() as sim:
            with self.assertRaises(ValueError):
                sim.map_from_gps(easting=1000000000, northing=500000)

            with self.assertRaises(ValueError):
                sim.map_from_gps(northing=-50, easting=500000)

    def test_version_info(self):  # Check that the sim reports a numerical version number
        with SimConnection() as sim:
            version = sim.version
            self.assertTrue(isinstance(version, str))
            self.assertTrue(isinstance(float(version[:4]), float))

    def test_lat_northing(self):  # Checks that exceptions are thrown if an invalid pair of gps values are given
        with SimConnection() as sim:
            with self.assertRaises(Exception) as e:
                sim.map_from_gps(northing=4812775, latitude=37.7)
            self.assertIn("Either latitude and longitude or northing and easting should be specified", repr(e.exception))

    # def test_both_lat_northing(self):
    #     with SimConnection() as sim:
    #         with self.assertRaises(Exception) as e:
    #             sim.map_from_gps(northing=1, easting=2, latitude=3, longitude=4)

    def test_lat_str(self):  # Checks that exceptions are thrown if a string is given for latitude
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                sim.map_from_gps(latitude="asdf", longitude=2)

    def test_long_str(self):  # Checks that exceptions are thrown if a string is given for longitude
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                sim.map_from_gps(latitude=1, longitude="asdf")

    def test_northing_str(self):  # Checks that exceptions are thrown if a string is given for northing
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                sim.map_from_gps(northing="asdf", easting=2)

    def test_easting_str(self):  # Checks that exceptions are thrown if a string is given for easting
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                sim.map_from_gps(northing=1, easting="asdF")

    def test_altitude_str(self):  # Checks that exceptions are thrown if a string is given for altitude
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                sim.map_from_gps(latitude=1, longitude=2, altitude="asd")

    def test_orientation_str(self):  # Checks that exceptions are thrown if a string is given for orientation
        with SimConnection() as sim:
            with self.assertRaises(TypeError):
                sim.map_from_gps(latitude=1, longitude=2, orientation="asdf")
