import os
import json
import sys
import django
from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
django.setup()

# Get the WSGI application
application = get_wsgi_application()

def handle_request(event, context):
    """
    Handle incoming HTTP requests and pass them to Django
    """
    # Get request data from environment variable
    request_file = os.environ.get('REQUEST_FILE')
    if not request_file or not os.path.exists(request_file):
        return {
            'statusCode': 500,
            'body': 'Request file not found'
        }
    
    # Read request data
    with open(request_file, 'r') as f:
        request_data = json.load(f)
    
    # Create a WSGI environment
    environ = {
        'REQUEST_METHOD': request_data.get('method', 'GET'),
        'PATH_INFO': request_data.get('path', '/'),
        'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in request_data.get('query', {}).items()]),
        'CONTENT_TYPE': request_data.get('headers', {}).get('content-type', ''),
        'CONTENT_LENGTH': str(len(str(request_data.get('body', '')))),
        'wsgi.version': (1, 0),
        'wsgi.input': sys.stdin,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Call Django application
    response = application(environ, lambda status, headers: None)
    
    # Extract response data
    status = response.status
    headers = dict(response.headers)
    body = b''.join(response).decode('utf-8')
    
    return {
        'statusCode': status,
        'headers': headers,
        'body': body
    } 