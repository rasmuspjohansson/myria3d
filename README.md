<div align="center">

# Myria3D: Aerial Lidar HD Semantic Segmentation with Deep Learning


<a href="https://pytorch.org/get-started/locally/"><img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white"></a>
<a href="https://pytorchlightning.ai/"><img alt="Lightning" src="https://img.shields.io/badge/-Lightning-792ee5?logo=pytorchlightning&logoColor=white"></a>
<a href="https://hydra.cc/"><img alt="Config: Hydra" src="https://img.shields.io/badge/Config-Hydra-89b8cd"></a>

[![](https://shields.io/badge/-Lightning--Hydra--Template-017F2F?style=flat&logo=github&labelColor=303030)](https://github.com/ashleve/lightning-hydra-template)

[![CICD](https://github.com/IGNF/myria3d/actions/workflows/cicd.yaml/badge.svg)](https://github.com/IGNF/myria3d/actions/workflows/cicd.yaml)
[![Documentation Build](https://github.com/IGNF/myria3d/actions/workflows/gh-pages.yml/badge.svg)](https://github.com/IGNF/myria3d/actions/workflows/gh-pages.yml)
</div>
<br><br>


Myria3D is a deep learning library designed with a focused scope: the multiclass semantic segmentation of large scale, high density aerial Lidar points cloud.

The library implements the training of 3D Segmentation neural networks, with optimized data-processing and evaluation logics at fit time. Inference on unseen, large scale point cloud is also supported.
It allows for the evaluation of single-class IoU on the full point cloud, which results in reliable model evaluation.

Myria3D is built upon [PyTorch](https://pytorch.org/). It keeps the standard data format 
from [Pytorch-Geometric](https://pytorch-geometric.readthedocs.io/). 
Its structure was bootstraped from [this code template](https://github.com/ashleve/lightning-hydra-template),
which heavily relies on [Hydra](https://hydra.cc/) and [Pytorch-Lightning](https://github.com/PyTorchLightning/pytorch-lightning) to enable flexible and rapid iterations of deep learning experiments.

Although the library can be extended with new neural network architectures or new data signatures, it makes some opiniated choices in terms of neural network architecture, data processing logics, and inference logic. Indeed, it is initially built with the [French "Lidar HD" project](https://geoservices.ign.fr/lidarhd) in mind, with the ambition to map France in 3D with 10 pulse/m² aerial Lidar by 2025. The data will be openly available, including a semantic segmentation with a minimal number of classes: ground, vegetation, buildings, vehicles, bridges, others. 

> &rarr; For installation and usage, please refer to [**Documentation**](https://ignf.github.io/myria3d/).

> &rarr; A stable, production-ready version of Myria3D is tracked by a [Production Release](https://github.com/IGNF/myria3d/releases/tag/prod-release-tag). In the release's assets are a trained multiclass segmentation model as well as the necessary configuration file to perform inference on French "Lidar HD" data. Those assets are provided for convenience, and are subject to change in time to reflect latest model training.
___


#usage at KDS instructions 
```
In this example a KDS .laz file is colorized with RGBNir data from ortofoto (better to use the real values)
this file is used for configuration of the Myria3D classifier: trained_model_assets/proto151_V2.0_epoch_100_Myria3DV3.1.0_predict_config_V3.7.0.yaml
in this .yml file the model to use is defined (trained_model_assets/proto151_V2.0_epoch_100_Myria3DV3.1.0.ckpt) as well as what .laz file to classify (/mnt/T/mnt/trainingdata/lidar/test_data/rgbNir_colorized_myria_input/colorized.laz) and what pretrained model to use:(trained_model_assets/proto151_V2.0_epoch_100_Myria3DV3.1.0.ckpt)  
In order to visualize the resulting classifications in qgis the resulting -laz file is read by read_and_write_laz.py and saved in a format that qgis can read

python add_rgbnir_to_laz.py --laz_file /mnt/T/mnt/trainingdata/lidar/test_data/splitted_laz/split_1.laz --raster /mnt/T/mnt/trainingdata/lidar/test_data/2024_1km_6179_723.tif --output_laz /mnt/T/mnt/trainingdata/lidar/test_data/rgbNir_colorized_myria_input/colorized.laz
python run.py task.task_name=predict
python read_and_write_laz.py --input_laz /mnt/T/mnt/trainingdata/lidar/test_data/myria_output/colorized.laz --output_laz /mnt/T/mnt/trainingdata/lidar/test_data/cleaned_up_myria_output/cleaned_up_colorized.laz


PROBLEMS and TODO:
The result of the above comands is a classification that seem to work as it should but is having some related to teh 50x50 meter receptive field size. There is a clear 'checker box pattern' and a lkot of things are incorectly classified as water . 

Potential fixes: 1. make the receptive field larger 2. investigate if we can use overlaps? 3. create our own trainingdata and finetune the model to our data 4. we can then also introduce more classes (e.g cars)
e.g python run.py task.task_name=predict predict.subtile_overlap=25
```
___


Please cite Myria3D if it helped your own research. Here is an example BibTex entry:
```
@misc{gaydon2022myria3d,
  title={Myria3D: Deep Learning for the Semantic Segmentation of Aerial Lidar Point Clouds},
  url={https://github.com/IGNF/myria3d},
  author={Charles Gaydon},
  year={2022},
  note={IGN (French Mapping Agency)},
}
```
