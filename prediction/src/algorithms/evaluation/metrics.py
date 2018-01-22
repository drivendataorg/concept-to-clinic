import numpy as np


def get_accuracy(true_positives, true_negatives, false_positives, false_negatives):
    """
     The accuracy is the ability to correctly predict the class of an observation.
    Args:
        true_positives: amount of items that have correctly been identifies as positives
        true_negatives: amount of items that have correctly been identifies as negatives
        false_positives: amount of items that have wrongly been identifies as positives
        false_negatives: amount of items that have wrongly been identifies as negatives

    Returns:

    """
    return (true_positives + true_negatives) / (true_positives + true_negatives + false_positives + false_negatives)


def logloss(true_label, predicted, eps=1e-15):
    """Calculate the logarithmic loss (http://wiki.fast.ai/index.php/Log_Loss)"""
    p = np.clip(predicted, eps, 1 - eps)
    if true_label == 1:
        return -np.log(p)
    else:
        return -np.log(1 - p)
