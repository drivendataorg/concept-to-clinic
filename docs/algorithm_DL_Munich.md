# DL Munich

## Summary
**Author:** [Niklas Köhler](https://www.kaggle.com/niklaskoehler), [Alex Wolf](https://www.kaggle.com/falexwolf), [Mo](https://www.kaggle.com/m2dao2dar), [Julian Jungwirth](https://www.kaggle.com/julianjungwirth)     </br>
**Repository:**  https://github.com/NDKoehler/DataScienceBowl2017_7th_place   </br>
The 7th place at the Data Science Bowl 2017 on the private leaderboard.

## License
[MIT License](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/blob/master/LICENCE)


## Prerequisites

| Dependency |   Name   | Version  |
|------------|----------|----------|
| Language   | Python   | 3.4.3    | 
| ML engine  |          |          | 
| ML backend | Tensorflow | 1.0.1  | 
| OS         | Ubuntu   | 14.04    | 
| Processor  | CPU      | Intel(R) Core(TM) i7-4930K CPU |
|            | GPU      | Nvidia GTX 1080 |
| GPU driver | CUDA     | 8.0      |
|            | cuDNN    | 5.1      |


**Dependency packages:**
```
opencv-python==3.2.0.6
Python 3.4.3
dicom==0.9.9-1
joblib==0.10.3
tensorflow-gpu==1.0.1
SimpleITK==0.10.0.0
numpy==1.12.0
pandas==0.19.2
scipy==0.18.1
scikit-image==0.12.3
scikit-learn==0.18.1
```


## Algorithm design


### Preprocessing
1. Resampling to the isotropic resolution of ![equation](http://latex.codecogs.com/gif.latex?%5Cdpi%7B80%7D%201%5Ctimes1%5Ctimes1%5C%3Amm%5E3%20/%20px%5E3).
2. Segment the lungs on the resampled CT scan via a lung segmentation neural network, trained with around 150 manually annotated lung wings.  
2. Crop CT scan by the minimal cube which will fits the lungs.  
  
![](https://preview.ibb.co/gcHAQb/Screenshot_from_2017_09_28_19_12_11.png)



### Nodule detection
#### Training  
In objective to segment lung nodules 5-channel [UNet](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/blob/master/dsb3_networks/nodule_segmentation/tf_scripts/architecture/model_def/unet_graph2D3D.py) architecture with ![](http://latex.codecogs.com/gif.latex?%5Cdpi%7B80%7D%205%5Ctimes128%5Ctimes128%5C%3Apx%5E2) receptive field has been employed. The model has been trained over the LUNA|LIDC dataset. A random crop of lung slices sampled randomly from all 3 room axis (not only axial) along with four adjacent 
slices (+2/-2) were feded into the network as an input, the corresponding elliptical nodule annotation mask for the central slice was used as a target output. Training data was made of exclusively croped slices which contain a nodule annotation and 15 random negative slices for each room axis from each patient scan, which do not contain any nodule annotation. Finally, a training batch consists of 30 random nodule sectioning slices and 2 random negative slices.   
  
![](https://preview.ibb.co/e4Bekb/Screenshot_from_2017_09_28_19_16_12.png)  


#### Prediction  

The trained segmentation network has been applied to all slices of a CT scann from all 3 room axis. This results in three 3D
probability maps which has been be averaged. This final 3D probability map tensor was the basis for the candidate proposal clustering.

![](https://preview.ibb.co/bZis5b/Screenshot_from_2017_09_28_19_16_49.png)  

#### Candidate proposal clustering

Regions in the probability map tensor that have a high probability for being nodules have been identified using [DBSCAN](https://en.wikipedia.org/wiki/DBSCAN). The [sklearn.cluster.DBSCAN](http://scikit-learn.org/stable/modules/clustering.html#dbscan) implementation has been used. 

>We chose a relatively low threshold on the probability map to generate an input for DBSCAN and deal with the high number of proposed regions that results from this in two ways.  
>1. Regions that are too large to be processed in the later stage of cancer classification are again clustered with a threshold just sufficiently high for producing small enough candidates. 
>2. Proposed regions are sorted according to a score compute as the sum over the m highest pixel values in the region, where m is approximately the number of pixels in the smallest annotated nodule.

The resulting cluster centers are used to crop candidates from the original data in ![0.5×0.5×0.5](http://latex.codecogs.com/gif.latex?%5Cdpi%7B80%7D%200.5%20%5Ctimes0.5%5Ctimes0.5%5C%3A%20mm%5E3%20/%20px%5E3) and ![0.7×0.7×0.7](http://latex.codecogs.com/gif.latex?%5Cdpi%7B80%7D%200.7%20%5Ctimes0.7%5Ctimes0.7%5C%3A%20mm%5E3%20/%20px%5E3) resolutions.


### Prediction of cancer probability
>The cancer classification network uses multiple candidates from the candidate proposal steps as input and predicts a single cancer probability for each patient. From 5 to 20 candidates per patient has been used. Additionally to the pixel information from the lung CT-scan we include the nodule probability map information from the segmentation network in a second input channel. Therefore, the classifier maps a tensor of shape (C,64,64,64,2), where C = 10 is the number of candidates, to a single output probability. The classifier is either a 3D residual convolution network of an 2D residual convolution network. In the case of 3D classifier each candidate is represented by the full (64,64,64,2) tensor. In the case of the 2D classifier each candidate is presented as the 3 center slices from all 3 room axis. The package of these three layers then is treated by the network as a multichannel input (no weight-sharing for different axis).  

>When applied to a single candidate the 3D residual core model reduces the candidate tensor from (64,64,64,2) pixels to an (8,8,8,128) feature map, by applying multiple stacked convolution and pooling layers (details in code). We reduce this final feature tensor with shape (8,8,8,128) with an 1x1 convolution layer with a single kernel to (8,8,8,1). A final global average pooling followed by a sigmoidal activation function reduces this map to the single final output. We apply this residual core model to all candidates of a patient simultaneously and share the weight in the candidate dimension. When applying the core-module to a multi-candidate input with shape (C,64,64,64,2) we arrive at an (C, 1) output tensor. We then apply a reduction function (max) to this tensor in the second dimension to obtain a single value. The entire graph is schematically shown for the 2D case in figure:  

![](https://preview.ibb.co/kBTgyw/Screenshot_from_2017_09_28_19_17_15.png)  


### Final Ensemble
For the final solution four different Patient-Classifier-Networks have been employed, the outputs of which were averaged to a single prediction. 

| Network | isotropic scan resolution | architecture | 
|-------------|-----|---------------------|
| 05res 3DNet | 0.5 | 3D residual network |
| 07res 3DNet | 0.7 | 3D residual network |
| 05res 2DNet | 0.5 | 2D residual network |
| 07res 2DNet | 0.7 | 2D residual network |

## Trained model

**Source:** seems that it's no access to the trained models. @reubano has opend an [issue](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/issues/1) at the 3rd of July but there's no responce.  </br>

**Usage instructions:**  [README](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/blob/master/README.md)   </br>

## Model Performance

### Training- / prediction time

**Test system:**     </br>

| Component | Spec  | Count | 
|-----------|-------|-------|
| CPU       | Intel(R) Core(TM) i7-4930K CPU |       |
| GPU       | Nvidia GTX 1080 |       |
| RAM       | 32GB  |       |
|           | 200GB |       |

**Training time:**  from the [training log](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/blob/5ff69f779ddbb1a3bf46f04b2312d4418c0ba6d2/dsb3_networks/classification/luna_resnet3D/output_dir/luna3D/all.log) it seems that one 3D resnet model requires 13 epochs with average 750s per epoch. For the 2D resnet from the coresponding [train log](https://raw.githubusercontent.com/NDKoehler/DataScienceBowl2017_7th_place/5ff69f779ddbb1a3bf46f04b2312d4418c0ba6d2/dsb3_networks/classification/luna_resnet2D/output_dir/gold_prio3_plane_mil0/all.log) folloed that the authors train the model over 17 epochs with the average 150s per epoch. Taking into account that there're two classification models of each type the resulting training time of the classification part will consume about 7 hours. </br>
**Prediction time:** unknown, but must be less than 14 min per CT, since it processes the 506 CTs for the 5 days </br>

### Model Evaluation

**Dataset:**  Data Science Bowl evaluation dataset </br>

| Metric   | Score |
|----------|-------|
| Log Loss | 0.42751 |

## Use cases


### When to use this algorithm

 - For the nodules candidates detection and segmentation, also in combination with the Alex | Andre | Gilberto | Shize segmentation algorithm.  
 - As a part of classification batch, may be used only one architecture out of four.

### When to avoid this algorithm

 - If there's is no GPU support it may consume a huge amount of time. Also the isotropic scan spacings which was used at classification stage are not common, this will lead to additional time consumption caused by resizing.  
 
## Adaptation into Concept To Clinic

### Porting to Python 3.5+
The solution is already compatible with Python 3.5+

### Porting to run on CPU and GPU
The approach consists of four deep 3D / 2D residual networks for classification (which runs through each candidate from a CT scan) and two 3D2D Unet models for nodules and lungs segmentation. It'll require a huge amount of time to even predict with this pipeline using CPU only.

### Improvements on the code base
Since the objective of the DSB17 was to guess whether the patient has canser or not, the approach of DL Munich doesn't provide any information for each nodule, but only for a candidates set. It'll be beneficial for the concept-to-clinic to recieve the information for each candidate respectively. It can be done merely by extracting values from before the `max` operator. 

### Adapting the model

## Comments
The algorithm of nodules segmentation is well generalised and may be integrated with the Alex | Andre | Gilberto | Shize segmentation algorithm. Since the main motivation for four architectures was the generalization then if will be used in combination with other approaches it seems to be beneficial to use only one (or two: 3D and 2D) out of four.

## References
[DL Munich description](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/blob/master/documentation/DL_Munich_model_desc.pdf)  
[README](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/blob/master/README.md)
