#!/usr/bin/env python3

import time
import random
import board
import argparse
from adafruit_dotstar import DotStar

def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("ledcount",
        help="Number of daisy-chained DotStar LEDs in strip",
        type=int)
    parser.add_argument("-b", "--brightness",
        help="Overall LED brightness (0.0-1.0)",
        default=1.0,
        type=float)
    parser.add_argument("-d", "--delay",
        help="Delay between color randomization (seconds)",
        default=0.1,
        type=float)
    opts = parser.parse_args()
    return (opts.ledcount, opts.brightness, opts.delay)

(ledcount, brightness, delay) = parse_cmdline()
leds = DotStar(board.SCK, board.MOSI, ledcount, brightness=brightness)

while True:
    for idx in range(ledcount):
        leds[idx] = (random.randrange(0,255),
                     random.randrange(0,255),
                     random.randrange(0,255))

    time.sleep(delay)

