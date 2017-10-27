from ..algorithms.classify import trained_model


def test_classify_predict_model_load(metaimage_path, model_path):
    assert not trained_model.predict(metaimage_path, [], model_path)


def test_classify_predict_inference(metaimage_path, luna_nodule, model_path):
    predicted = trained_model.predict(metaimage_path, [luna_nodule], model_path)
    assert predicted
    assert 0 <= predicted[0]['p_concerning'] <= 1
