from ..algorithms.classify.src.lr3dcnn.model import Model
import os


def test_classify_init_load(models_dir_path):
    model = Model(init_model=True, pull_size=10, batch_size=32, data_format=None)
    assert model is not None
    model = Model(
        init_model=os.path.join(models_dir_path, 'model.h5'),
        pull_size=10,
        batch_size=1,
        data_format=None
    )
    assert model is not None


def test_classify_predict(dicom_paths, nodule_locations, models_dir_path):
    model = Model(
        init_model=os.path.join(models_dir_path, 'model.h5'),
        pull_size=10,
        batch_size=1,
        data_format=None
    )
    candidates = [{'file_path': dicom_paths[0], 'centroids': [nl for nl in nodule_locations]}]
    predicted = model.predict(candidates)
    assert 0 <= predicted[0]['centroids'][0]['p_concerning'] <= 1


def test_classify_real_nodule_full_dicom(dicom_paths, models_dir_path):
    model = Model(
        init_model=os.path.join(models_dir_path, 'model.h5'),
        pull_size=10,
        batch_size=1,
        data_format=None
    )
    candidates = [{'file_path': dicom_paths[0], 'centroids': [{'x': 222, 'y': 259, 'z': 225}]}]
    predicted = model.predict(candidates)
    print(predicted)
    assert .3 <= predicted[0]['centroids'][0]['p_concerning'] <= 1
