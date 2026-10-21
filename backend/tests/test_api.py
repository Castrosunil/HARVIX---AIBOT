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

def test_natural_language_math_prompts():
    cases = [
        ('Solve the equation 2*x^2 - 5*x + 3 = 0.', '3/2'),
        ('Find the derivative of x^3.', '3*x**2'),
        ('Find the integral of x^2.', 'x**3/3'),
        ('Simplify (x + 2)^2 - x^2.', '4*x + 4'),
    ]
    for prompt, expected in cases:
        response = client.post('/api/chat', json={'message': prompt, 'mode': 'auto'})
        data = response.json()
        assert response.status_code == 200
        assert data['mode'] == 'math'
        assert expected in data['response']

def test_math_ignores_dashboard_text_around_equation():
    response = client.post('/api/chat', json={
        'message': 'HARVIX math\nMath result\nSolve the equation 2*x^2 - 5*x + 3 = 0.',
        'mode': 'math',
    })
    data = response.json()
    assert response.status_code == 200
    assert '[1, 3/2]' in data['response']
    assert 'HARVIX' not in data['response']

def test_chat_routes_coding():
    response = client.post('/api/chat', json={'message': 'Debug this Python function', 'mode': 'auto'})
    assert response.status_code == 200 and response.json()['mode'] == 'coding'

def test_chat_generates_basic_code():
    response = client.post('/api/chat', json={'message': 'Write a factorial program', 'mode': 'auto'})
    data = response.json()
    assert response.status_code == 200
    assert data['mode'] == 'coding'
    assert '```python' in data['reply'] and 'def factorial' in data['reply']

def test_chat_returns_structured_response_alias():
    response = client.post('/api/chat', json={'message': 'Create a Python program to find the largest number in an array.', 'mode': 'auto'})
    data = response.json()
    assert data['response'] == data['reply']
    assert 'largest_number' in data['response']

def test_chat_preserves_code_request_types():
    cases = [
        ('Write a Python program for binary search.', 'binary_search'),
        ('Give me a Java program for a linked list.', 'class Node'),
        ('Generate 10 test cases for this problem.', 'solve_case'),
    ]
    for prompt, expected in cases:
        data = client.post('/api/chat', json={'message': prompt, 'mode': 'auto'}).json()
        assert data['mode'] == 'coding'
        assert expected in data['reply']

def test_execute_python_returns_real_stdout_and_multiple_inputs():
    response = client.post('/api/execute', json={
        'language': 'python',
        'code': 'values = [int(line) for line in input().split()]\nprint(sum(values))',
        'stdin': '5 10 15',
    })
    data = response.json()
    assert response.status_code == 200
    assert data['success'] is True
    assert data['output'].strip() == '30'

def test_execute_python_reports_errors():
    response = client.post('/api/execute', json={'language': 'python', 'code': 'print(1 / 0)'})
    data = response.json()
    assert response.status_code == 200
    assert data['success'] is False
    assert 'ZeroDivisionError' in data['error']

def test_chat_run_request_returns_actual_output():
    response = client.post('/api/chat', json={
        'message': 'Run this program:\n```python\nprint(10)\n```\nInput: 10',
        'mode': 'auto',
    })
    data = response.json()
    assert response.status_code == 200
    assert data['mode'] == 'coding'
    assert '10' in data['response']
    assert 'Execution result' in data['response']

def test_python_is_default_for_general_generation_requests():
    response = client.post('/api/chat', json={
        'message': 'Create a program to read a file and count the words.',
        'mode': 'auto',
    })
    data = response.json()
    assert response.status_code == 200
    assert data['mode'] == 'coding'
    assert '```python' in data['response']
    assert 'OPENAI_API_KEY' not in data['response']
