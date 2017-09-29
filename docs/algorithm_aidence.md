# Aidence

## Summary
**Author:** [Tim Salimans](https://www.kaggle.com/timsalimans), [Mark-Jan Harte](https://www.kaggle.com/markjan), [Gerben van Veenendaal](https://www.kaggle.com/gerbenvv)  </br>
**Repository:**  https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294?at=master   </br>
The 3rd place at the Data Science Bowl 2017 on the private leaderboard.

## License 
[GNU GENERAL PUBLIC LICENSE](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294c17f833e56379cc493ecfe48304a/COPYING.txt?at=master&fileviewer=file-view-default)  
[Copyright (C) 2017 Aidence B.V.](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294?at=master)  


## Prerequisites

| Dependency |   Name   | Version  |
|------------|----------|----------|
| Language   | Python   | 3.4      |
| ML engine  |          |          |
| ML backend | Tensorflow | 1.1    |
| OS         |          |          |
| Processor  | CPU      | yes      |
|            | GPU      | Nvidia K80 |
| GPU driver | CUDA     | 8.0      |
|            | cuDNN    | 6.0      |


**Dependency packages:**
```
tensorflow==1.1
opencv>=3.1
scipy==0.17.0
numpy==1.13
scikit-learn==0.19.0
pydicom==0.9.9
SimpleITK==1.0.1
pandas==0.20.3
pycuda==2017.1.1
```


## Algorithm design


### Preprocessing
Resampling to the isotropic resolutions of ![equation](http://latex.codecogs.com/gif.latex?%5Cdpi%7B80%7D%202.5%5Ctimes0.512%5Ctimes0.512%20mm%5E3/px%5E3) and ![equation](http://latex.codecogs.com/gif.latex?%5Cdpi%7B80%7D%201.25%5Ctimes0.5%5Ctimes0.5%20mm%5E3/px%5E3) for the final model.

### Nodule detection
Fully convolutional Resnet has been employed in order to detect for each pixel whether it is contained in the center of a nodule. It was trained it over the LIDC/IDRI dataset. Two of those models has been trained: one for normal sized nodules and one for masses. The masses on the train data of Kaggle have been annotated and the mass network has been trained on both masses from LIDC/IDRI as well as masses from Kaggle. Takes the logit output of that network for the whole volume and thresholds it to determine candidates. It also masks out nodules outside the lung.

### Prediction of cancer probability
Takes the candidates and trains some attributes of the LIDC dataset (malignancy, etc.) and trains the cancer label for the Kaggle scans in a multi-task model.

## Trained model

**Source:** From the [issue description](https://github.com/concept-to-clinic/concept-to-clinic/issues/21) followed that the trained model is already requested.  </br>
There are two `.pkl` models in [localization](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294c17f833e56379cc493ecfe48304a/models-ours/localization/models/model-45000.pkl?at=master) and [localization-large](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294c17f833e56379cc493ecfe48304a/models-ours/localization-large/models/model-60000.pkl?at=master)

**Usage instructions:**  [README](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294c17f833e56379cc493ecfe48304a/run.txt?at=master&fileviewer=file-view-default)   </br>

## Model Performance

### Training- / prediction time

**Test system:**     </br>

| Component | Spec  | Count | 
|-----------|-------|-------|
| CPU       |       |       |
| GPU       | Nvidia K80 | 4 for everything but the final model <br/> 8 for the final model  |
| RAM       |       |       |


**Training time:** 
>It takes about 3-5 days to run everything (infer+train) on a decent machine with 8 GPUs. </br>  
**Prediction time:**  
unknown, but must be less than 14 min per CT, since it processes the 506 CTs for the 5 days </br>

### Model Evaluation

**Dataset:**  Data Science Bowl evaluation dataset </br>

| Metric   | Score |
|----------|-------|
| Log Loss | 0.40127 |

## Use cases


### When to use this algorithm

 - The annotation for the mass and nodules over the Kaggle dataset, provided by the aidence team, can be used in futher fine-tunings / retrainings.
 
### When to avoid this algorithm

 - even with GPU support the approach of per voxel examination may consume a huge amount of time. The authors have used 8 GPUs Nvidia K80 which is 
 
## Adaptation into Concept To Clinic

### Porting to Python 3.5+
The solution is already compatible with Python 3.5+

### Porting to run on CPU and GPU
The approach consists of two deep 3D residual networks for classification (which runs through each `voxel` from a CT scan). It'll require a huge amount of time to even predict with this pipeline using CPU only.

### Improvements on the code base
The code itself looks good to me.

### Adapting the model

## Comments
The major benefits for the concept-to-clinic from the aidence approach will be to include provided mass- ans nodule- annotations over the Kaggle dataset into the overall dataset for further retraining other models on it. 

## References
[Aidence algorithm](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294?at=master)  
[README](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294c17f833e56379cc493ecfe48304a/README.md?at=master)
[Mass-annotations](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294c17f833e56379cc493ecfe48304a/original-datasets/kaggle/mass-annotations.pkl?at=master) over Kaggle data.
[Nodule-annotations](https://bitbucket.org/aidence/kaggle-data-science-bowl-2017/src/38c4f2f67294c17f833e56379cc493ecfe48304a/original-datasets/kaggle/nodule-annotations.pkl?at=master) over Kaggle data.
