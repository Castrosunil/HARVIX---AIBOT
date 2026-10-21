from fastapi.testclient import TestClient
from backend.app.main import app
client = TestClient(app)

def test_health():
    response = client.get('/api/health')
    assert response.status_code == 200 and response.json()['status'] == 'ok'

def test_math_equation():
    response = client.post('/api/math', json={'expression': '2*x^2 - 5*x + 3 = 0'})
    assert response.status_code == 200
    assert '1' in response.json()['result'] and '3/2' in response.json()['result']

def test_chat_routes_coding():
    response = client.post('/api/chat', json={'message': 'Debug this Python function', 'mode': 'auto'})
    assert response.status_code == 200 and response.json()['mode'] == 'coding'

def test_chat_generates_basic_code():
    response = client.post('/api/chat', json={'message': 'Write a factorial program', 'mode': 'auto'})
    data = response.json()
    assert response.status_code == 200
    assert data['mode'] == 'coding'
    assert '```python' in data['reply'] and 'def factorial' in data['reply']
