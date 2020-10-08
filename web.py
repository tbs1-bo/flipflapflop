'''
Web-Interface for the display.

Start with
FLASK_APP=web.py
flask run --host=0.0.0.0

Use FLASK_ENV=development for a development server.

'''

from flask import Flask, request

app = Flask(__name__)
import displayprovider
import time

display = displayprovider.get_display()

@app.route('/')
def index():
    return 'ok'

@app.route('/px/<int:x>/<int:y>/<string:onoff>', methods=['GET', 'POST'])
def px(x, y, onoff):
    print(x, y, onoff)
    if onoff == 'on':
        display.px(x, y, True)
        display.show()
    elif onoff == 'off':
        display.px(x, y, False)
        display.show()
    else:
        return 'error'

    return 'ok'
