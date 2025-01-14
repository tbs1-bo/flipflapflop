'''
Web-Interface for the display.

Start with

    $ flask --app web.py run --host=0.0.0.0

Use FLASK_ENV=development for a development server.

The webserver provides an address at location '/px/<x>/<y>/<on or off>' with
coordinate values for <x> and <y> and a status value for <on or off> which
must "on" or "off". You can send a GET or POST request to this addres.

For instance to turn pixel at location (2,3) on you can use

    $ curl HOSTNAME/px/2/3/on

Route /page can be read with method GET or changed with method POST.

/page (GET) returns a list of 1s and 0s that represent the current display.

/page (POST) expects a parameter data of 1s and 0s to change the current 
display. Entries with x are ignored and allow for partial updates of the
display.

/display (GET) returns the current display as JSON.

/display (POST) expects a JSON with a single image or a list of images to 
display. Each image is a dictionary with the keys "pixels" and "duration_ms".
The value of "pixels" is a string of 0s and 1s. The value of "duration_ms" is
the duration of the image in milliseconds. For instance::    

        {
            "images": [
                {   
                    "pixels": "000011x0...",  # values of x are ignored
                    "duration_ms": 1000
                },
                ...
            ]            
        }

To show text, send a json with the text::
    
        {
            "text": "Hello World",
            "scrolling": true,     (optional, default false)
            "fps": 10,             (optional, default 10)
            "duration_ms": 1000    (optional, default 1000)
        }

'''

from flask import Flask, request, render_template
import displayprovider
import configuration
import flipdotfont
import time

app = Flask(__name__)

def get_display():
    if 'display' not in app.config:
        app.config['display'] = displayprovider.get_display(width=configuration.WIDTH, height=configuration.HEIGHT)
    
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
        dimension=dimension)

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

def _display_text(txt, scrolling=False, fps=10, duration_ms=1000):
    "Display text on display."
    display = get_display()
    scroller = flipdotfont.TextScroller(display, txt, flipdotfont.small_font())
    if duration_ms > configuration.web_max_show_time_ms:
        return "duration too long", 400
    if fps < 0:
        return "fps must be positive", 400    

    if scrolling:
        start = time.time()
        while True:
            scroller.scrolltext()
            display.show()
            time.sleep(1/fps)
            if time.time() - start > duration_ms / 1000:
                break
    else:
        display.show()

    return "ok", 200

@app.route('/page', methods=['POST'])
def route_page_post():
    data = request.get_data(as_text=True)
    return _show(data)

def _show(data):
    "Show data (string of 0s and 1s) on the display)."
    display = get_display()
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

def _show_sequence(list_of_images):
    "Show a sequence of images."
    showtime_ms = 0
    for image in list_of_images:
        showtime_ms += image["duration_ms"]
        if showtime_ms > configuration.web_max_show_time_ms:
            return "overall duration_ms too long", 400
        
        desc, code = _show(image["pixels"])
        if code != 200:
            return "Error in image: " + desc, code
        time.sleep(image["duration_ms"] / 1000)

    return "ok", 200

@app.route('/page', methods=['GET'])
def route_page_get():
    "Return the current display as string of 0s and 1s."
    response = ''
    for b in get_buffer():
        response += '1' if b else '0'

    return response, 200

@app.route("/display", methods=['GET'])
def route_display_get():
    "Return the current display (in JSON): width, height, data"
    pixels = ""
    for b in get_buffer():
        pixels += "1" if b else "0"
    js = {
        "width": get_display().width,
        "height": get_display().height,
        "pixels": pixels
    }
    return js, 200

@app.route("/display", methods=['POST'])
def route_display_post():    
    """
    Send a new display. Expecting json of the form::

        {
            "pixels": "00001100..."
        }

    To send a sequence of images, send a list of images including duration in 
    ms::

        {
            "images": [
                {   
                    "pixels": "00001100...",
                    "duration_ms": 1000
                },
                ...
            ]
        }

    To show text, send a json with the text::

        {
            "text": "Hello World",
            "scrolling": true,     (optional, default false)
            "fps": 10,             (optional, default 10)
            "duration_ms": 1000    (optional, default 1000)
        }

    To set the led brightness, send a json with the led value::
    
        {
            "led": "on"  # or "off"
        }
    
    """
    data = request.get_json()

    if "pixels" in data:
        return _show(data["pixels"])
    if "images" in data:        
        return _show_sequence(data["images"])
    if "text" in data:
        return _display_text(data["text"], 
                      data.get("scrolling", False), 
                      data.get("fps", 10), 
                      data.get("duration_ms", 1000))
    if "led" in data:
        return _set_led(data["led"])
    
    return "no text, pixels, led brightness or images in json", 400

def _set_led(onoff):
    "Set led on or off."
    if onoff not in ["on", "off"]:
        return "led must be on or off", 400

    get_display().led(onoff == "on")
    return "ok", 200

def test_display_get():
    client = app.test_client()
    response = client.get("/display")
    assert response.status_code == 200
    js = response.get_json()
    assert "width" in js
    assert int(js["width"]) == configuration.WIDTH
    assert "height" in js
    assert int(js["height"]) == configuration.HEIGHT

    for d in js["pixels"]:
        assert d in ["0", "1"]

def test_display_post():
    client = app.test_client()
    pixels = "00001100"
    response = client.post("/display", json={"pixels": pixels})
    assert response.status_code == 200
    js = client.get("/display").json

    assert js["pixels"][0:len(pixels)] == pixels

    # sequence of images
    images = []
    for pxs in ["00001100", "11110000", "00000000"]:
        images.append({"pixels": pxs, "duration_ms": 100})

    response = client.post("/display", json={"images": images})
    assert response.status_code == 200

    # too many images
    old_config_value = configuration.web_max_show_time_ms
    configuration.web_max_show_time_ms = 100
    images = []
    for pxs in ["00001100", "11110000", "00000000"]:
        images.append({"pixels": pxs, "duration_ms": 1000})
    response = client.post("/display", json={"images": images})
    assert response.status_code == 400, response.get_data(as_text=True)
    configuration.web_max_show_time_ms = old_config_value

    # show text
    response = client.post("/display", json={"text": "Hello World"})
    assert response.status_code == 200, response.get_data(as_text=True)
    response = client.post("/display", 
        json={
            "text": "Hello World", 
            "scrolling": True,
            "fps": 10,
            "duration_ms": 1000})
    assert response.status_code == 200, response.get_data(as_text=True)

    # set led brightness
    for onoff in ("on", "off"):
        response = client.post("/display", json={"led": onoff})
        assert response.status_code == 200, response.get_data(as_text=True)

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

    resp = client.post('/page', data='000abc')
    assert resp.status_code == 400

    resp = client.post('/page', data='000000')
    assert resp.status_code == 200

    resp = client.get('/page')
    assert resp.data[:9] == b'000000000', resp.data

    resp = client.post('/page', data='110110110')
    assert resp.status_code == 200

    resp = client.get('/page')
    assert resp.data[:9] == b'110110110'
    assert resp.data[-9:] == b'000000000'

    resp = client.post('/page', data='000xxxXXx')
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
