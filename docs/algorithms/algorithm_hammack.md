# Daniel Hammack Algorithm

## Summary
The algorithm stands out with the idea to pre-detect possible abnormal regions which are then fed to two ensembles of 17 3D convolutional neural networks (CNNs). It is combined with the algorithm by Julian de Wit at the prediction level.

## Source
**Author:** Daniel Hammack  
**Repository:** https://github.com/dhammack/DSB2017  
The approach scored 2nd place at the Data Science Bowl 2017.

## License
Neither mentioned in the repository nor in the technical report, but since the authors had to accept the [Data Science Bowl rules](https://www.kaggle.com/c/data-science-bowl-2017/rules), the code must be published under [MIT](http://opensource.org/licenses/MIT) license.


## Prerequisites

```eval_rst
+------------+----------------------+----------+
| Dependency |   Name               | Version  |
+============+======================+==========+
| Language   | Python               |   2.7    |
+------------+----------------------+----------+
| ML engine  | Keras                |          |
+------------+----------------------+----------+
| ML backend | Theano, scikit-learn |          |
+------------+----------------------+----------+
| OS         |                      |          |
+------------+----------------------+----------+
| Processor  | CPU                  | yes      |
+------------+----------------------+----------+
|            | GPU                  | yes      |
+------------+----------------------+----------+
| GPU driver | CUDA                 |          |
+------------+----------------------+----------+
|            | cuDNN                |          |
+------------+----------------------+----------+
```


**Dependency packages:**
Neither the repository nor the authors specified exact versions of the Python packages:  
```
cPickle
joblib
matplotlib
numpy  
pandas  
pdb
PIL
pydicom
pylab
scipy  
SimpleITK  
skimage
```

## Algorithm design

### Preprocessing
The author states:
```
Each CT scan is resized so that each voxel represents a 1 mm³ volume. This is necessary so that the
same model can be applied to scans with different ‘slice thickness’. Slice thickness refers to the distance
between consecutive slices (when viewing a 3D image as a collection of 2D slices) and can vary by up to
4x between scans. The scans are also clipped between -1000 and 400 Hounsfield units. Air has a value of
-1000 HU and bone has 400, so values beyond these two endpoints are not informative for the diagnosis.
After this, each scan is rescaled to lie between 0 and 1 with -1000 mapping to 0 and +400 mapping to
1. A crude lung segmentation is also used to crop the CT scan, eliminating regions that don’t intersect
the lung.
```

### Nodule detection
To detect candidate nodules, the author built a model for identifying regions of the scan that appear abnormal:
```
[...] This model has an architecture similar to our nodule models, but it was trained on data with 90% normal
samples and 10% abnormal samples. It used a regression objective with a single output representing a
weighted combination of nodule attributes (with more weight for the more important attributes). Thus
a larger value is assigned the more ‘abnormal’ the region.
Each scan is limited to have between 1 and 50 ‘abnormal regions’. If more than 50 are found, the
50 most abnormal are kept (and if none are found we pick the most abnormal regardless). An abnormal
region is defined to be any 64 mm³ region of the scan which received a prediction higher than a chosen
threshold (our choice was 1 but it’s relatively arbitrary as the units for this metric aren’t meaningful).
```
The author found out that it is very helpful to predict further attributes of the nodules such as diameter, lobulation, spiculation, and malignancy.
He suspects that
```
[...] training simultaneously on multiple objectives smooths out the gradients (as we were
able to increase the learning rate substantially when training on multiple objectives).
```
To create more training data, the author performed random 3D transformations of the input.


### Prediction of cancer probability
```
The last step in our pipeline is to forecast a cancer diagnosis given the nodule attribute predictions. The
number of nodules per scan is variable and there are 4 predicted attributes for each nodule. We manually
constructed features thought to be informative for diagnosis from the nodule attribute predictions. Our
features are:
• max malignancy, spiculation, lobulation, and diameter across nodules (4 features)
• stdev of malignancy, spiculation, lobulation, and diameter predictions across nodules (4 features)
• location of most malignant nodule (3 features, one for each dimension in the scan)
• stdev of nodule locations in each dimension (3 features)
• nodule clustering features (4 features)
```
When plotting the feature importances, one can clearly recognize that `malignancy` is the feature that correlates the most with the cancer probability.
Another interesting fact is that the Z-dimension, so whether the nodule is closer to the head or closer to the feet, is also a very useful feature.
![](https://user-images.githubusercontent.com/6676439/30220303-39f8a54a-94bf-11e7-9e93-2e8e40bcf7be.png)

## Trained model

**Source:** https://github.com/dhammack/DSB2017/commit/896282c0f41a4fd752aabe7fa9de6a65943ba745  

**Usage instructions:** The code used to score and save the predictions is in [scoring_code](https://github.com/dhammack/DSB2017/tree/master/scoring_code).


## Model Performance

### Training- / prediction time

**Test system:**     </br>

```eval_rst
+-----------+-------------------------------+-------+
| Component | Spec                          | Count |
+===========+===============================+=======+
| CPU       |                               |       |
+-----------+-------------------------------+-------+
| GPU       | Tesla K80 / amazon p2.xlarge  | 1     |
+-----------+-------------------------------+-------+
| RAM       |                               |       |
+-----------+-------------------------------+-------+
```

**Training time:**  8 hours on K80 / 1.5 hours on AWS  
**Prediction time:**  unknown

### Model Evaluation


**Dataset:**
Data Science Bowl evaluation dataset

```eval_rst
+----------+---------+
| Metric   | Score   |
+==========+=========+
| Log Loss | 0.401172|
+----------+---------+
```

## Use cases

### When to use this algorithm

 - the output of the first network, which finds the 50 most abnormal regions and predicts the attributes `diameter, lobulation, spiculation` and `malignancy`, could be used to suggest abnormal regions to the user including the predicted attributes to offer further support in detecting candidate nodules  
 - using multiple small networks and ensembling them creates in theory a solution that generalizes very well


### When to avoid this algorithm

 - running multiple CNNs and combining them adds a lot of computational overhead which results in a longer prediction time. Though, it's still unclear how long the prediction given one CT scan really takes (so this is just an assumption)

## Adaptation into Concept To Clinic

### Porting to Python 3.5+
A very tough problem might be that the author was not able to specify exact dependency versions he used. This could become a problem when we try to "estimate" the used versions. In the README the author already mentions: `Also - I have noticed that a newer version of OpenCV can break some of my code`. What might be even more devastating is what the author means by stating `Also I sometimes make modifications to my local Keras install to try out new things`. This makes it really complicated to estimate whether porting it to Python 3 is feasible.

### Porting to run on CPU and GPU
I haven't found the code that specifies which device to use for training so far. I'd estimate that porting the code to work on a CPU should definitely be possible.

### Improvements on the code base
I reached out to the author about how to actually use the proposed algorithm (he suggested to get in contact with him in such a case). Unfortunately, he didn't respond so far.

### Adapting the model
One could try to reduce the number of trained networks and predicted abnormal regions in order to speed up the prediction time.

## Comments
From my point of view, this is a very promising approach.
First using a network to suggest abnormal regions with helpful attributes that should further be investigated is a neat way to reduce the problem size.
Unfortunately, there is very little to no documentation of the code.
Furthermore, we don't know which exact dependency versions have been used which might result in further problems.

## References
Repository: https://github.com/dhammack/DSB2017  
Technical Report: https://github.com/dhammack/DSB2017/blob/master/dsb_2017_daniel_hammack.pdf
