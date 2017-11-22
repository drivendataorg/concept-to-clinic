"""
    prediction.src.tests.test_endpoints
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Provides unit tests for the API endpoints.
"""
import json

from functools import partial

import pytest

from flask import url_for
from src.algorithms import classify, identify, segment
from src.factory import create_app


def get_data(response):
    data = response.get_data(as_text=True)
    mimetype = response.headers.get('mimetype', '')
    content_type = response.headers.get('content-type', '')
    is_json = ('json' in mimetype) or ('json' in content_type)
    return json.loads(data) if is_json else data


@pytest.fixture
def client(request):
    app = create_app(config_mode='Test')
    client = app.test_client()
    headers = {'Accept': 'application/json'}
    client.get = partial(client.get, headers=headers)

    def client_url_for(base, **kwargs):
        with app.test_request_context():
            return url_for('blueprint.{}'.format(base), **kwargs)

    client.url_for = client_url_for
    return client


def test_home(client):
    url = client.url_for('home')
    r = client.get(url)
    data = get_data(r)
    assert 'Welcome' in data['message']


def test_endpoint_documentation(client):
    docstrings = {
        'identify': identify.trained_model.predict.__doc__,
        'segment': segment.trained_model.predict.__doc__,
        'classify': classify.trained_model.predict.__doc__
    }

    for algorithm in ['identify', 'segment', 'classify']:
        url = client.url_for('predict', algorithm=algorithm)
        r = client.get(url)
        data = get_data(r)
        assert data['description'] == docstrings[algorithm]


@pytest.mark.stop_timeout
def test_identify(client, dicom_path, content_type):
    url = client.url_for('predict', algorithm='identify')
    test_data = {'dicom_path': dicom_path}
    r = client.post(url, data=json.dumps(test_data), content_type=content_type)
    data = get_data(r)
    assert 'prediction' in data
    assert data['prediction']

    for prediction in data['prediction']:
        assert (0.5 <= prediction['p_nodule'] < 1.0)
        assert all(prediction[pos] > 0 for pos in ['x', 'y', 'z'])


def test_classify(client, metaimage_path, luna_nodule, content_type):
    url = client.url_for('predict', algorithm='classify')
    test_data = {'dicom_path': metaimage_path, 'centroids': [luna_nodule]}
    r = client.post(url, data=json.dumps(test_data), content_type=content_type)
    data = get_data(r)
    assert 'prediction' in data
    assert data['prediction']
    assert 0 <= data['prediction'][0]['p_concerning'] <= 1


def test_segment(client, dicom_path, nodule_locations, content_type):
    url = client.url_for('predict', algorithm='segment')
    test_data = {'dicom_path': dicom_path, 'centroids': nodule_locations}
    r = client.post(url, data=json.dumps(test_data), content_type=content_type)
    data = get_data(r)
    assert 'prediction' in data
    assert isinstance(data['prediction']['binary_mask_path'], str)
    assert data['prediction']['volumes']
    assert data['prediction']['volumes'][0] > 0


def test_bad_algorithm(client):
    url = client.url_for('predict', algorithm='blahblah')
    r = client.get(url)
    data = get_data(r)
    assert r.status_code == 500
    assert "'blahblah' is not a valid algorithm" in data['error']


def test_wrong_parameter(client, content_type):
    # dicom_path missing
    url = client.url_for('predict', algorithm='identify')
    test_data = {}
    r = client.post(url, data=json.dumps(test_data), content_type=content_type)
    data = get_data(r)
    assert r.status_code == 500
    assert "'dicom_path'" in data['error']

    # centroids missing
    url = client.url_for('predict', algorithm='segment')
    test_data = {'dicom_path': ''}
    r = client.post(url, data=json.dumps(test_data), content_type=content_type)
    data = get_data(r)
    assert r.status_code == 500
    assert "'centroids'" in data['error']

    # centroids unnecessary
    url = client.url_for('predict', algorithm='identify')
    test_data = {'dicom_path': '', 'centroids': []}
    r = client.post(url, data=json.dumps(test_data), content_type=content_type)
    data = get_data(r)
    assert r.status_code == 500
    assert "'centroids'" in data['error']


# test that other errors are passed through the API
def test_other_error(client, content_type):
    url = client.url_for('predict', algorithm='identify')

    # non-existent dicom path as example
    test_data = {'dicom_path': '/'}
    r = client.post(url, data=json.dumps(test_data), content_type=content_type)
    data = get_data(r)
    assert r.status_code == 500

    message = "The path / doesn't contain any .mhd or .dcm files"
    assert message in data['error']
