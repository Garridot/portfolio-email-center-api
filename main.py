from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import re

from dotenv import load_dotenv
import os

load_dotenv() # take environment variables from .env.

app = Flask(__name__)

app.config['MAIL_SERVER']   = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']     = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS']  = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL']  = os.getenv('MAIL_USE_SSL').lower() in ['true', '1', 't']

mail = Mail(app)

def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

@app.route('/send_email_api', methods=['POST'])
def send_email_api():
    data    = request.get_json()  
    email   = data.get('email')
    message = data.get('message')

    if not email or not message:
        return jsonify({'error': 'All fields are required.'}), 400  

    if not is_valid_email(email):
        return jsonify({'error': 'The email address is invalid.'}), 400      

    if len(message.strip()) == 0:   
        return jsonify({'error': 'The message cannot be empty.'}), 400    


    try:
        msg = Message(
            f'Email from {email}',
            sender="darden246@gmail.com",
            recipients=["garridot210@gmail.com"]
        )
        msg.body = message
        mail.send(msg)
        return jsonify({'success': 'The email was sent successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500        

if __name__ == '__main__':
    app.run(debug=True)

