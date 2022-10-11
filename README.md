# Environment_Prediction : package containing the modules, tools and scripts use for Environment Prediction research. 

## Overview

The Environment Prediction research is running by ROB-TAU research team in collaboration with [ReWalk Robotics](https://rewalk.com/)  
as a part of the HRI collection of researches. 

To be continue... the aim of the research and what is included.. bla bla .. 

## Installation
Clone the repository:

```bash
git clone git@github.com/nimiCurtis/Environment_Prediction.git
cd Environment_Prediction
```
NOTE: using a virtual environment is recommended for the installation of the requiered packages 

The requiements are seperated for the Jetson Nano requierments as the data collector and actual tool for implement the trained models, and for the processing requierments which recomended to be install on PC for better computational capabilities such as DL/ML models training (will build in the future).  

You can install them by:

```bash
pip install -r requirements/jetson_requirements.txt
```

Finally for using the ZED camera SDK of stereolabs you must download the SDK properly.
Therefore you should follow the SDK installation process for PC/nvidia_jetson.

See: [Download and Install the ZED SDK](https://www.stereolabs.com/docs/installation/jetson/).


## Content

The pacakge contains several folder:

- [conf](/conf): contains ```recorder.yaml```  and ```zedm.yaml``` with the relevant parameters. 
- [dataset](/dataset/): contains the saved dataset folders 
- [examples](/examples/): contains several testing scripts
- [modules](/modules/): contains the ZED and RECORDER classes
- [requierments](/requierments/): contains the requierments got from: 
    ```bash
    pip freeze
    ```

## Hardware and System architecture

TBD

## Usage 

TBD

## Helpful Links
To be continue .. 
- [ZED git python API](https://github.com/stereolabs/zed-python-api)
- [ZED API Documentation](https://www.stereolabs.com/docs/api/)
- [ZED examples](https://github.com/stereolabs/zed-examples)




