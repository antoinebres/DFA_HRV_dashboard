# import paho.mqtt.subscribe as subscribe
# MQTT_BROKER = "broker.emqx.io"
# msg = subscribe.simple("demo/#", hostname=MQTT_BROKER)
# print("%s %s" % (msg.topic, msg.payload))

import paho.mqtt.client as mqtt_client
import json
from time import sleep

class Subscriber(object):
	"""docstring for Subscriber"""
	def __init__(self):
		# super(Subscriber, self).__init__()
		self.MQTT_BROKER = "broker.emqx.io"
		self.MQTT_PORT   = 1883
		self.KEEP_ALIVE  = 45
		self.client = mqtt_client.Client()
		self.RRs = []
		self.client.on_message = self._on_message
		self.client.on_connect = self._on_connect
		self.client.connect(host=self.MQTT_BROKER, port=self.MQTT_PORT, keepalive=self.KEEP_ALIVE)
		self.client.subscribe("35be6981-4190-48f5-8e33-80cccf71694d/hr")
		self.client.loop_start()

	def _on_connect(self, client, userdata, flags, rc):
	    print( "Connexion: code retour = %d" % rc )
	    print( "Connexion: Statut = %s" % ("OK" if rc==0 else "échec") )


	def _on_message(self, client, userdata, message):
		if 'rr' in json.loads(message.payload).keys():
			self.RRs.extend(json.loads(message.payload)['rr'])

	def get_RRs(self):
		return list(map(lambda x: x/1000, self.RRs))



if __name__ == '__main__':
	rr_sub = Subscriber()
	while True:
		print(rr_sub.get_RRs()[-5:])
		sleep(.5)

