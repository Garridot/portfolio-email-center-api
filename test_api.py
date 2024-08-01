import os
import pytest
from flask import json
from main import app  

API_KEY = os.getenv('API_KEY')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_send_email_api_success(client):
    headers = {'x-api-key': API_KEY}
    data = {
        'email': 'test@example.com',
        'message': 'This is a test message.'
    }
    response = client.post('/send_email_api', headers=headers, data=json.dumps(data), content_type='application/json')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['success'] == 'The email was sent successfully.'

def test_send_email_api_missing_fields(client):
    headers = {'x-api-key': API_KEY}
    data = {
        'email': 'test@example.com'
    }
    response = client.post('/send_email_api', headers=headers, data=json.dumps(data), content_type='application/json')
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data['error'] == 'All fields are required.'

def test_send_email_api_invalid_email(client):
    headers = {'x-api-key': API_KEY}
    data = {
        'email': 'invalid-email',
        'message': 'This is a test message.'
    }
    response = client.post('/send_email_api', headers=headers, data=json.dumps(data), content_type='application/json')
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data['error'] == 'The email address is invalid.'

def test_send_email_api_empty_message(client):
    headers = {'x-api-key': API_KEY}
    data = {
        'email': 'test@example.com',
        'message': ' '
    }
    response = client.post('/send_email_api', headers=headers, data=json.dumps(data), content_type='application/json')
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data['error'] == 'The message cannot be empty.'

def test_send_email_api_unauthorized(client):
    data = {
        'email': 'test@example.com',
        'message': 'This is a test message.'
    }
    response = client.post('/send_email_api', data=json.dumps(data), content_type='application/json')
    json_data = response.get_json()
    assert response.status_code == 401
    assert json_data['error'] == 'Unauthorized access'
