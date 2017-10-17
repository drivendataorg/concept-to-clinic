import pytest

from ..algorithms.classify import trained_model


@pytest.fixture
def metaimage_path():
    yield '../images/LUNA-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797.mhd'


@pytest.fixture
def model_path():
    yield 'src/algorithms/classify/assets/gtr123_model.ckpt'


def test_classify_predict_model_load(metaimage_path, model_path):
    predicted = trained_model.predict(metaimage_path,
                                      [],
                                      model_path)

    assert len(predicted) == 0


def test_classify_predict_inference(metaimage_path, model_path):
    predicted = trained_model.predict(metaimage_path,
                                      [{"z": 556, "y": 100, "x": 0}],
                                      model_path)

    assert len(predicted) == 1
    assert isinstance(predicted[0]['p_concerning'], float)
    assert predicted[0]['p_concerning'] >= 0.
    assert predicted[0]['p_concerning'] <= 1.
