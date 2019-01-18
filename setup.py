import os
from setuptools import setup

setup(
    name = "dotstardemo",
    version = "0.0.1",
    author = "Magnus Olsson",
    author_email = "magnus@minimum.se",
    description = ("Adafruit DotStar Demo"),
    scripts=['scripts/led_random.py', 'scripts/led_powermate.py'],
    install_requires=['Adafruit-CircuitPython-DotStar', 'pypowermate']
)

