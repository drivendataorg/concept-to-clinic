"""
    prediction.src.tests.test_endpoints
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Provides unit tests for the API endpoints.
"""
from functools import partial
import json

import pytest

from flask import url_for
from src.factory import create_app
from src.algorithms import classify, identify, segment


def get_data(response):
    data = response.get_data(as_text=True)
    mimetype = response.headers.get('mimetype', '')
    content_type = response.headers.get('content-type', '')
    is_json = ('json' in mimetype) or ('json' in content_type)
    return json.loads(data) if is_json else data


@pytest.fixture
def dicom_path():
    return '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
           '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'


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


def test_indentify(client, dicom_path):
    url = client.url_for('predict', algorithm='identify')
    test_data = dict(dicom_path=dicom_path)

    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')

    data = get_data(r)

    assert isinstance(data['prediction'], list)
    assert data['prediction'][0]['x'] == 0


def test_classify(client, dicom_path):
    url = client.url_for('predict', algorithm='classify')
    test_data = dict(dicom_path=dicom_path, centroids=[])

    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')

    data = get_data(r)

    assert isinstance(data['prediction'], list)


def test_segment(client, dicom_path):
    url = client.url_for('predict', algorithm='segment')
    test_data = dict(dicom_path=dicom_path, centroids=[])

    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')

    data = get_data(r)

    assert isinstance(data['prediction']['binary_mask_path'], str)
    assert isinstance(data['prediction']['volumes'], list)


def test_bad_algorithm(client):
    url = client.url_for('predict', algorithm='blahblah')
    r = client.get(url)
    data = get_data(r)
    assert r.status_code == 500
    assert "'blahblah' is not a valid algorithm" in data['error']


def test_wrong_parameter(client):
    # dicom_path missing
    url = client.url_for('predict', algorithm='identify')
    test_data = dict()
    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')
    data = get_data(r)
    assert r.status_code == 500
    assert "'dicom_path'" in data['error']

    # centroids missing
    url = client.url_for('predict', algorithm='segment')
    test_data = dict(dicom_path='')
    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')
    data = get_data(r)
    assert r.status_code == 500
    assert "'centroids'" in data['error']

    # centroids unnecessary
    url = client.url_for('predict', algorithm='identify')
    test_data = dict(dicom_path='', centroids=[])
    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')
    data = get_data(r)
    assert r.status_code == 500
    assert "'centroids'" in data['error']


# test that other errors are passed through the API
def test_other_error(client):
    url = client.url_for('predict', algorithm='identify')
    # non-existent dicom path as example
    test_data = dict(dicom_path='/')
    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')
    data = get_data(r)
    assert r.status_code == 500
    assert "The path doesn't contain neither .mhd nor .dcm files" in data['error']
