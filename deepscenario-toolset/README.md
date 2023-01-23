# DeepScenario Toolsets

# Requirements

* Python 3.6 or higher

# Installation

## Option 1
1. Download the *[lastest version](https://github.com/Simula-COMPLEX/DeepScenario/releases/download/deepscenario-toolset/scenario-toolset.tar.gz)* of toolsets;

2. Install the toolsets in your development environment.
```python
pip install scenario-toolset.tar.gz
```
## Option 2
1. Clone or download the repoisitory: https://github.com/Simula-COMPLEX/DeepScenario;
2. Run the following command under *deepscenario-toolset* directory to install Python files and necessary dependencies:

```python
pip3 install --user .

# or install in development mode
pip3 install --user -e .
```

# Usage

*DeepScenario toolsets* is an extension of *[PythonAPI](https://github.com/lgsvl/PythonAPI)* developed by *[SVLSimulator](https://www.svlsimulator.com/)*, for how to use normal functionality of the APIs, please refer [here](https://www.svlsimulator.com/docs/python-api/python-api/).
Examples of usage of our toolsets can be found [here](https://github.com/Simula-COMPLEX/DeepScenario/blob/main/deepscenario-toolset/tests/test_scenariotoolset.py). We describe several examples of using *ScenarioCollector* and *ScenarioRunner* as follows.

## ScenarioCollector

*ScenarioCollector* can automatically collect scenario at runtime, below we show how it works by defining a simple scenario. The scenario is *[npc-follow-the-lane](https://github.com/lgsvl/PythonAPI/blob/master/quickstart/10-npc-follow-the-lane.py)*, which is an example from *SVLSimulator*. To automatically collect the scenario, only four addition lines of code need to be added.

### Step 1 Load the environment and define vehicles and their behaviors
```python
import lgsvl
from environs import Env

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
sim.add_agent(env.str("LGSVL__VEHICLE_0", lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5),
              lgsvl.AgentType.EGO, state)

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

agents = sim.get_agents()
```

### Step 2 Initialize *ScenarioCollector*

```python
sc_collector = lgsvl.scenariotoolset.ScenarioCollector(city_map='BorregasAve')  # BorregasAve, SanFrancisco
sc_collector.initialize_story(agents, datatime=str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
                              v_date=str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                              timestamp=int(time.time()), weatherdataset="None")
```

### Step 3 Run and collect the scenario

```python
timestep = 0.5
for i in range(10):
    sc_collector.create_story_by_timestamp(i + 1, agents, sim)
    sim.run(timestep)
    
sc_collector.save_scenario(timestep, './test.deepscenario')
```

## ScenarioRunner
*ScenarioRunner* can support replaying scenarios by taking scenario files as inputs. In addition to replaying scenarios, *ScenarioRunner* can also be used to check scenario information, like entities information. Finally, *ScenarioRunner* can print scene by *timestep*, which is expected to facilitate further
analysis and diagnoses of autonomous driving systems. We show the usage of *ScenarioRunner* as follows.

### Usage 1 Get entity information
Entities includes autonomous vehicles, other vehicles, and pedestrians, which may appear in a driving scenario. Below is how to get information of entities using *ScenarioRunner*.

```python
runner = lgsvl.scenariotoolset.ScenarioRunner()
runner.load_scenario_file(scenario_filepath_or_buffer='./deepscenario/rear_end_collision.deepscenario')
print(runner.get_entities_info())
```

The information returned is in *json* format, as can be seen below.
```json
{
  "Ego0": {
    "model": "Sedan",
    "color": "Default",
    "type": "Ego",
    "uid": "470ce96f-3ac6-42c8-a64b-6196a8d235db",
    "initialization": {
      "position": {
        "x": -50.34,
        "y": -1.036,
        "z": -9.03
      },
      "rotation": {
        "x": 0.0,
        "y": 104.823,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "angular_velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      }
    }
  },
  "NPC0": {
    "model": "Sedan",
    "color": "white",
    "type": "NPC",
    "uid": "Sedan(Clone)362986ab-a2a8-49d1-aa74-6ec130ebe17a",
    "initialization": {
      "position": {
        "x": -40.673,
        "y": -1.036,
        "z": -11.588
      },
      "rotation": {
        "x": 0.0,
        "y": 104.823,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "angular_velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      }
    }
  },
  "Pedestrian0": {
    "model": "Bob",
    "color": "Default",
    "type": "Pedestrian",
    "uid": "0f79fbef-e285-4128-8919-417fa0588f01",
    "initialization": {
      "position": {
        "x": -2.004,
        "y": -1.036,
        "z": -21.822
      },
      "rotation": {
        "x": 0.0,
        "y": 104.823,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "angular_velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      }
    }
  }
}
```

### Usage 2 Get driving scene by timestep
A driving scene describes snapshots of the environment’s state without involving sufficient time series information, we can get a driving scene by a specific timestep using *ScenarioRunner*.

```python
runner = lgsvl.scenariotoolset.ScenarioRunner()
runner.load_scenario_file(scenario_filepath_or_buffer='./deepscenario/rear_end_collision.deepscenario')
print(runner.get_scene_by_timestep(timestep=21))
```

The returned driving scene is shown as follows.

```json
{
  "timestep": 21,
  "Ego0": {
    "dynamic_parameters": {
      "speed": "16.865",
      "velocity": {
        "x": "16.305",
        "y": "-0.24",
        "z": "-4.301"
      },
      "angular_velocity": {
        "x": "0.002",
        "y": "-0.002",
        "z": "0.031"
      }
    },
    "geographic_parameters": {
      "position": {
        "x": "-22.151",
        "y": "-1.846",
        "z": "-16.493"
      },
      "rotation": {
        "x": "0.687",
        "y": "104.746",
        "z": "359.769"
      },
      "gps": {
        "altitude": "-1.846",
        "easting": "587053.507",
        "latitude": "37.417",
        "longitude": "-122.016",
        "northing": "4141599.151",
        "orientation": "-104.746"
      }
    }
  },
  "NPC0": {
    "dynamic_parameters": {
      "speed": "12.0",
      "velocity": {
        "x": "11.598",
        "y": "-0.25",
        "z": "-3.069"
      },
      "angular_velocity": {
        "x": "0",
        "y": "0",
        "z": "0"
      }
    },
    "geographic_parameters": {
      "position": {
        "x": "7.661",
        "y": "-2.23",
        "z": "-24.38"
      },
      "rotation": {
        "x": "0.0",
        "y": "104.823",
        "z": "-0.0"
      },
      "gps": {
        "altitude": "-2.23",
        "easting": "587045.62",
        "latitude": "37.417",
        "longitude": "-122.016",
        "northing": "4141569.339",
        "orientation": "-104.823"
      }
    }
  },
  "Pedestrian0": {
    "dynamic_parameters": {
      "speed": "0.0",
      "velocity": {
        "x": "0",
        "y": "0",
        "z": "0"
      },
      "angular_velocity": {
        "x": "0",
        "y": "0",
        "z": "0"
      }
    },
    "geographic_parameters": {
      "position": {
        "x": "1.665",
        "y": "-2.084",
        "z": "-20.263"
      },
      "rotation": {
        "x": "0",
        "y": "65.925",
        "z": "0"
      },
      "gps": {
        "altitude": "-2.084",
        "easting": "587049.737",
        "latitude": "37.417",
        "longitude": "-122.016",
        "northing": "4141575.335",
        "orientation": "-65.925"
      }
    }
  }
}
```

### Usage 3 Replay driving scenario without ADSs
*ScenarioRunner* can exactly replay the behaviors of the autonomous vehicle and obstacles by reading their kinetic parameters. By selecting and replaying driving scenarios in this way, *ScenarioRunner* can facilitate further analysis and diagnoses.

```python
runner = lgsvl.scenariotoolset.ScenarioRunner()
runner.load_scenario_file(scenario_filepath_or_buffer='./deepscenario/rear_end_collision.deepscenario')
runner.connect_simulator_ads(simulator_port=8181, bridge_port=9090)

runner.run(mode=0) # mode=0: disable ADSs; mode=1: enable ADSs
```

An running example of replaying scenarios in this mode is avaliable [here]().

### Usage 4 Replay driving scenario with ADSs
*ScenarioRunner* can also integrate different ADSs. In this way, the behaviors of the ego vehicle are not replayed by *ScenarioRunner* but controlled by the ADS, and the behaviors of obstacles can still be accurately replayed. This way enables testing various ADSs by integrating ADSs in the replayed driving conditions.

```python
runner = lgsvl.scenariotoolset.ScenarioRunner()
runner.load_scenario_file(scenario_filepath_or_buffer='./deepscenario/rear_end_collision.deepscenario')
runner.connect_simulator_ads(simulator_port=8181, bridge_port=9090)

runner.run(mode=1) # mode=0: disable ADSs; mode=1: enable ADSs
```

An running example of replaying scenarios in this mode is avaliable [here]().
