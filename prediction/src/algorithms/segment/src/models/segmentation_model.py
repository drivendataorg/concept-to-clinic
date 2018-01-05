import os

import numpy as np
from keras import backend as K
from keras.models import load_model

from .....preprocess.lung_segmentation import DATA_SHAPE

try:
    from ......config import Config
except ValueError:
    from config import Config


class SegmentationModel(object):
    """Each segmentation model receives the rescaled DICOM images as input with the shape given by DATA_SHAPE
    and predicts a boolean mask with the same shape that indicates whether a voxel pixel contains malicious tissue"""

    def fit(self, X, y):
        """Fit the model using a matrix containing the rescaled DICOM images of shape (n, DATA_SHAPE) and the labels
        which are the boolean masks of the same shape.

        Args:
            X: Rescaled DICOM scans of shape (n, DATA_SHAPE)
            y: Boolean masks of shape (n, DATA_SHAPE)

        """
        assert X.shape[1:] == DATA_SHAPE, "Expected X include samples of shape " \
                                          "{} but got {}".format(X.shape[1:], DATA_SHAPE)
        assert y.shape[1:] == DATA_SHAPE, "Expected y include samples of shape " \
                                          "{} but got {}".format(y.shape[1:], DATA_SHAPE)
        self._fit(X, y)

    def _fit(self, X, y):
        raise NotImplementedError("Must implement '_fit()'")

    def predict(self, X):
        """Predict a boolean mask given the rescaled input scan.

        Args:
            X: Rescaled DICOM scan of shape DATA_SHAPE

        Returns: Path to the segmented scan

        """
        assert X.shape == (1, *DATA_SHAPE)
        y_predicted = self._predict(X)
        assert y_predicted.shape == (1, *DATA_SHAPE), "Expected y_predicted to be {} but got {}".format(
            (1, *DATA_SHAPE), y_predicted.shape)
        segment_path = os.path.join(os.path.dirname(Config.SEGMENT_ASSETS_DIR), 'lung-mask.npy')
        np.save(segment_path, y_predicted[0, :, :, :, 0])
        return segment_path

    def _predict(self, X):
        raise NotImplementedError("Must implement 'predict()'")

    def get_best_model_path(self):
        """
        Return the absolute path under which the best model of a SegmentationModel is stored
        """
        return os.path.join(Config.SEGMENT_ASSETS_DIR, "best_model_{}.hdf5".format(type(self).__name__))

    def load_best(self):
        """
        Load the best model which is serialized at get_best_model_path()
        """
        self.model = load_model(self.get_best_model_path())
        return self

    @classmethod
    def dice_coef(cls, y_true, y_pred, smooth=1.):
        """Calculates the Dice coefficient which equals 2TP/(2TP + FP + FN) between two tensors.

        Args:
            y_true: True labels. TensorFlow tensor.
            y_pred: Predictions. TensorFlow tensor of the same shape as y_true.
            smooth: Smoothing value that prevents division by zero

        Returns: single tensor value

        """
        y_true_f = K.flatten(y_true)
        y_pred_f = K.flatten(y_pred)
        intersection = K.sum(y_true_f * y_pred_f)
        return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

    @classmethod
    def dice_coef_loss(cls, y_true, y_pred):
        """ Calculates the negated dice coefficient (since losses should be minimized)

        Args:
            y_true: True labels. TensorFlow tensor.
            y_pred: Predictions. TensorFlow tensor of the same shape as y_true.

        Returns: single tensor value

        """
        return -SegmentationModel.dice_coef(y_true, y_pred)
