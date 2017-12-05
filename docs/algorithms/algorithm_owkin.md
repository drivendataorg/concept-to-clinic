# Owkin Algorithm

## Summary
The algorithm ensembles an approach that uses 3 U-Nets and 45 engineered features (1) and a 3D VGG derivative (2).
The cancer probability is predicted by both approaches using XGBoost and in the end ensembled using the average.

## Source
**Author:** [owkin (Pierre)](https://github.com/owkin/) and [Simon Jegou](https://github.com/SimJeg)  
**Repository:** [https://github.com/owkin/DSB2017](https://github.com/owkin/DSB2017)  
The approach scored 10th place at the Data Science Bowl 2017.

## License
The repository doesn't mention a license but since the authors had to accept the [Data Science Bowl rules](https://www.kaggle.com/c/data-science-bowl-2017/rules), the code must be published under [MIT](http://opensource.org/licenses/MIT) license.

## Prerequisites

```eval_rst
+------------+------------+----------+
| Dependency |   Name     | Version  |
+============+============+==========+
| Language   | Python     |    2.7   |
+------------+------------+----------+
| ML engine  |  Keras     |    2     |
+------------+------------+----------+
| ML backend | Tensorflow | 1        |
+------------+------------+----------+
| OS         |            |          |
+------------+------------+----------+
| Processor  | CPU        | (yes)    |
+------------+------------+----------+
|            | GPU        | yes      |
+------------+------------+----------+
| GPU driver | CUDA       |          |
+------------+------------+----------+
|            | cuDNN      |          |
+------------+------------+----------+
```

**Dependency packages:**

```python
tensorflow-gpu
keras
SimpleITK
pandas
pyidcom
h5py
opencv-python
radiomics
xgboost
```


## Algorithm design
Approach 1 uses 3 U-Nets which are structured as follows:  
![U-Net X](https://user-images.githubusercontent.com/6676439/30765249-08a9966c-9fef-11e7-9c2f-2718ad3aea0f.png)  

Approach 2 in turn uses a 3D VGG derivative that predicts 11 output variables:  
![3D VGG](https://user-images.githubusercontent.com/6676439/30765243-041f83ea-9fef-11e7-9a70-94db47159bea.png)

### Preprocessing
Approach 1 normalizes the Hounsfield values and then uses k-means clustering with k=2.  
Approach 2 segments the lung using Hounsfield units and fills the lung structures that is according to the author superior to morphological closing.

### Nodule detection
Approach 1 applies `a U-Net to each slice in direction X, Y or Z to output a mask with the same shape where the 1s represent the nodules detected by the Unet`.
A custom loss functions has been used to train the U-Nets (the Dice coefficient).
It `appl[ies] these U-Net on all the slices to obtain 6 different 3D binary segmentation masks of the detected nodules (directions X, Y, Z + unions I1, I2 and I3)`  
Approach 2 passes 64x64x64 cubes of the patient's scan to the 3D VGG model, which predicts 11 features in turn.

### Prediction of cancer probability
Approach 1 `extract[s] the 10 biggest nodules and compute[s] 45 features for each nodule (including location, area, volume, HU statistics etc.).`
These 450 features are then passed to a XGBoost classifier whereupon the 6 predictions are then averaged.  
Approach 2 passes the predicted features to a XGBoost classifier as well.

## Trained model

**Source:**  
- Approach 1: https://github.com/owkin/DSB2017/blob/master/sje_scripts/Unet_{X,Y,Z}.hdf5
-  Approach 2: https://github.com/owkin/DSB2017/blob/master/pic_scripts/model64x64x64_v5_rotate_v2.h5  

**Usage instructions:**  
```
#Create train features with patch model (Pierre's model)
cd ./pic_scripts/
python kaggle_script_features_patch.py -i /XXX/train/ -o /tmp/patch_model_features_train.csv

#Create train features with unet+radiomics (Simon's model)
cd ./../sje_scripts/
python kaggle_script_features_unet.py -i /XXX/train/ -o /tmp/unet_features_train.npz

#Create test features with patch model (Pierre's model)
cd ./../pic_scripts/
python kaggle_script_features_patch.py -i /XXX/test/ -o /tmp/patch_model_features_test.csv

#Create test features with unet+radiomics (Simon's model)
cd ./../sje_scripts/
python kaggle_script_features_unet.py -i /XXX/test/ -o /tmp/unet_features_test.npz

#Build xgbmodel from train features
cd ./../pic_scripts/
python kaggle_train.py -p /tmp/patch_model_features_train.csv -u /tmp/unet_features_train.npz -l /fusionio/KaggleBowl/stage1_labels.csv -s /tmp/model.bst

#Prediction from test features
python kaggle_predict.py -p /tmp/patch_model_features_test.csv -u /tmp/unet_features_test.npz -l /fusionio/KaggleBowl/sample_submission.csv -s /tmp/model.bst -f /tmp/sub_final.csv
```

## Model Performance

### Training- / prediction time

**Test system:**  Unknown

```eval_rst
+-----------+-------+-------+
| Component | Spec  | Count |
+===========+=======+=======+
| CPU       |       |       |
+-----------+-------+-------+
| GPU       |       |       |
+-----------+-------+-------+
| RAM       |       |       |
+-----------+-------+-------+
```

**Training time:**  Unknown  
**Prediction time:** 3 min per Patient for approach 1

### Model Evaluation

**Dataset:**
Data Science Bowl evaluation dataset

```eval_rst
+----------+--------+
| Metric   | Score  |
+==========+========+
| Log Loss | 0.44068|
+----------+--------+
```

## Use cases


### When to use this algorithm

 - if you want to use other lung segmentation methods than Hounsfield Unit clipping since the presented approaches also use morphologic features, filling and clustering

### When to avoid this algorithm

 - if a GPU us not available or the memory is very limited (8 million parameters per U-Net)

## Adaptation into Concept To Clinic
Since I was lacking the training data and CUDA, I was not able to completely run the scripts.

### Porting to Python 3.5+
Porting it to Python 3.5 should be as easy as running `2to3`.
After adapting `print` statements to Python 3, I was able to start all scripts without import errors, deprecation warnings or the like.

### Porting to run on CPU and GPU
Loading the models was easily possible using Tensorflow CPU.
However, I can't make a statement about how long it takes to make predictions using the CPU only.

### Improvements on the code base
I like the code base so far.

### Adapting the model
We should examine the approaches to segment lungs carefully that were used by the presented approaches.
Also, we definitely should have a look at [pyradiomics](https://github.com/Radiomics/pyradiomics) as this allowed one author to easily compute 45 features by just passing the image mask of a nodule and letting pyradiomics do the work.

## Comments
I really like the code base.
It is relatively clean and well documented for a competition submission.
My only concerns are regarding how long it would take to predict nodules of a patient using a CPU only.
One U-Net alone has 8 million parameters and the VGG derivative 400k.
Approach 1 alone apparently took 2-3 minutes for one patient to predict his cancer probability, which certainly involved at least one GPU.


## References
[Repository](https://github.com/owkin/DSB2017)
