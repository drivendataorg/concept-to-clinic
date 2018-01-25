import numpy as np
import scipy.spatial

SMOOTH = 1e-10


def hausdorff_distance(ground_true, predicted):
    """Computes the Hausdorff distance, uses `scipy` implementation of 'an efficient algorithm for
    calculating the exact Hausdorff distance.' provided by A. A. Taha et al.

    Args:
        ground_true ground_true (np.ndarray[bool]): ground true mask to be compared with predicted one.
        predicted predicted (np.ndarray[bool]): predicted mask, allowed values are from {True, False}.
            Should be the same dimension as `ground_true`.
    Returns:
        double: The directed Hausdorff distance.
    """
    u = np.array(np.where(ground_true)).T
    v = np.array(np.where(predicted)).T
    hd, _, _ = scipy.spatial.distance.directed_hausdorff(u, v)
    return hd


def sensitivity(ground_true, predicted, smooth=SMOOTH):
    """Computes the sensitivity.

    Args:
        ground_true ground_true (np.ndarray[bool]): ground true mask to be compared with predicted one.
        predicted predicted (np.ndarray[bool]): predicted mask.
            Should be the same dimension as `ground_true`.
    Returns:
        double: The sensitivity.
    """
    P = np.sum(ground_true)
    TP = np.sum(ground_true * predicted) + smooth
    return P / TP


def specificity(ground_true, predicted, smooth=SMOOTH):
    """Computes the specificity.

    Args:
        ground_true ground_true (np.ndarray[bool]): ground true mask to be compared with predicted one.
        predicted predicted (np.ndarray[bool]): predicted mask.
            Should be the same dimension as `ground_true`.
    Returns:
        double: The specificity.
    """
    N = np.prod(ground_true.shape) - np.sum(ground_true)
    TN = np.sum(np.logical_not(ground_true) * np.logical_not(predicted)) + smooth
    return N / TN


def dice_coefficient(ground_true, predicted):
    """Computes the Dice dissimilarity coefficient via `scipy` implementation.

    Args:
        ground_true ground_true (np.ndarray[bool]): 1-dimensional raveled ground true mask
            to be compared with predicted one.
        predicted predicted (np.ndarray[bool]): 1-dimensional raveled predicted mask.
    Returns:
        double: The Dice dissimilarity.
    """

    return scipy.spatial.distance.dice(ground_true, predicted)


def dice_coefficient_uns(ground_true, predicted, smooth=SMOOTH):
    """The analogy of Dice coefficient provided by one of participants of ultrasound
    nerve segmentation Kaggle challenge. The implementation was adopted from:
    https://github.com/jocicmarko/ultrasound-nerve-segmentation/blob/master/train.py

    Args:
        ground_true ground_true (np.ndarray[bool]): ground true mask to be compared with predicted one.
        predicted predicted (np.ndarray[bool | float]): predicted mask, the values lies either in [0, 1] or
            in {True, False}. Should be the same dimension as `ground_true`.
        smooth (float): differs of the default value from the original implementation, was
            caused by the difference of ordinary mask volume.
    Returns:
        double: The analogy of Dice coefficient
    """

    intersection = 2. * np.sum(ground_true * predicted) + smooth
    union = np.sum(ground_true) + np.sum(predicted) + smooth

    return np.mean(intersection / union)


def evaluate(ground_true, predicted, threshold=0., uns_smooth=SMOOTH):
    """The function to orchestrate the evaluations.

    Args:
        ground_true (np.ndarray[bool]): ground true mask to be compared with predicted one.
        predicted (np.ndarray[bool | float]): predicted mask, the values lies either in [0, 1] or in {True, False}
            Should be the same dimension as `ground_true`.
        threshold (float): if the `predicted.dtype` is not boolean, then `predicted` = `predicted` > `threshold`.
            The default value is 0.
        uns_smooth (float): used by a Dice coefficient analogy provided by one of participants of
            ultrasound nerve segmentation Kaggle challenge.
    Returns:
        dictionary contained magnitudes of the metrics of type ::
            {hausdorff_distance (double)
             dice_coefficient_uns (double)
             sensitivity (double)
             specificity (double)
             dice_coefficient (double)}.
    """
    metrics = {}
    metrics['hausdorff_distance'] = hausdorff_distance(ground_true, predicted)
    metrics['dice_coefficient_uns'] = dice_coefficient_uns(ground_true, predicted, uns_smooth)

    ground_true_f = np.ravel(ground_true) > threshold
    predicted_f = np.ravel(predicted) > threshold
    metrics['sensitivity'] = sensitivity(ground_true_f, predicted_f)
    metrics['specificity'] = specificity(ground_true_f, predicted_f)
    metrics['dice_coefficient'] = dice_coefficient(ground_true_f, predicted_f)
    return metrics
