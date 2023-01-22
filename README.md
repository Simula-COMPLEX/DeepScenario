[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
# DeepScenario: An Open Driving Scenario Dataset for Autonomous Driving System Testing

> **Dataset avaliability** - To facilitate reviewing *DeepScenario* dataset, reviewers please refer to the corresponding data in this repository. We also plan to release the dataset in permanent repositories like Zenodo once it gets accepted.<br/>

This repoisitory contains:

1. **[deepscenario-dataset](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-dataset)** - Scenarios 
2. **[deepscenario-toolset](https://github.com/Simula-COMPLEX/DeepScenario/tree/main/deepscenario-toolset)** - 

## Table of Contents
- [Contributions](#contributions)
- [Overview of Scenario](#overview-of-deepcollision)
- [DeepCollision Environment Configuration API](#deepCollision-environment-configuration-api)
  - [REST API List](#rest-api-list)
  - [Usage](#usage)
- [Related Efforts](#related-efforts)
- [Paper](#paper)
- [Maintainers](#maintainers)

## Contributions
With the rapid development of autonomous driving systems (ADSs), testing ADSs under various driving conditions has become a key method to ensure the successful deployment of ADS in the real-world. However, it is impossible to test all the scenarios due to the inherent complexity and uncertainty of ADSs and the driving tasks. Further, testing of ADSs is expensive regarding time and computational resources. Therefore, a large-scale driving scenario dataset consisting of various driving conditions is needed. To this end, we present an open driving scenario dataset \deepscenario, containing over 30\textit{K} \textit{executable} driving scenarios, which are collected by 2880 test executions of three driving scenario generation strategies. Each scenario in the dataset is labeled with six attributes characterizing test results. We further show the attribute statistics and distribution of driving scenarios. For example, there are 1050 collision scenarios, in 917 scenarios there were collisions with other vehicles, 105 and 28 with pedestrians and static obstacles, respectively.

![image](https://github.com/Simula-COMPLEX/DeepScenario/blob/main/figures/dataset-generation-overview.png)

