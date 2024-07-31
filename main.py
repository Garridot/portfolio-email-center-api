from flask import Flask, request, jsonify, redirect
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from upstash_redis import Redis
from markupsafe import escape
from dotenv import load_dotenv
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import re
import os

# Load environment variables
load_dotenv()

# Flask application configuration
app = Flask(__name__)

app.config['MAIL_SERVER']   = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']     = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS']  = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL']  = os.getenv('MAIL_USE_SSL').lower() in ['true', '1', 't']

mail = Mail(app)

# Security and rate limiting configuration
PERSONAL_EMAIL = os.getenv('PERSONAL_EMAIL')
API_KEY = os.getenv('API_KEY')

# Configure Upstash Redis
UPSTASH_REDIS_REST_URL = os.getenv('UPSTASH_REDIS_REST_URL')
UPSTASH_REDIS_REST_TOKEN = os.getenv('UPSTASH_REDIS_REST_TOKEN')

redis_client = Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)

limiter = Limiter(
    key_func=get_remote_address,
    # app=app,
    storage_uri=UPSTASH_REDIS_REST_URL,
    strategy="fixed-window",
    default_limits=["200 per day", "50 per hour"],
    storage_options={"token": UPSTASH_REDIS_REST_TOKEN}
)

# Logging configuration
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Helper functions
def is_valid_email(email):
    """Validates if an email address is valid."""
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def require_api_key(f):
    """Decorator to require an API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key and key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({'error': 'Unauthorized access'}), 401
    return decorated_function

# Application routes
@app.route('/send_email_api', methods=['POST'])
@limiter.limit("5 per minute") 
@require_api_key
def send_email_api():
    """Handle the route to send emails."""

    app.logger.info('Request received from %s', request.remote_addr)

    data = request.get_json()  
    email = data.get('email')
    message = data.get('message')

    if not email or not message:
        return jsonify({'error': 'All fields are required.'}), 400  
    if not is_valid_email(email):
        return jsonify({'error': 'The email address is invalid.'}), 400      
    if len(message.strip()) == 0:   
        return jsonify({'error': 'The message cannot be empty.'}), 400 

    sanitized_message = escape(message)  

    try:
        msg = Message(
            f'Email from {email} via Email Center API',
            sender=os.getenv('MAIL_USERNAME'),
            recipients=[PERSONAL_EMAIL]
        )
        msg.body = sanitized_message
        mail.send(msg)
        return jsonify({'success': 'The email was sent successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500  

# Main to run the application
if __name__ == '__main__':
    app.run(debug=True)


