import numpy as np
import pytest

from ..algorithms.segment.src import evaluate


@pytest.fixture(scope='session')
def masks():
    ones = np.ones((10, 10, 10))
    zeros = np.zeros((10, 10, 10))
    combined = np.concatenate([zeros, ones], axis=0)
    combined_1 = np.concatenate([combined, combined], axis=1)
    combined_2 = np.concatenate([np.swapaxes(combined, 0, 1),
                                 np.swapaxes(combined, 0, 1)], axis=0)
    yield combined_1, combined_2


def test_segment_evaluate_hausdorff_distance(masks):
    combined_1, combined_2 = masks
    assert np.abs(10. - evaluate.hausdorff_distance(combined_1, combined_2)) < 1e-4


def test_segment_evaluate_dice_coefficient_uns(masks):
    combined_1, combined_2 = masks
    assert np.abs(.5 - evaluate.dice_coefficient_uns(combined_1, combined_2, smooth=1e-1)) < 1e-4


def test_segment_evaluate_dice_coefficient(masks):
    combined_1, combined_2 = masks
    combined_1 = np.ravel(combined_1).astype(np.bool_)
    combined_2 = np.ravel(combined_2).astype(np.bool_)
    assert .5 == evaluate.dice_coefficient(combined_1, combined_2)


def test_segment_evaluate_sensitivity(masks):
    combined_1, combined_2 = masks
    combined_1 = np.ravel(combined_1).astype(np.bool_)
    combined_2 = np.ravel(combined_2).astype(np.bool_)
    assert np.isclose([evaluate.sensitivity(combined_1, combined_2)], [2.])


def test_segment_evaluate_sensitivity_no_zero_division():
    zeros1 = np.zeros((10, 10, 10))
    zeros2 = np.zeros((10, 10, 10))
    combined_1 = np.ravel(zeros1).astype(np.bool_)
    combined_2 = np.ravel(zeros2).astype(np.bool_)
    assert np.isclose([evaluate.sensitivity(combined_1, combined_2)], [0.])


def test_segment_evaluate_specificity(masks):
    combined_1, combined_2 = masks
    combined_1 = np.ravel(combined_1).astype(np.bool_)
    combined_2 = np.ravel(combined_2).astype(np.bool_)
    assert np.isclose([evaluate.specificity(combined_1, combined_2)], [2.])


def test_segment_evaluate_specificity_no_zero_division():
    zeros1 = np.zeros((10, 10, 10))
    zeros2 = np.zeros((10, 10, 10))
    combined_1 = np.ravel(zeros1).astype(np.bool_)
    combined_2 = np.ravel(zeros2).astype(np.bool_)
    assert np.isclose([evaluate.specificity(combined_1, combined_2)], [1.])


def test_segment_evaluate_evaluate(masks):
    combined_1, combined_2 = masks
    desired_behaviour = {'hausdorff_distance': 10.0,
                         'dice_coefficient_uns': 0.5,
                         'sensitivity': 2.0,
                         'specificity': 2.0,
                         'dice_coefficient': 0.5}

    calculated = evaluate.evaluate(combined_1, combined_2)

    for key, output in desired_behaviour.items():
        assert np.abs(output - calculated[key]) < 1e-4, 'The output of function %s is %f, while %f was expected.' % \
                                                        (key, calculated, output)
