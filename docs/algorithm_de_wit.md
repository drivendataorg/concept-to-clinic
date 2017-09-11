# Julian de Wit Algorithm

## Summary
The algorithm stands out with the idea to pre-detect strange tissue, estimate the malignancy of the nodules using a [C3D](http://vlg.cs.dartmouth.edu/c3d/) network and predict the cancer probability using XGBoost and some other features.
 It is combined with the algorithm by Daniel Hammack at the prediction level.

## Source
**Author:** Julian de Wit  
**Repository:** https://github.com/juliandewit/kaggle_ndsb2017  
2nd place at the Data Science Bowl 2017 together with the algorithm by Hammack

## License
MIT


## Prerequisites
| Dependency |   Name   | Version  |
|------------|----------|----------|
| Language   | Python   | 3.5 |
| ML engine  | Keras    | 2.0.8 |
| ML backend | Tensorflow| 1.3.0 |
| OS         | Windows/Ubuntu |64 Bit|
| Processor  | CPU      | yes  |
|            | GPU      | yes |
| GPU driver | CUDA     | 8.0 |
|            | cuDNN    | 6.0 |

**Dependency packages:**
````
beautifulsoup4==4.6.0
lxml==3.8.0
numpy==1.13.1
pandas==0.20.3
scipy==0.19.1
scikit-learn==0.19.0
scikit-image==0.13.0
tensorflow-gpu==1.3.0
Keras==2.0.8
xgboost==0.6a2
opencv-python==3.3.0.10
pydicom==0.9.9
SimpleITK==1.0.1
````

## Algorithm design
![](http://juliandewit.github.io/images/plan2017_2.png)

### Preprocessing
Every scan was rescaled so that every voxel represented a volume of 1x1x1 mm.
Next, the pixel intensities were clipped to the minimum and maximum of the interesting Hounsfield Units.
Then, they were scaled between 0 and 1.
Lastly, the author ensured that all the scans have the same orientation.


### Strange tissue detection
The author used a C3D network with an input of 32x32x32 mm which is a receptive field that is 8 times smaller than the one of Hammack.
This way it is much lighter and more diverse with respect to the used architecture of Hammack.
![](http://juliandewit.github.io/images/network_table.png)

### Prediction of cancer probability
The author states:
```
In the end I only used 7 features for the gradient booster to train upon.
These were the maximum malignancy nodule and its Z location for all 3 scales and the amount of strange tissue.
```


## Trained model

**Source:** https://retinopaty.blob.core.windows.net/ndsb3/trained_models.rar  

**Usage instructions:**  
```
[...] The models are placed in the ./models/ directory.
From there the nodule detector step3_predict_nodules.py can be run to detect nodules in a 3d grid per patient.
The detected nodules and predicted malignancy are stored per patient in a separate directory.
The masses detector is already run through the step2_train_mass_segmenter.py and will stored a csv with estimated masses per patient.
```

## Model Performance

### Training- / prediction time
Unfortunately, neither the blog entry nor the readme mention the system that was used for training and testing.  
**Test system:**

| Component | Spec  | Count |
|-----------|-------|-------|
| CPU       |       |       |
| GPU       |       |       |
| RAM       |       |       |

**Training time:**  10 hours per 3D ConvNet  
**Prediction time:** unknown  

### Model Evaluation

**Dataset:** Data Science Bowl 2017  

| Metric   | Score |
|----------|-------|
| Log-Loss |0.40117|

## Use cases

### When to use this algorithm

 - when we don't want to port the code (as it is already written for Python 3)
 - when we don't want to train the models (as they are downloadable)

### When to avoid this algorithm

 - It's unclear how well the algorithm performs without being ensembled with the solution of Hammack - especially since its respective field is 8 times smaller than the one of Hammack. Also, the author already mentions himself that the network architecture still needs finer tuning.

## Adaptation into Concept To Clinic

### Porting to Python 3.5+
It's already written to run with Python 3.

### Porting to run on CPU and GPU
It is possible to make Tensorflow use the CPU instead of the GPU.

### Improvements on the code base
The author states that he did not clean up the complete repository to keep its reproducibility. It might make sense to contact the author to task for further suggestions for the clean up.

### Adapting the model
The author suggests to play around with the architecture of the CNNs since he put very few time in that, although the architecture of a neural network is a critical factor of its performance.


## Comments
The differences between the two approaches of Hammack and de Wit can be seen in the following table:
![](http://juliandewit.github.io/images/julian_daniel.png)


## References
[Report](http://juliandewit.github.io/kaggle-ndsb2017/)  
[Code](https://github.com/juliandewit/kaggle_ndsb2017)
