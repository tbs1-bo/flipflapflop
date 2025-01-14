import json
import paho.mqtt.client
import configuration
import displayprovider
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

BROKER = configuration.mqtt_broker
TOPIC_DISPLAY = configuration.mqtt_topic_display
TOPIC_INFO = configuration.mqtt_topic_info

class Mqtt2Display:    
    def __init__(self, broker, topic_display, topic_info, 
                 fdd: displayprovider.DisplayBase):
        '''
        Create a bridge that connects to the given broker, subscribes to the 
        given topic and displays string sequences of 1s and 0s that are 
        published to the topic_display on the given flipdotdisplay. An info 
        topic is used to publish information about the fdd display on connect.
        '''
        self.mqtt = paho.mqtt.client.Client()
        self.mqtt.on_connect = self._on_connect
        self.mqtt.on_message = self._on_message
        log.info(f"connecting to broker {broker}")
        self.mqtt.connect(broker)
        self.topic_display = topic_display
        self.topic_info = topic_info
        self.fdd = fdd

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:  # connection successful
            log.info(f"Connected. Subscribing to topic {self.topic_display}")
            self.mqtt.subscribe(self.topic_display)
        else:
            log.error(f"Unable to connect. error {rc}")

        # publishing info about the display
        log.info(f"publishing display info to topic {self.topic_info}")
        js = {
            'width': self.fdd.width,
            'height': self.fdd.height,
            'implementation class': self.fdd.__class__.__name__,
            'displaytopic': self.topic_display,
            'info': f'Send pixel information (1s and 0s) to topic {self.topic_display}'
        }
        self.mqtt.publish(self.topic_info, json.dumps(js), retain=True)

    def _on_message(self, client, userdata, msg: paho.mqtt.client.MQTTMessage):
        self.draw_on_display(str(msg.payload, 'ascii'))

    def draw_on_display(self, pixels):
        self.fdd.clear()
        for x in range(self.fdd.width):
            for y in range(self.fdd.height):
                index = y * self.fdd.width + x
                if index >= len(pixels):
                    break  # too few pixels received

                pixel = pixels[index]

                if pixel == '1':
                    self.fdd.px(x, y, True)
                elif pixel == '0':
                    self.fdd.px(x, y, False)
                # ignoring other pixel data

        self.fdd.show()

    def run(self, background=True):
        'Start the network loop in background (non blocking) or foreground (blocking).'

        if background:
            self.mqtt.loop_start()
        else:
            self.mqtt.loop_forever()

class MqttDisplay(displayprovider.DisplayBase):
    '''
    A Display that sends all data into a topic of an MQTT broker.

    >>> import fffmqtt
    >>> fdd = fffmqtt.MqttDisplay(width=2,height=3, 
    ...     broker='test.mosquitto.org', topic='display')
    connecting to broker test.mosquitto.org

    >>> fdd.clear()
    >>> fdd.px(1,1,True)

    The next line finally sends all data to the topic inside the broker.

    >>> fdd.show()
    '''
    def __init__(self, width, height, broker, topic):
        '''A display that connects to a broker and publishes pixel data
        encoded as string of 1s and 0s into the given topic.
        '''
        super().__init__(width, height)

        self.topic = topic
        self.mqtt = paho.mqtt.client.Client()
        print('connecting to broker', broker)
        self.mqtt.connect(broker)
        self.buffer = ['0'] * (width * height)

    def px(self, x, y, val):
        index = y * self.width + x
        self.buffer[index] = '1' if val else '0'

    def is_px(self, x, y):
        return self.buffer[y * self.width + x] == '1'
    
    def show(self):
        payload = ''.join(self.buffer)
        self.mqtt.publish(self.topic, payload)
        #self.mqtt.loop()

class MqttTasmotaDisplay(MqttDisplay):
    '''Linear (i.e. one dimensionbal) Display that sends information to an MQTT
    broker respecting the tasmota topic format.

    https://github.com/arendst/Sonoff-Tasmota/wiki/commands#light
    https://github.com/arendst/Sonoff-Tasmota/wiki/commands#using-backlog
    '''

    def __init__(self, width, broker, cmnd_base_topic):
        super().__init__(width, height=1, broker=broker, topic=cmnd_base_topic)
        self.mqtt.publish(cmnd_base_topic + '/PIXELS', width)

    def show(self):
        'Will send LEDx #RRGGBB commands in form of BACKLOG command.'

        backlog = ''
        for i in range(len(self.buffer)):
            if self.is_px(i, 0):
                payload = 'ff0000'
            else:
                payload = '000000'

            backlog += 'led%s %s;' % (i+1, payload)

        print("sending payload ", len(backlog))
        self.mqtt.publish(self.topic + "/BACKLOG", backlog)

def test_tasmota_display():
    num_leds = 4
    fff = MqttTasmotaDisplay(num_leds, 'test.mosquitto.org', 'cmnd/baksonoff')

    import time
    for i in range(num_leds):
        print("setting pixel", i)
        fff.clear()
        fff.px(i,0, True)
        fff.show()
        time.sleep(0.1)

def test_mqtt_display():
    import time
    import random

    def on_msg(client, userdata, msg:paho.mqtt.client.MQTTMessage):
        userdata['msg_recvd'] = True
        userdata['test_passed'] = str(msg.payload, 'ascii') == userdata['expected']

    broker = 'test.mosquitto.org'
    topic = 'mqttdisplay_t' + str(random.randint(1000,10000))

    mqtt = paho.mqtt.client.Client()
    mqtt.on_message = on_msg
    mqtt.connect(broker)
    mqtt.loop_start()
    mqtt.subscribe(topic)    

    fdd = MqttDisplay(width=2, height=3, broker=broker, topic=topic)

    for x1,y1,x2,y2,exp in [(0,0,1,1, '100100'),
                            (0,0,1,2, '100001'),
                            (0,0,1,0, '110000')]:
        fdd.clear()
        fdd.px(x1,y1, True)
        fdd.px(x2,y2, True)
        user_data = {'msg_recvd': False, 'expected': exp, 'test_passed': False}
        mqtt.user_data_set(user_data)
        fdd.show()

        time.sleep(1)
        assert user_data['msg_recvd']
        assert user_data['test_passed']

    mqtt.disconnect()


def test_rotating_plasma():
    # create simulator and let mqtt messages update the display
    import flipdotsim
    fdd_sim = flipdotsim.FlipDotSim(width=configuration.WIDTH, height=configuration.HEIGHT)
    mqtt2disp = Mqtt2Display(BROKER, TOPIC_DISPLAY, TOPIC_INFO, fdd_sim)
    mqtt2disp.run(background=True)

    # create mqttdisplay and let demo publish messages into the display topic
    import demos
    fdd_mqtt = MqttDisplay(configuration.WIDTH, configuration.HEIGHT, 
                           BROKER, TOPIC_DISPLAY)
    demo = demos.RotatingPlasmaDemo(fdd_mqtt)
    demo.run(runtime=2)

    fdd_sim.close()

def discover_mqtt_broker(timeout=5):
    '''Try to discover an MQTT broker on all interaces using zeroconf. 
    A timeout (in seconds) specifies how long to wait for an answer.
    An IPv4 adress is returned if a broker has been discovered. 
    '''

    import time
    import socket

    # https://github.com/jstasiak/python-zeroconf/blob/master/README.rst
    from zeroconf import ServiceBrowser, Zeroconf
    import zeroconf

    # helper class
    class OneServiceFinder:
        def __init__(self):
            self.service_info = None

        def add_service(self, zeroconf, type, name):
            if self.service_info is None:
                self.service_info = zeroconf.get_service_info(type, name)
                print("service found", self.service_info.name)

        def get_ip(self):
            if not self.service_found():
                return None

            # assuming IPv4
            return socket.inet_ntop(socket.AF_INET, self.service_info.addresses[0])

        def service_found(self):
            return self.service_info is not None

    start_time = time.time()

    zc = Zeroconf()
    listener = OneServiceFinder()
    # starts implicitly
    ServiceBrowser(zc, "_mqtt._tcp.local.", listener)

    waiting = True
    while waiting:
        if listener.service_found():
            waiting = False
        if time.time()-start_time > timeout:
            waiting = False

        time.sleep(0.1)

    zc.close()
    return listener.get_ip()

def test_discover_mqtt_broker():
    print("Searching Broker")    
    broker_ip = discover_mqtt_broker()
    if broker_ip:
        assert '.' in broker_ip, broker_ip
        print('service discovered:', broker_ip)

def main():
    fdd = displayprovider.get_display()
    log.info(f"using display {fdd.__class__.__name__} with size {fdd.width, fdd.height}")
    log.info("Starting bridge from MQTT broker to display")
    mqtt2disp = Mqtt2Display(BROKER, TOPIC_DISPLAY, TOPIC_INFO, fdd)
    mqtt2disp.run(background=False)

if __name__ == '__main__':
    main()
    #test_discover_mqtt_broker()
    #test_rotating_plasma()
