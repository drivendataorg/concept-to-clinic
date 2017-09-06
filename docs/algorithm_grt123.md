# grt123 Algorithm

## Summary
The algorithm consists of nodule detection and cancer classification based on 3D convolution neural networks.
The model receives preprocessed 3D lung scans as
input and outputs both the bounding boxes of suspicious nodules and the probability of getting cancer.

## Source
**Author:** Team grt123      
**Repository:** https://github.com/lfz/DSB2017  
1st place at the Data Science Bowl 2017

## License
Neither mentioned in the repository nor in the technical report, but since the authors had to accept the [Data Science Bowl rules](https://www.kaggle.com/c/data-science-bowl-2017/rules), the code must be published under [MIT](http://opensource.org/licenses/MIT) license.


## Prerequisites

| Dependency |   Name   | Version  |
|------------|----------|----------|
| Language   | Python   |   2.7    |
| ML engine  | pyTorch  | 0.1.10+ac9245a |
| ML backend |          |          |
| OS         | Ubuntu   |  14.04   |
| Processor  | CPU      |  yes     |
|            | GPU      |  yes     |
| GPU driver | CUDA     |  8.0     |
|            | cuDNN    |  5.1     |


**Dependency packages:**
```
h5py==2.6.0  
SimpleITK==0.10.0  
numpy==1.11.3
nvidia-ml-py==7.352.0
matplotlib==2.0.0
scikit-image==0.12.3
scipy==0.18.1
pyparsing==2.1.4
pytorch==0.1.10+ac9245a
```


## Algorithm design
First, a binary mask of a lung is applied to the data to filter out as much noise as possible. Next, a CNN is trained to detect nodules that might be malicious. Lastly, another CNN takes the top 5 nodules that appear to be most malicious and tries to predict whether the patient has cancer. For both networks data augmentation is used to artificially increase the amount of data on which they can be trained.

### Preprocessing
All raw data is first converted into Hounsfield units.
It is then clipped with the window [-1200, 600] and then transformed linearly to [0, 255].
Next, a binary mask of the space inside a lung is calculated.
![screenshot from 2017-08-29 10-07-02](https://user-images.githubusercontent.com/6676439/29810873-d461d9ce-8ca1-11e7-93b0-20a0ad8c5d6b.png)
The mask is multiplied with the raw data in order to quickly remove noise that does not belong to the lung.
Everything outside of the mask is padded with 170.
All values greater than 210 (typically the bones) are replaced with
170 as well.
The padding value 170 is chosen to resemble the intensity of tissue.


### Nodule detection
Due to the memory constraints of the GPU, patches of sizes 128 x 128 x 128 are cropped from the lung scans and then fed to the network.
70% of the patches contain at least one nodule while the remaining 30% may contain no modules.
If a patch goes beyond the range of the lung scan, it is padded with the value 170.
For data augmentation, patches are
randomly left-right flipped and resized with a ratio between 0.8 and 1.15.
Oversampling was used for big nodules in the training set to achieve a more balanced distribution of nodule sizes. Also, hard negative mining was used to further balance the training set.
The network structure looks as follows:
![screenshot from 2017-08-29 10-06-48](https://user-images.githubusercontent.com/6676439/29810879-d9088d1a-8ca1-11e7-9e1d-8b7d68b838c4.png)

### Prediction of cancer probability
After the nodule detection net (N-Net) was trained, the authors applied it onto the whole 3D scan of each patient. The top 5 proposed nodules of the N-Net are then fed to the cancer classification net.
Next, they proceeded as follows:  
*
We extracted the last convolution layer of N-Net for each proposal, which is a 32 × 32 × 32 cube of 128 features shown in Fig. 3 as a green volume. We max pool over the central 2 × 2 × 2 voxels of each proposal, and pass the resulting 128-D features to
two succeeding fully connected layers to generate a prediction of cancer probability. We
assume the final diagnosis is made from these 5 proposals and a hypothetical dummy
nodule (in case N-Net missed some nodules) independently.*  
The whole approach can be seen in Figure 4.
![screenshot from 2017-08-29 10-06-03](https://user-images.githubusercontent.com/6676439/29810847-b7e0cac6-8ca1-11e7-88ca-772a4fb4b48b.png)
The prediction loss is defined at the right hand side of Figure 4 where P_{d} is a free parameter
representing the cancer probability from the dummy nodule.

## Trained model

**Source:**   
https://github.com/lfz/DSB2017/tree/master/model  


**Usage instructions:**  
Running [main.py](https://github.com/lfz/DSB2017/blob/master/main.py) should use the final models to create the output files for the Data Science Bowl.

## Model Performance

### Training- / prediction time

**Test system:** </br>

| Component | Spec  | Count |
|-----------|-------|-------|
| CPU       |       |       |
| GPU       | TITAN X|   8   |
| GPU       |Memory |>= 12GB|
| RAM       |       |       |

**Training time:**  4 days</br>
**Prediction time:** </br>

### Model Evaluation

**Dataset:** Private Kaggle Test Data

| Metric   | Score |
|----------|-------|
| Log-Loss |  0.39975 |

## Use cases

### When to use this algorithm

 - when you want to achieve the least log-loss on the Data Science Bowl test data

### When to avoid this algorithm

 - when you want to train the model by yourself from scratch (it took the authors 4 days on 8 TITAN X)

## Adaptation into Concept To Clinic

### Porting to Python 3.5+
I did not manage to run the complete algorithm so far as I'm lacking CUDA.
@reubano attempted to port it to Python 3.5 [here](https://github.com/concept-to-clinic/DSB2017).

### Porting to run on CPU and GPU
Since modules such as [DataParallel](http://pytorch.org/docs/master/_modules/torch/nn/parallel/data_parallel.html) are used, it appears to be non-trivial to make the algorithm run only using a CPU.

### Improvements on the code base
As expected from a code base created at a competition, most of it is completely undocumented.

### Adapting the model
Multiplying the data with a binary mask of a lung is a nice way to remove noise that does not belong to the lung itself. Also, using CNNs definitely makes sense as the weight sharing decreases the amount of memory needed by the model.

## Comments
The accuracy and ranking of the algorithm speaks for itself. Though, I'm not sure how easy it is to re-use as it is completely undocumented, written in Python 2.7 and it took 8 TITAN X to train it. Hopefully, to segment a nodule it also works on a regular GPU of a desktop PC.  

## References
[Repository](https://github.com/lfz/DSB2017)  
[Technical Report](https://github.com/lfz/DSB2017/blob/master/solution-grt123-team.pdf)
