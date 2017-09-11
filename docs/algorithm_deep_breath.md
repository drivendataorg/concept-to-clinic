# Deep Breath Algorithm

## Summary
This algorithm trains a network for determining if a voxel in a scan is part of a nodule to generate a list of
nodule candidates and their centroids, and additional networks to reduce the number of candidates and predict the malignancy of 
the remaining nodules. Finally, another network is trained to predict the probability of lung cancer.

## Source
**Authors:** Elias Vansteenkiste, Matthias Freiberger, Andreas Verleysen, 
Iryna Korshunova, Lionel Pigou, Frederic Godin, Jonas Degrave  
**Repository:** https://github.com/EliasVansteenkiste/dsb3  
The approach scored 9th place at the Data Science Bowl 2017.

## License
[MIT](http://opensource.org/licenses/MIT) license


## Prerequisites

| Dependency |   Name   | Version  |
|------------|----------|----------|
| Language   | Python   |   2.7    |
| ML engine  | Lasagne  | 0.2.dev1 |
| ML backend | Theano   | 0.9.0b1  |
| OS         | Ubuntu   |  16.04   |
| Processor  | CPU      | yes      |
|            | GPU      | yes      |
| GPU driver | CUDA     |   8      |
|            | cuDNN    |   5.1    |


**Dependency packages:**
```
theano 0.9.0b1
lasagne 0.2.dev1
scikit-image 0.12.3
scipy 0.18.1
numpy 1.12.0
scikit-learn 0.18.1
```


## Algorithm design

The authors provide a detailed overview of the algorithm in [1].

### Preprocessing
As described by the authors:
```
The chest scans are produced by a variety of CT scanners, this causes a difference in spacing between voxels of the original scan. 
We rescaled and interpolated all CT scans so that each voxel represents a 1x1x1 mm cube. 
```

### Nodule detection
First, a network for segmenting nodules in the input scan was built using the LUNA dataset as training data.
The dataset contains the location and diameter of nodules.
```
To train the segmentation network, 64x64x64 patches are cut out of the CT scan and fed to the input of the segmentation network.
For each patch, the ground truth is a 32x32x32 mm binary mask. Each voxel in the binary mask indicates if the voxel is inside the nodule.
The masks are constructed by using the diameters in the nodule annotations.
```
The Dice coefficient was used as an objective function, as it is well suited to counter the imbalance of bigger and smaller nodules.
```
The downside of using the Dice coefficient is that it defaults to zero if there is no nodule inside the ground truth mask.
There must be a nodule in each patch that we feed to the network. To introduce extra variation, we apply translation and rotation augmentation. 
The translation and rotation parameters are chosen so that a part of the nodule stays inside the 32x32x32 cube around the center of the 64x64x64 input patch.
```
The network architecture is based on the U-net architecture, which was adapted to 3D input data. It mainly consists of convolutional layers with 3x3x3 filter kernels without padding, 
and one max pooling layer. (See [1] for a detailed schematic.)
```
The trained network is used to segment all the CT scans of the patients in the LUNA and DSB dataset. 64x64x64 patches are taken out the volume with a stride of 32x32x32 and the prediction maps are stitched together.
In the resulting tensor, each value represents the predicted probability that the voxel is located inside a nodule.
```

### Blob detection
After nodule segmentation, there is a prediction for each voxel in the scan if it is inside a nodule. To find the center of nodules, blobs of high probability voxels are searched.
To find such blobs, the Difference of Gaussian method is used as implemented in the scikit-image package.
After blob detection, there is a list of nodule candidates with their respective centroids.
Some problems the authors discovered with this method:
```
Unfortunately the list contains a large amount of nodule candidates. For the CT scans in the DSB train dataset, the average number of candidates is 153. The number of candidates is reduced by two filter methods:

    Applying lung segmentation before blob detection
    Training a false positive reduction expert network
```

### Lung segmentation
After discovering that 2D segmentation didn't work well because the segmentation network didn't have a global context, the authors developed a 3D approach which focused on cutting out the non-lung 
cavities from the convex hull built around the lungs.

### False Positive Reduction
To reduce the large size of nodule candidates that are returned by the blob detection algorithm, an expert network was trained for predicting if the candidate really is a nodule.
```
We used lists of false and positive nodule candidates to train our expert network. The LUNA grand challenge has a false positive reduction track which offers a list of false and true nodule candidates for each patient.
For training our false positive reduction expert we used 48x48x48 patches and applied full rotation augmentation and a little translation augmentation (±3 mm).
If we want the network to detect both small nodules (diameter <= 3mm) and large nodules (diameter > 30 mm), the architecture should enable the network to train both features with a very narrow and a wide receptive field. 
The inception-resnet v2 architecture is very well suited for training features with different receptive fields. Our architecture is largely based on this architecture. We simplified the inception resnet v2 and applied its principles to tensors with 3 spatial dimensions. 
We distilled reusable flexible modules. These basic blocks were used to experiment with the number of layers, parameters and the size of the spatial dimensions in our network.
```
(See [1] for a detailed schematic.)

### Malignancy prediction
Another network was trained on the LUNA dataset to predict the malignancy of nodules:
```
The network we used was very similar to the FPR network architecture. In short it has more spatial reduction blocks, more dense units in the penultimate layer and no feature reduction blocks.
We rescaled the malignancy labels so that they are represented between 0 and 1 to create a probability label. We constructed a training set by sampling an equal amount of candidate nodules that did not have a malignancy label in the LUNA dataset.
As objective function, we used the Mean Squared Error (MSE) loss which showed to work better than a binary cross-entropy objective function.
```


### Prediction of cancer probability
```
After we ranked the candidate nodules with the false positive reduction network and trained a malignancy prediction network, we are finally able to train a network for lung cancer prediction on the Kaggle dataset. 
Our strategy consisted of sending a set of n top ranked candidate nodules through the same subnetwork and combining the individual scores/predictions/activations in a final aggregation layer.
```

Transfer learning was used to improve the results:
```
At first, we used the the fpr network which already gave some improvements. Subsequently, we trained a network to predict the size of the nodule because that was also part of the annotations in the LUNA dataset. In both cases, our main strategy was to reuse the convolutional layers but to randomly initialize the dense layers.
```

To aggregate nodule predictions, the two most successful strategies were described as follows:

**P_patient_cancer = 1 - ∏ P_nodule_benign**
The idea behind this aggregation is that the probability of having cancer is equal to 1 if all the nodules are benign. If one nodule is classified as malignant, P_patient_cancer will be one. The problem with this approach is that it doesn’t behave well when the malignancy prediction network is convinced one of the nodules is malignant. Once the network is correctly predicting that the network one of the nodules is malignant, the learning stops.

**Log Mean Exponent**
The idea behind this aggregation strategy is that the cancer probability is determined by the most malignant/the least benign nodule. The LME aggregation works as the soft version of a max operator. As the name suggest, it exponential blows up the predictions of the individual nodule predictions, hence focussing on the largest(s) probability(s). Compared to a simple max function, this function also allows backpropagating through the networks of the other predictions.


For the final predictions, the results of the last 30 stage models were ensembled.

## Trained model

Not available

## Model Performance

### Training- / prediction time

As taken from the official documentation:

**Test system:**     </br>
7 machines with following specs:
GPU: GTX 1080, GTX 980, Titan X, Tesla K40
Mem: 32GB to 64GB per machine
CPU: mostly 6 cores, 3GHz to 4GHz

**Training time:** 4 days </br>
**Prediction time:** 3 days </br>

### Model Evaluation

**Dataset:**    </br>

| Metric   | Score |
|----------|-------|
| Accuracy |       |

## Use cases
<!-- List strengths and weaknesses of the algorithm. -->

### When to use this algorithm

 - 
 -
 -

### When to avoid this algorithm

 - 
 -
 -
 
## Adaptation into Concept To Clinic

### Porting to Python 3.5+


### Porting to run on CPU and GPU
With training times and specs as specified in the section above, it does not seem to be worth to try running this on CPU only.

### Improvements on the code base
Code is spread across lots of (ambiguously named) files with what seem to be independent Python scripts, lots of cleanup/refactoring needs to be done here.

### Adapting the model
The models used for nodule detection are a good approach to find candidates, but the process has to be turned into a reusable pipeline. 

## Comments


## References

[1] https://eliasvansteenkiste.github.io/machine%20learning/lung-cancer-pred/
