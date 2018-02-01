from ..algorithms.classify import trained_model


def test_classify_predict_load(metaimage_path, model_path):
    assert not trained_model.predict(metaimage_path, [], model_path)


def test_classify_dicom(dicom_paths, nodule_locations, model_path):
    predicted = trained_model.predict(dicom_paths[0], nodule_locations, model_path)
    assert predicted
    assert 0 <= predicted[0]['p_concerning'] <= 1


def test_classify_real_nodule_small_dicom(dicom_path_003, model_path):
    predicted = trained_model.predict(dicom_path_003, [{'x': 302, 'y': 287, 'z': 12}], model_path)
    assert predicted
    assert 0.3 <= predicted[0]['p_concerning'] <= 1


def test_classify_real_nodule_full_dicom(dicom_paths, model_path):
    predicted = trained_model.predict(dicom_paths[2], [{'x': 302, 'y': 287, 'z': 187}], model_path)
    assert predicted
    assert 0.3 <= predicted[0]['p_concerning'] <= 1


def test_classify_luna(metaimage_path, luna_nodule, model_path):
    predicted = trained_model.predict(metaimage_path, [luna_nodule], model_path)
    assert predicted
    assert 0 <= predicted[0]['p_concerning'] <= 1
