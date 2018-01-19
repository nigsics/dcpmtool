# dcpmtool
The project dcpmtool (Dynamic Control Plane Management tool) is related to the paper

```
Shaoteng Liu, Rebecca Steinart and Dejan Kostic, "Flexible deployment of control plane",  IEEE NoMs 2018.
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

1. Python 2.7 is required.
2. clone the project

```
git clone https://github.com/nigsics/dcpmtool.git {Your folder}
```

### Installing
1. Install python package networkx. See
```
   https://networkx.github.io/documentation/networkx-1.10/install.html
```
2. Install python package pandas. See
```
   https://pandas.pydata.org/pandas-docs/stable/install.html
```
## Running the tool
   
### Prepare the topology description file
  The topology of a network is described in graphml format (http://graphml.graphdrawing.org/).  Examples can be find in the folder annotated_topo/

### Run a test 
1. Configure a test.

   Open placement_alg/run.config and modify the parameters 
```
resultpath : the path for storing the result files.
topopath   : the path for finding the network topology description file.
topoloogy  : the name of the network topology description file used in the test.
linkbandwidth : the list of link bandwidths to be tested.

```

2. Run a test.

In folder placement_alg/, open a terminal and run
```
python run_bd_scale_test.py
```

The service reliability under different link bandwidths can be find in {resultpath}/ folder. 


3. Display the results

In folder graphes/, open a terminal and run

```
python draw_colour_coded.py
```

Several graphes will be generated. The graphes named with the format "{topology}_{bandwidth}" describe the corresponding deployment plans of control instances (red nodes) under different link bandwidth settings. 
The graph named with the format "{topology}__scale_up" shows the achieved failure probability (failure probability = service reliability) corresponding to the link bandwidths.

 

## License

This project is licensed under the Apache 2 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
Thanks to the authors Shaoteng Liu, Rebecca Steinart and Dejan Kostic. This project was funded in part by the Swedish Foundation for Strategic Research (reference number RIT15-0075) and by the Commission of the European Union in terms of the 5G-PPP COHERENT project (Grant Agreement No. 671639).



