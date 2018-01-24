from ..algorithms.classify.src.lr3dcnn.model import Model


def test_classify_init_load(models_dir_path):
    model = Model(init_model=True, pull_size=10, batch_size=32, data_format=None)
    assert model is not None
    model = Model(init_model=models_dir_path, pull_size=10, batch_size=32, data_format=None)
    assert model is not None

# def test_classify_dicom(dicom_paths, nodule_locations, model_path):
#     predicted = trained_model.predict(dicom_paths[0], nodule_locations, model_path)
#     assert predicted
#     assert 0 <= predicted[0]['p_concerning'] <= 1
#
#
# def test_classify_real_nodule_small_dicom(dicom_path_003, model_path):
#     predicted = trained_model.predict(dicom_path_003, [{'x': 369, 'y': 350, 'z': 5}], model_path)
#     assert predicted
#     assert 0.3 <= predicted[0]['p_concerning'] <= 1
#
#
# def test_classify_real_nodule_full_dicom(dicom_paths, model_path):
#     predicted = trained_model.predict(dicom_paths[2], [{'x': 367, 'y': 349, 'z': 75}], model_path)
#     assert predicted
#     assert 0.3 <= predicted[0]['p_concerning'] <= 1
#
#
# def test_classify_luna(metaimage_path, luna_nodule, model_path):
#     predicted = trained_model.predict(metaimage_path, [luna_nodule], model_path)
#     assert predicted
#     assert 0 <= predicted[0]['p_concerning'] <= 1
