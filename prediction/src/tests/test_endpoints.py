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


def test_identify(client):
    url = client.url_for('predict', algorithm='identify')

    test_data = dict(dicom_path='')

    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')

    data = get_data(r)

    assert isinstance(data['prediction'], list)
    assert data['prediction'][0]['x'] == 0


def test_classify(client):
    url = client.url_for('predict', algorithm='classify')
    test_data = dict(dicom_path='', centroids=[])

    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')

    data = get_data(r)

    assert isinstance(data['prediction'], list)


def test_segment(client):
    url = client.url_for('predict', algorithm='segment')
    test_data = dict(dicom_path='', centroids=[])

    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')

    data = get_data(r)

    assert isinstance(data['prediction']['binary_mask_path'], str)
    assert isinstance(data['prediction']['volumes'], list)


def test_error(client):
    url = client.url_for('predict', algorithm='classify')

    # missing centroids
    test_data = dict(dicom_path='')

    r = client.post(url,
                    data=json.dumps(test_data),
                    content_type='application/json')

    assert r.status_code == 500
