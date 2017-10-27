from ..algorithms.classify import trained_model


def test_classify_predict_model_load(metaimage_path, model_path):
    predicted = trained_model.predict(metaimage_path,
                                      [],
                                      model_path)

    assert len(predicted) == 0


def test_classify_predict_inference(metaimage_path, luna_nodule, model_path):
    predicted = trained_model.predict(metaimage_path, [luna_nodule], model_path)
    assert len(predicted) == 1
    assert isinstance(predicted[0]['p_concerning'], float)
    assert predicted[0]['p_concerning'] >= 0.
    assert predicted[0]['p_concerning'] <= 1.
