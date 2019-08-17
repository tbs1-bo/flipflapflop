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
        self.mqtt.connect(broker)
        self.mqtt.on_connect = self._on_connect
        self.mqtt.on_message = self._on_message
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

def demo():
    import flipdotsim
    fdd = flipdotsim.FlipDotSim()

    mqtt2disp = Mqtt2Display(BROKER, TOPIC_DISPLAY, TOPIC_INFO, fdd)
    mqtt2disp.run(background=False)


if __name__ == '__main__':
    demo()
