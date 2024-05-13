import json
from typing import Dict
from tornado.concurrent import Future
from tornado.websocket import WebSocketHandler
from tornado.ioloop import PeriodicCallback
import numpy as np
import yarp
from sys import byteorder
from random import randint
from yarp import Sound
from numpy import int16, frombuffer
from datetime import datetime

class AudioOutHandler(WebSocketHandler):
    def initialize(self,network):
        self.callback = PeriodicCallback(self.periodic_call, 1000)

        self.sound = yarp.Sound()
    
        self.audio_buffer = []
        self.portIn = yarp.BufferedPortSound()
        self.portIn.open('/webAudio:i')
        self.network = network
        self.network.connect('/audioRecorder_nws/audio:o', '/webAudio:i')

    def periodic_call(self):
        self.sound = self.portIn.read()
        audioBuffer = np.array([self.sound.get(i) for i in range(self.sound.getSamples())]).astype(np.int16)

        self.write_message(audioBuffer.tobytes(), binary=True)

    def on_message(self, message):
        if message == "true":
            self.sound = self.portIn.read()
            config = {"numSamples": self.sound.getSamples(), "numChannels": self.sound.getChannels(), "frequency": self.sound.getFrequency()}
            self.write_message(json.dumps(config)) # to configure audio context

            self.callback.callback_time = (self.sound.getSamples() / self.sound.getFrequency()) * 1000
            self.callback.start()
        else:
            self.callback.stop()
