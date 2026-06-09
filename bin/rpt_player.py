from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
import os
import random

class Player():

    def __init__(self):
        base = os.path.join(os.path.dirname(__file__), "..", "assets")

        self.sounds = []

        for filename in [
            "samp1.wav",
            "samp2.wav",
            "samp3.wav",
            "samp4.wav",
            "samp5.wav",
        ]:
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(os.path.join(base, filename)))
            self.sounds.append(effect)

    def play_random(self):
        random.choice(self.sounds).play()

    def randomly_play_random(self, chance=1):
        if random.randint(1, chance) == 1:
            self.play_random()