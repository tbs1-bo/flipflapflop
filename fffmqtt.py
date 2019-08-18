# TODO add service discovery for mqtt
# https://github.com/jstasiak/python-zeroconf/blob/master/README.rst

import paho.mqtt.client
import configuration
import displayprovider

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
        self.mqtt.connect(broker)
        self.topic_display = topic_display
        self.topic_info = topic_info
        self.fdd = fdd

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:  # connection successful
            print("Connected. Subscribing to topic", self.topic_display)
            self.mqtt.subscribe(self.topic_display)
        else:
            print("Unable to connect. error", rc)

        # publishing info about the display
        self.mqtt.publish(self.topic_info+'/width', self.fdd.width, retain=True)
        self.mqtt.publish(self.topic_info+'/height', self.fdd.height, retain=True)
        infotxt = 'Send pixel information to topic "%s".' % self.topic_display
        self.mqtt.publish(self.topic_info+'/info', infotxt, retain=True)

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
    
    def show(self):
        payload = ''.join(self.buffer)
        self.mqtt.publish(self.topic, payload)
        #self.mqtt.loop()

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
    try:
        print("Starting demo. Press crtl-c to stop.")
        demo.run()
    except KeyboardInterrupt:
        print("Demo finished")


if __name__ == '__main__':
    test_rotating_plasma()
