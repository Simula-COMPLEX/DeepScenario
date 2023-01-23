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

# Usgae

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
