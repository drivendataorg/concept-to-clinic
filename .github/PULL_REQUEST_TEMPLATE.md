<!--- Provide a general summary of your changes in the Title above -->

## Description
<!--- Describe your changes in detail -->

## Reference to official issue
<!--- If fixing a bug, there should be an existing issue describing it with steps to reproduce -->
<!--- Please link to the issue here: -->


## Motivation and Context
<!--- Why is this change required? What problem does it solve? -->
<!--- If adding a new feature or making improvements not already reflected in an official issue, please reference the relevant sections of the design doc -->


## How Has This Been Tested?
<!--- Please describe in detail how you tested your changes. -->
<!--- Include details of your testing environment, and the tests you ran to -->
<!--- see how your change affects other areas of the code, etc. -->

## Screenshots (if appropriate):


## Metrics (if appropriate):

If you submitting a PR for a prediction algorithm (segmentation, identification,
or classification) please fill in values for as many as the below statistics as
are relevant.

*algorithms by metric*

metric | relevant algorithms
-------|--------------------
[accuracy <sup>1</sup> <sup>2</sup>](https://stats.stackexchange.com/a/231237/143678) | classification, identification
[data IO](https://unix.stackexchange.com/questions/55212) | classification, identification, segmentation
[Dice coefficient <sup>3</sup>](https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient) | segmentation
[disk space usage](https://www.cyberciti.biz/faq/linux-check-disk-space-command) | classification, identification, segmentation
[Hausdorff distance <sup>3</sup>](https://en.wikipedia.org/wiki/Hausdorff_distance) | segmentation
[Jaccard index](https://en.wikipedia.org/wiki/Jaccard_index) | segmentation
[Log Loss](http://wiki.fast.ai/index.php/Log_Loss) | classification, identification <sup>4</sup>
[memory usage](https://stackoverflow.com/questions/110259) | classification, identification, segmentation
[prediction time <sup>2</sup>](https://stackoverflow.com/questions/385408) | classification, identification, segmentation
[sensitivity <sup>3</sup>](http://wiki.fast.ai/index.php/Deep_Learning_Glossary#Recall) | segmentation
[specificity <sup>3</sup>](http://wiki.fast.ai/index.php/Deep_Learning_Glossary#Specificity) | segmentation
[training time <sup>2</sup>](https://stackoverflow.com/questions/385408) | classification, identification, segmentation

*notes*

1. Use 5-fold cross validation if there is enough time and computational power available, otherwise use a holdout set
1. This metric may be automatically calculated by the machine learning architecture, e.g., Keras
1. The calculations for these metrics [are available here](https://github.com/concept-to-clinic/concept-to-clinic/blob/master/prediction/src/algorithms/segment/src/evaluate.py)
1. In order to calculate Log Loss for identification, the data needs to be arranged in a way that shows for each pixel, whether or not it is a nodule centriod. Restated, the pixel level labels of 1/0 would correspond to centriod/not-centriod.

*metrics by algorithm*

algorithm      | relevant metrics
---------------|------------------
classification | accuracy, data IO, disk space usage, Log Loss, memory usage, prediction time, training time
identification | accuracy, data IO, disk space usage, Log Loss, memory usage, prediction time, training time
segmentation   | data IO, Dice coefficient, disk space usage, Hausdorff distance, Jaccard index, memory usage, prediction time, sensitivity, specificity, training time

When reporting your values, please use a format similar to the following example.

algorithm    | metric | value
-------------|--------|------:
segmentation | accuracy | 99.5
segmentation | Jaccard index | 0.5
segmentation | prediction time (s) | 45.3
segmentation | memory usage (MB) | 5.4

## CLA
- [ ] I have signed the CLA; if other committers are in the commit history, they have signed the CLA as well
