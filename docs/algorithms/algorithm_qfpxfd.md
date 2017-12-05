# qfpxfd algorithm

## Summary
**[Kaggle solution Authors](https://www.kaggle.com/c/data-science-bowl-2017/leaderboard):** [Jia Ding](https://www.kaggle.com/jdingpku), [JunGao](https://www.kaggle.com/stevegaopku), [WangDong](https://www.kaggle.com/xyq676419)  
**[Luna solution Authors](https://luna16.grand-challenge.org/results/):** Jia Ding, Aoxue Li, Zhiqiang Hu and Liwei Wang
The 4th place at the Data Science Bowl 2017 on the private leaderboard.

## License
[MIT License](https://github.com/NDKoehler/DataScienceBowl2017_7th_place/blob/master/LICENCE)


## Prerequisites
```Unknown```

```eval_rst
+------------+------------+----------+
| Dependency |   Name     | Version  |
+============+============+==========+
| Language   | Python     |          |
+------------+------------+----------+
| ML engine  | Keras      |          |
+------------+------------+----------+
| ML backend | Tensorflow |          |
+------------+------------+----------+
```


**Dependency packages:**
```Unknown```

## Algorithm design
The algorithm itself consists of 2 steps:
* Candidate detection
* False Positive Reduction

### Preprocessing
The axial slices are used as inputs. For each axial slice in CT images, its two neighbors slices are concatenated in axial direction, and then rescaled into 600×600×3 voxels.

### Candidate Detection

![1 1](https://user-images.githubusercontent.com/23284316/31894701-db90ad00-b817-11e7-9f05-3f082fbf3173.png)

the architecture of the proposed candidate detection network is composed of two modules: a region proposal network (RPN) that aims to propose potential regions of nodules (also called Region-of-Interest (ROI)); a ROI classifier then recognizes whether ROIs are nodules or not. These two DCNNs share the same feature extraction layers.

The region proposal network takes an image as input and outputs a set of rectangular object proposals (i.e. ROIs), each with an objectness score. 
It is based on an original Faster R-CNN with a deconvolutional layer added.

To generate ROIs, a small network is slided over the feature map of the deconvolutional layer. At each sliding-window location, multiple ROIs are simultaneously predicted. The multiple ROIs are parameterized relative to the corresponding reference boxes, called anchors.

![2](https://user-images.githubusercontent.com/23284316/31894747-f3d92234-b817-11e7-8d81-80a395291178.png)


With the ROIs extracted by RPN, a DCNN is developed to decide whether each ROI is nodule or not. A ROI Pooling layer is firstly exploited to map each ROI to a small feature map.

The ROI pooling works by dividing the ROI into a grid of sub-windows and then max-pooling the values in each sub-window into the corresponding output grid cell. Pooling is applied independently to each feature map channel as in standard max pooling. After ROI pooling layer, a fully-connected network, which is composed of two 4096-way fully-connected layers, then map the fixed-size feature map into a feature vector. A regressor and a classifier based on the feature vector then respectively regress boundingboxes of candidates and predict candidate confidence scores.

### False Positive Reduction Using 3D DCNN
![1 2](https://user-images.githubusercontent.com/23284316/31894769-02530bc2-b818-11e7-952a-aa64ec587328.png)

With the extracted nodule candidates, a 3D DCNN is utilized for false positive reduction. This network contains six 3D convolutional layers which are followed by Rectified Linear Unit (ReLU) activation layers, three 3D max-pooling lay- ers, three fully connected layers, and a final 2-way softmax activation layer to classify the candidates from nodules to none-nodules.
![3](https://user-images.githubusercontent.com/23284316/31894793-11e4b586-b818-11e7-8925-bd04168b501a.png)

As for inputs of the proposed 3D DCNN, each CT scan is firstly normalized with a mean of -600 and a standard deviation of -300. After that, for each candidate, the center of candidate is used as the centroid and then crop a 40 × 40 × 24 patch. 

## Trained model

**Source:** seems that it's no access to the trained models. </br>

**Usage instructions:**  
```unknown```

## Model Performance
```Unknown```
<!--
**Test system:**  </br>

| Component | Spec  | Count | 
|-----------|-------|-------|
| CPU       |  |       |
| GPU       |  |       |
| RAM       |  |       |
|           |  |       |
-->

## Training time:**  
```Unknown```

## Prediction time:** unknown, but must be less than 14 min per CT, since it processes the 506 CTs for the 5 days </br>

### Model Evaluation
The performance was evaluated on the LUNA16 Challenge with dataset which contains a total of 888 CT scans. In the LUNA16 challenge, performance is evaluated using the Free-Response Receiver Operating Characteristic (FROC) analysis.

Candidate Detection Results showed sensetivity of 0.946 with 15.0 canditates/scan.
The competition performance metric (CPM, averaged FROC key-points' magnitude) score is 0.891.

**Dataset:**  Data Science Bowl evaluation dataset </br>

```eval_rst
+-------------------------+---------------------+---------------+-------------+
|  Problem                | Score               | Metric        | Dataset     |
+=========================+====================++===============+=============+
|Lung Cancer Detection    | Log Loss            | 0.40183       | Kaggle      |
+-------------------------+---------------------+---------------+-------------+
|False Positive Reduction | CPM                 | 0.891         | Luna16      |
+-------------------------+---------------------+---------------+-------------+
|Candidate Detection      | Sensitivity </br>   | 0.946 </br>   | Luna16      |
+-------------------------+---------------------+---------------+-------------+
|                         | Candidates per scan | 15.0          |             |
+-------------------------+---------------------+---------------+-------------+
```

## Use cases


### When to use this algorithm

 - For the nodules candidates detection and segmentation.  

### When to avoid this algorithm

 - If there's is no GPU support it may consume a huge amount of time.
 
## Adaptation into Concept To Clinic
Since the actual repo reference as well as a trained model can not be found, there is no way to adapt the algorithm into Concept To Clinic except for implementing it from scratch. The authors of the solution were emailed in order to get an actual information.

## References
[Luna16 results](https://luna16.grand-challenge.org/results/)  
[Data Science Bowl results](https://www.kaggle.com/c/data-science-bowl-2017/leaderboard)
