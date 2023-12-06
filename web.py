'''
Web-Interface for the display.

Start with

    $ FLASK_APP=web.py
    $ flask run --host=0.0.0.0

Use FLASK_ENV=development for a development server.

The webserver provides an address at location '/px/<x>/<y>/<on or off>' with
coordinate values for <x> and <y> and a status value for <on or off> which
must "on" or "off". You can send a GET or POST request to this addres.

For instance to turn pixel at location (2,3) on you can use

    $ curl HOSTNAME/px/2/3/on

Route /page can be read with method GET or changed with methode POST.

/page (GET) returns a list of 1s and 0s the represent the current display.

/page (POST) expects a parameter data of 1s and 0s to change the current 
display. Entries with x are ignored and allow for partial updates of the
display.

'''

from flask import Flask, request, render_template
import displayprovider
import configuration
import flipdotfont

app = Flask(__name__)

def get_display():
    if 'display' not in app.config:
        app.config['display'] = displayprovider.get_display()
    
    return app.config['display']

def get_buffer():
    if 'buffer' not in app.config:
        buffersize = get_display().width * get_display().height
        app.config['buffer'] = [False] * buffersize

    return app.config['buffer']

def set_px(x, y, val):
    get_display().px(x, y, val)

    # update buffer
    buffer = get_buffer()
    buffer[y * get_display().width + x] = val

@app.route('/')
def route_index():
    display = get_display()
    dimension = str(display.width) + ' x ' + str(display.height)
    return render_template(
        'index.html',
        dimension=dimension,
        web_conference_url=configuration.web_conference_url)

@app.route('/px/<int:x>/<int:y>/<string:onoff>', methods=['GET', 'POST'])
def route_px(x, y, onoff):
    display = get_display()
    if not(0 <= x < display.width):
        return 'x too big', 400
    if not(0 <= y < display.height):
        return 'y too big', 400

    if onoff == 'on':
        set_px(x, y, True)
        display.show()
    elif onoff == 'off':
        set_px(x, y, False)
        display.show()
    else:
        return 'value must be "on" or "off"', 400

    return 'ok', 200

@app.route('/txt', methods=['POST'])
def route_txt_post():
    txt = request.get_data(as_text=True)

    display = get_display()
    flipdotfont.TextScroller(display, txt, flipdotfont.small_font())

    display.show()
    return f'ok', 200

@app.route('/page', methods=['POST'])
def route_page_post():
    display = get_display()

    data = request.get_data(as_text=True)

    x, y = 0, 0
    for d in data:
        if d == '1':
            onoff = True
        elif d == '0':
            onoff = False
        elif d in ['x', 'X']:
            onoff = None
        else:
            return 'data must be 0 or 1 or x', 400

        if onoff is not None:
            if 0 <= x < display.width and 0 <= y < display.height:
                set_px(x, y, onoff)
            else:
                return 'image too big', 400

        if x+1 < display.width:
            x += 1
        else:
            y += 1
            x = 0

    display.show()
    return 'ok', 200

# TODO Splitting the display into areas /page1, /page2, ...
@app.route('/page', methods=['GET'])
def route_page_get():
    response = ''
    for b in get_buffer():
        response += '1' if b else '0'

    return response, 200

def test_px():
    client = app.test_client()

    for onoff in ['on', 'off']:
        for x,y in [(3,5), (11,9)]:
            resp = client.get('/px/{x}/{y}/{onoff}'.format(x=x, y=y, onoff=onoff))
            assert resp.status_code == 200
            assert resp.data == b'ok'
    
    resp = client.get('px/1000/1000/on')
    assert resp.status_code == 400

def test_page():
    client = app.test_client()

    resp = client.post('/page', data={'data':'000abc'})
    assert resp.status_code == 400

    resp = client.get('/page')
    assert resp.data[:9] == b'000000000'

    resp = client.post('/page', data={'data':'110110110'})
    assert resp.status_code == 200

    resp = client.get('/page')
    assert resp.data[:9] == b'110110110'
    assert resp.data[-9:] == b'000000000'

    resp = client.post('/page', data={'data': '000xxxXXx'})
    assert resp.status_code == 200
    resp = client.get('/page')
    assert resp.data[:9] == b'000110110'
    assert resp.data[-9:] == b'000000000'

def test_index():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200

def test_plasmademo():
    from math import sin, cos

    client = app.test_client()
    display = get_display()

    ticks = 0
    frames = 100
    for _ in range(frames):
        payload = ''
        for y in range(display.height):
            for x in range(display.width):
                ticks += 0.001
                s = sin(ticks / 50.0) * 2.0 + 6.0
                v = 0.3 + (0.3 * sin((x * s) + ticks / 4.0) *
                        cos((y * s) + ticks / 4.0))
                show_px = v > 0.3
                payload += '1' if show_px else '0'
                
        client.post('/page', data={'data': payload})

def test_plasmademo_remote():
    from math import sin, cos
    from urllib.request import urlopen
    import os

    if 'FFF_IP' in os.environ:
        host = 'http://' + os.environ['FFF_IP']
    else:
        print('No Public ip given in FFF_IP. Ignoring test.')
        return

    width, height = 28, 13
    ticks = 0
    frames = 100
    for _ in range(frames):
        payload = ''
        for y in range(height):
            for x in range(width):
                ticks += 0.005
                s = sin(ticks / 50.0) * 2.0 + 6.0
                v = 0.3 + (0.3 * sin((x * s) + ticks / 4.0) *
                        cos((y * s) + ticks / 4.0))
                show_px = v > 0.3
                payload += '1' if show_px else '0'

        urlopen(host + '/page', data=('data=' + payload).encode())
