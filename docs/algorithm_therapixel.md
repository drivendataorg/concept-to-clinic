# Therapixel

## Summary

The algorithm screens and characterizes nodules as well as masses and scans for emphysema as well as aorta calcifications using pre-trained models.
In the end, the results are aggregated and the cancer probability is calculated using XGBoost.

## Source
**Author:** Pierre Fillard  
**Repository:** https://github.com/pfillard/tpx-kaggle-dsb2017  

## License
GNU General Public License v3.0  


## Prerequisites
This is the recommended / tested environment

| Dependency |   Name   | Version  |
|------------|----------|----------|
| Language   | Python   |   3.5    |
| ML engine  |          |          |
| ML backend |          |Tensorflow 1.1|
| OS         | Ubuntu   |16.04 x64 |
| Processor  | CPU      |2x Intel i7|
|            | GPU      |4xNVIDIA Titan|
| Alternative GPU| GPU  |NVIDIA NVIDIA P6000|
| GPU driver | CUDA     |   8      |
|            | cuDNN    |   5.1    |


**Dependency packages:**
All dependencies have been installed using `pip3`.
````
https://github.com/pfillard/tensorflow/tree/r1.0_relu1
xgboost
numpy
scipy
skimage
SimpleITK
h5py
optparse
````


## Algorithm design
Unfortunately, there is no technical report or blog post about the approach so far.
Thus, the following notes have been derived from the source code only.

### Data format
The input data is expected to have been converted in ITK MetaImage (.mhd, .raw) format.
Some suggested ressources for that are [here](https://itk.org/ITKExamples/src/IO/GDCM/ReadDICOMSeriesAndWrite3DImage/Documentation.html) and [here](http://manpages.ubuntu.com/manpages/precise/man1/gdcm2vtk.1.html).

### Preprocessing
The algorithm first segments the lung using a VGG-like 3DConvNet.

### Nodule detection
Using 5 pre-trained models, the algorithm searches for nodules and saves their location together with the probability of the detection really being a nodule.
Next, two models estimate the malignancy and the size of the nodules using regression techniques.

### Further features
#### Mass detection
Using the same models as for nodule detection, the algorithm tries to detect masses that might also exist beyond the lungs.
The same models as for the nodule characterization are used to estimate size and malignancy of them.

#### Emphysema scan
For each image series, one model scans for emphysema (a lung disease that's responsible for short breath and is most often caused by smoking).
The model outputs ten values labeled 'eh0' to 'eh9' whose meaning is still enigmatic to me.

#### Aorta calcification
Lastly, one model is applied to find calcifications of the aorta.
The model outputs ten values labeled 'ah01' to 'ah10'.

### Prediction of cancer probability
The features created in the previous steps, which have been saved to separate CSV files, are firstly aggregated into one CSV file.
That file only uses the features: eh0, eh1, eh2, max_nod_size, max_nod_size, prob_max_nod, max_malignancy, prob_max_mal, ah0, ah1 and ah2.
Lastly, XGBoost predicts the cancer probability based on these features.

## Trained model

**Source:** https://github.com/pfillard/tpx-kaggle-dsb2017/tree/master/models

**Usage instructions:**  
- Use `train.py` for feature extraction and model training  
- Use `predict.py` to make predictions

## Model Performance

### Training- / prediction time
Unknown  
**Test system:**     </br>

| Component | Spec  | Count |
|-----------|-------|-------|
| CPU       |       |       |
| GPU       |       |       |
| GPU       |       |       |
| RAM       |       |       |

**Training time:**  </br>
**Prediction time:** </br>

### Model Evaluation

**Dataset:** Data Science Bowl 2017

| Metric   | Score |
|----------|-------|
| Accuracy |0.40409|

## Use cases

### When to use this algorithm

 - if we also want to include information about masses beyond the lung, emphysema or aorta calcification
 - if we're fine with working with black-box algorithms

### When to avoid this algorithm

 - if converting images in ITK MetaImage is not feasible
 - if we want to understand what the design decisions of the author have been regarding network architecture etc. (no documentation given)

## Adaptation into Concept To Clinic

### Porting to Python 3.5+
The algorithm was written to run with Python 3.5.

### Porting to run on CPU and GPU
When trying to run the code without a GPU, I'm getting errors when the models are restored.
However, I think that it should be possible to port the models to run on CPUs.
I'm just not that experienced with Tensorflow so far.

### Improvements on the code base
The `kaggle_utils` and the `lidc` files need to be refactored as they already consist of over 600, respectively, 1100 lines of code.

### Adapting the model
It's questionable how much impact the additional features have and how well the nodule detection works itself.
Also, the models still are big black-boxes that first need to be interpreted in order to understand them and to make changes that can improve them.

## Comments
I'm positively surprised by how well the author documented the technical requirements and how easy it is to overlook the codebase.
Unfortunately, I haven't found a blog article or technical report about the approach.
Thus, one is supposed to derive from the code what the author's solution concept is and what's the models architectures are.
Furthermore, I'm not sure how one is supposed to install the Tensorflow 1.0 fork of the author which adds a patch for relu.
It seems that one is required to compile it oneself using `./configure` and `bazel`.
I contacted the author and asked for any advices on how to understand the pre-trained models and how to improve the approach to actually use it in an application.
However, since the author seems to sell this approach or similar solutions to customers, I doubt that he will be able to help us a lot.

## References
[Repository](https://github.com/pfillard/tpx-kaggle-dsb2017)  
[Sales Homepage](http://therapixel.com/)
