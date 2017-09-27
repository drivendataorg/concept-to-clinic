# Alex |Andre |Gilberto |Shize algorithm

## Summary
The approach consists of 3D CNN data model which slide through the z coordinate of a CT volume, followed xgboost and extraTree models trained on different subsets of extracted features. 
by was custom built to reflect how radiologists review lung CT scans to diagnose cancer risk.  
![](https://preview.ibb.co/fUERDk/Screenshot_from_2017_09_27_01_11_49.png)
> A sliding 3D data model was custom built to reflect how radiologists review lung CT scans to diagnose cancer risk. As part of this data model - which allows for any nodule to be analyzed multiple times - a neural network nodule identifier has been implemented and trained using the Luna CT dataset. Non-traditional, unsegmented (i.e. full CT scans) were used for training, in order to ensure no nodules, in particular, those on the lung perimeter are missed.  

## Source

**Author:** Alexander Ryzhkov, Gilberto Titericz Junior, Andre, Shize Su </br>
**Repository:** [https://github.com/astoc/kaggle_dsb2017](https://github.com/astoc/kaggle_dsb2017)   </br>
The approach scored the 8th place at the Data Science Bowl 2017.  

## License
[MIT License](https://github.com/astoc/kaggle_dsb2017/blob/master/LICENSE)


## Prerequisites

<table>
  <thead>
    <tr>
      <th colspan="3">Andre</th>
      <th colspan="3">Shize</th>
    </tr>
    <tr>
      <th>Dependency</th> 
      <th>Name</th>
      <th>Version</th>
      <th>Dependency</th> 
      <th>Name</th>
      <th>Version</th>
    </tr>
  </thead>
  
  <tbody>
    <tr>
      <td>Language</td>
      <td>Python</td>
      <td>3.5</td>
      <td>Language</td>
      <td>Python</td>
      <td>2.7</td>
    </tr>
    <tr>
      <td>ML engine</td>
      <td>Keras</td>
      <td>1.2.2</td>
      <td>ML engine</td>
      <td>Keras</td>
      <td>1.2.2</td>
    </tr>
    <tr>
      <td>ML backend</td>
      <td>Theano</td>
      <td>0.8+</td>
      <td>ML backend</td>
      <td>Theano</td>
      <td></td>
    </tr>
    <tr>
      <td>OS</td>
      <td>PC Linux <br/>AWS Linux</td>
      <td><br/>P2</td>
      <td>OS</td>
      <td>AWS Linux</td>
      <td>C3.8</td>
    </tr>
    <tr>
      <td>Processor</td>
      <td>CPU</td>
      <td>PC i7<br/>P2 vCPU</td>
      <td>Processor</td>
      <td>CPU</td>
      <td>Intel Xeon</td>
    </tr>
    <tr>
      <td></td>
      <td>GPU</td>
      <td>PC NVIDIA 8GB<br/>P2 NVIDIA K80 12GB</td>
      <td></td>
      <td>GPU</td>
      <td>no</td>
    </tr>
    <tr>
      <td>GPU driver</td>
      <td>CUDA<br/>cuDNN</td>
      <td>7.5<br/>6.0</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </tbody>
</table>

Some of the cells' values were restored from the AWSs' setups and CUDA compatibility.

**Dependency packages:** Neither the repository nor the authors specified exact versions of the Python packages:


Andre         | Shize
--------------|---------------------------------
Keras 1.2.2   | numpy
Theano        | pandas
spyder        | xgboost
opencv        | scikit-learn
pydicom       |
scipy         |
scikit-image  |
SimpleITK     |
numpy         |
pandas        |

## Algorithm design


### Preprocessing
1. Resampling all patient CT scans to a relatively rough resolution of 2x2x2mm. 
2. CT voxels' values standardisation to Hounsfield scale. 
3. Lungs segmentation.

### Nodule detection
> Train a nodule identifier on a slicing architecture using Luna dataset and intermediate files created (3 options provided).  

The slicing architecture itself is made of UNets. One of the aforementioned options is also a good data augmentation method:  
> [..] Special mosaic-type aggregation of training of the nodule identifier has been deployed, as illustrated below.    

![](https://preview.ibb.co/ivOTtk/Screenshot_from_2017_09_27_01_35_56.png)

### Prediction of cancer probability
>The most important feature is the existence of nodule(s), followed by their size, location and their other characteristics. For instance, a very significant number of patients for which no nodule has been found, proved to be no cancer cases. [..] Key features include existence/size of the largest nodule, and its vertical location, existence of emphysema, volume of all nodules, and their diversity. 

The authors also have mentioned that the code location of nodules versus the segmented lungs centre of gravity as a feature provide higher significance in comparison with convenient upper/lower parts of lungs feature.   
>As outlined, our combined approach uses the neural network as a feature generator and then applying xgboost and extraTree models on the extracted features to generate predictions and submissions. To make the model performance more stable, we also run some of the models with multiple random seeds (e.g., for xgb, use 50 random runs; for extraTree, use 10 random runs) and take the average. Our final winning submission (private LB0.430) is a linear combination of a couple of xgb models and extraTree models.
## Trained model

**Source:** [nodule_identifiers](https://github.com/astoc/kaggle_dsb2017/blob/master/code/Andre/nodule_identifiers/d8_2x2x2_best_weights.h5) </br>

**Usage instructions:** [Shize algorithm](https://github.com/astoc/kaggle_dsb2017/blob/master/code/Shize/00ReadMe.txt), [Andre algorithm](https://github.com/astoc/kaggle_dsb2017/blob/master/code/Andre/ReadMe.txt) <br/>
## Model Performance

### Training- / prediction time

**Test system:**     </br>

| Component | Spec  | Count |
|-----------|-------|-------|
| CPU       | C3.8 Intel Xeon |       |
| GPU       | P2 NVIDIA K80 12GB |  >1   |
| RAM       |       |       |

**Training time:** days on AWS
>Training some of the nodule models took days using high end 12GB GPUs.</br>   

**Prediction time:** unknown, but must be less than 14 min per CT, since it processes the 506 CTs for the 5 days </br>

### Model Evaluation

**Dataset:** Data Science Bowl evaluation dataset  </br>

| Metric   | Score |
|----------|-------|
| Log Loss | 0.43019 |

## Use cases


### When to use this algorithm

 - The nodules detection system seems to be a good contribute to a concept-to-clinic's ensemble, by the reason listed in comments.

### When to avoid this algorithm

 - The nodules detection method provided by the authors requires inconvenient rough CT's spacing (`2x2x2mm`) which may conflict with other pipelines, if the high order interpolation polynomials will be employed then the additional spacing transaction may considerably affect on a computation time.
 - The training from scratch, as it was mentioned by the authors, for only one of the sliding architectures may take days even over AWS P2 equipped by NVIDIA K80 12GB GPUs.
 
## Adaptation into Concept To Clinic

### Porting to Python 3.5+
The Andre part had been already written in python 3.5. However Shize used the python 2. The main difficulties seems to be the lack of specified versions for the packages employed by Shize. Nonetheless, Shize's part consists merely of ensembling already extracted features via xgboost and extraTree models, and GPUs are not required. 

### Porting to run on CPU and GPU
The noodles detector written on `Keras` with `Theano` as the backend, thus it shall run on CPU out of the box.

### Improvements on the code base


### Adapting the model
Worth noting that simpler model consisted only of a [single xgb](https://github.com/astoc/kaggle_dsb2017/blob/master/code/Shize/0Shize_DSB_feat3_xgb_v5.py) has performed similarly (0.434 on private LB). Thus it will be better to drop away the cumbersome combination of different xgb and extraTree models , and some of them were using averaged prediction from 50 or 10 random
runs (i.e., using 50 (or 10) different random seeds)

## Comments
The whole pipeline relies on the nodules detector, and at the same time the approach has reached 8th place on the DSB17 private LB,  it's worth to admire that method then and consider it into account. Moreover, the authors stated that they didn't use the information relative nodule malignancy as they've incorrectly assumed it's unavailable, therefore training the model from scratch or fine tune it over the data within malignancy status seems to be beneficial. 

## References
Repository: https://github.com/astoc/kaggle_dsb2017  
Technical Report: https://github.com/astoc/kaggle_dsb2017/blob/master/Solution_description_DSB2017_8th_place.pdf  
Luna16 dataset: https://luna16.grand-challenge.org/home/  