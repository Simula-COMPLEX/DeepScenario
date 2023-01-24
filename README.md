[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
# DeepScenario: An Open Driving Scenario Dataset for Autonomous Driving System Testing

> **Dataset avaliability** - To facilitate reviewing *DeepScenario* dataset, reviewers please refer to the corresponding dataset in this repository. We also plan to release the dataset in permanent repositories like Zenodo once it gets accepted.<br/>

This repoisitory contains:

1. **[deepscenario-dataset](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-dataset)** - DeepScenario dataset, which includes driving scenarios generated by executing three scenario generation strategies: *Reinforcement Learning (RL)-based Strategy*, *Random-based Strategy*, *Greedy-based Strategy*;
2. **[deepscenario-toolset](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-toolset)** - The toolset for *DeepScenario* dataset, including *ScenarioCollector* that can automatically collect driving scenarios, and *ScenarioRunner* that can support replaying driving scenarios.

## Table of Contents
- [Abstract](#abstract)
- [DeepScenario Dataset Description](#deepscenario-dataset-description)
  - [Dataset Structure](#dataset-structure)
  - [Fields in Scenario Attribute Files](#fields-in-scenario-attribute-files)
- [DeepScenario Toolset](#deepscenario-toolset)
  - [Installation](#installation)
  - [Usage](#usage)
- [Maintainers](#maintainers)
<!--
  - [Installation](#installation)
  - [ScenarioCollector](#scenariocollector)
  - [ScenarioRunner](#scenariorunner)
 -->

## Abstract
With the rapid development of autonomous driving systems (ADSs), testing ADSs under various driving conditions has become a key method to ensure the successful deployment of ADS in the real-world. However, it is impossible to test all the scenarios due to the inherent complexity and uncertainty of ADSs and the driving tasks. Further, testing of ADSs is expensive regarding time and computational resources. Therefore, a large-scale driving scenario dataset consisting of various driving conditions is needed. To this end, we present an open driving scenario dataset *DeepScenario*, containing over 30*K* *executable* driving scenarios, which are collected by 2880 test executions of three driving scenario generation strategies. Each scenario in the dataset is labeled with six attributes characterizing test results. We further show the attribute statistics and distribution of driving scenarios. For example, there are 1050 collision scenarios, in 917 scenarios there were collisions with other vehicles, 105 and 28 with pedestrians and static obstacles, respectively.

The scenario dataset generation process is shown in the following figure. As the figure shows, to generate driving scenarios, several *Test Setups* need to be specified. Then we execute an *Environment Configuration Framework*, which generates critical driving scenarios and tests an ADS by configuring its operating environment. After the test executions, the test results are further used for *Dataset Creation*.
Specifically, Each strategy was set up with three reward functions, *reward-ttc*, *reward-dto*, and *reward-jerk*. We introduced real-world weather data on four different days (i.e., *rain-day*, *rain-night*, *sunny-day*, and *sunny-night*) to simulate various weather conditions and their changes over time. The test executions were conducted on four roads (i.e., *road1*, *road2*, *road3*, and *road4*).

![image](https://github.com/Simula-COMPLEX/DeepScenario/blob/main/figures/dataset-generation.png)

## DeepScenario Dataset Description
*DeepScenario* dataset contains 33530 driving scenarios generated by executing three strategies: (i) *[rl_based-strategy](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-dataset/rl_based-strategy)*, (ii) *[random-strategy](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-dataset/random-strategy)*, and (iii) *[greedy-strategy](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-dataset/greedy-strategy)*, among which 6703 are generated by *rl_based-strategy*, which are less than the number of scenarios generated by *random-strategy* (i.e., 13565) and *greedy-strategy* (i.e., 13262). 

### Dataset Structure
The scenario dataset contains three directories corresponds to three strategies. And each strategy directory is organized following three reward function settings. We show scenario file naming convention and directory strcuture as follows.
<!--
Complete structure is shown [here](https://raw.githubusercontent.com/Simula-COMPLEX/DeepScenario/main/deepscenario-dataset/tree.md).
-->
```js
.
├── greedy-strategy
│   ├── reward-dto
│   │   ├── road1-rain_day-scenario-attributes.csv
│   │   ├── road1-rain_day-scenarios
│   │   │   ├── 0_scenario_0.deepscenario
│   │   │   ├── 0_scenario_1.deepscenario
│   │   │   ├── 0_scenario_2.deepscenario
│   │   │   ├── ...
│   │   │   ├── 6_scenario_0.deepscenario
│   │   │   ├── 6_scenario_1.deepscenario
│   │   │   ├── 6_scenario_2.deepscenario
│   │   │   ├── ...
│   │   │   ├── 20_scenario_0.deepscenario
│   │   │   ├── 20_scenario_1.deepscenario
│   │   │   ├── 20_scenario_2.deepscenario
│   │   │   ├── ...
│   │   ├── road1-rain_night-scenario-attributes.csv
│   │   ├── road1-rain_night-scenarios
│   │   │   ├── 0_scenario_0.deepscenario
│   │   │   ├── 0_scenario_1.deepscenario
│   │   │   ├── 0_scenario_2.deepscenario
│   │   │   ├── ...
│   │   ├── road1-sunny_day-scenario-attributes.csv
│   │   ├── road1-sunny_day-scenarios
│   │   │   ├── ...
│   │   ├── road1-sunny_night-scenario-attributes.csv
│   │   ├── road1-sunny_night-scenarios
│   │   │   ├── ...
│   │   ├── ...
│   │   ├── road4-rain_day-scenario-attributes.csv
│   │   ├── road4-rain_day-scenarios
│   │   │   ├── ...
│   │   ├── road4-rain_night-scenario-attributes.csv
│   │   ├── road4-rain_night-scenarios
│   │   │   ├── ...
│   │   ├── road4-sunny_day-scenario-attributes.csv
│   │   ├── road4-sunny_day-scenarios
│   │   │   ├── ...
│   │   ├── road4-sunny_night-scenario-attributes.csv
│   │   └── road4-sunny_night-scenarios
│   │   │   ├── ...
│   ├── reward-jerk
│   │   └── ...
│   └── reward-ttc
│   │   └── ...
├── random-strategy
│   ├── reward-dto
│   │   └── ...
│   ├── reward-jerk
│   │   └── ...
│   └── reward-ttc
│   │   └── ...
├── rl_based-strategy
│   ├── ...
└── tree.md
157 directories, 33662 files
```
For example, scenario directory **./greedy-strategy/reward-dto/road1-rain_day-scenarios** contains scenarios generated by executing *greedy-strategy* with test setup *reward-dto*, *road1*, *rain_day*. The attributes of each scenario are listed in **./greedy-strategy/reward-dto/road1-rain_day-scenario-attributes.csv**.

### Fields in Scenario Attribute Files

We show *[./greedy-strategy/reward-dto/road1-rain_day-scenario-attributes.csv](https://github.com/Simula-COMPLEX/DeepScenario/blob/main/deepscenario-dataset/greedy-strategy/reward-dto/road1-rain_day-scenario-attributes.csv)* as an example of scenario attribute file. Fields in scenario attribute file and their description are shown below.

<div class="scrollable-table-wrapper" markdown="block">

| Execution  | ScenarioID | Configuration_API_Description | Attribute[TTC] | Attribute[DTO] | Attribute[Jerk] | Attribute[COL] | Attribute[COLT] |Attribute[SAC]
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
|       0       | 0_scenario_0|A red BoxTruck is overtaking (near) the ego vehicle and maintaining lane.|100000|24.810964|3.4799999999999995|False|None|0|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
|      18       | 18_scenario_4 |A skyblue SUV is crossing the road (far) and maintaining lane.|100000|1.331153|5.299999999999999|True|pedestrian|2.3469087361531504|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

</div>

**Execution** -  This field indicates the ID of the test execution;

**ScenarioID** - This field indicates the ID of the scenario in the scenario dataset. For example, *0_scenario_0* is the 0th scenario collected when executing *execution 0*. In this example, the real scenario file can be located by its *ScenarioID*, which is *[./greedy-strategy/reward-dto/road1-rain_day-scenarios/0_scenario_0.deepscenario](https://github.com/Simula-COMPLEX/DeepScenario/blob/main/deepscenario-dataset/greedy-strategy/reward-dto/road1-rain_day-scenarios/0_scenario_0.deepscenario)*.

**Configuration_API_Description** - This field is a brief description of the configuration REST API used to generated the scenario;

**Attribute[TTC]** - This field is *Time-To-Collision (TTC)* attribute, which is a safety measure indicating the time it would take for a collision occurs, and smaller *TTC* values indicate higher safety risk;

**Attribute[DTO]** - This field is *Distance-To-Obstacles (DTO)* attribute, which is a safety measure indicating the distances to obstacles when an autonomous vehicle driving in the scenario, and smaller *DTO* values indicate higher safety risk;

**Attribute[Jerk]** - This field is *Jerk* attribute, which is a measure of comfort for passengers, and larger *Jerk* values indicate less comfort;

**Attribute[COL]** - This field is *Collision (COL)*, which is a Boolean attribute indicating if the autonomous vehicle collided with obstacles when driving in the scenario;

**Attribute[COLT]** - This field is *Collision Type (COLT)*, which is an enumerated attribute that shows the type of obstacle the autonomous vehicle collided with;

**Attribute[SAC]** - This field is *Speed-At-Collision (SAC)*, which is an attribute that records the speed at which the autonomous vehicle in the scenario collided (if it happened) with the obstacle.

## DeepScenario Toolset
The *DeepScenario* toolset includes *ScenarioCollector* and *ScenarioRunner*, which has been integrated into *[PythonAPI](https://github.com/lgsvl/PythonAPI)* developed by *[SVLSimulator](https://www.svlsimulator.com/)*.
The toolset has been tested on *[SVLSimulator Version 2021.1](https://github.com/lgsvl/simulator/releases/tag/2021.1)* with running *[Apollo 5.0](https://github.com/ApolloAuto/apollo/releases/tag/v5.0.0)* as the autonomous driving system.

### Installation
To view the requirement and installation procedure for running the toolset, please look at [toolset-installation](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-toolset#requirements).

### Usage
To see detailed instructions of using *ScenarioCollector* and *ScenarioRunner*, please look at [toolset-usage](https://github.com/Simula-COMPLEX/DeepScenario/blob/main/deepscenario-toolset/README.md#usage).

<!-- 
### Installation

### ScenarioCollector

### ScenarioRunner
-->
## Maintainers
[@ChengjieLu](https://github.com/chengjie-lu)
