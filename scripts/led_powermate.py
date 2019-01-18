#!/usr/bin/env python3
''' DotStar demo using a powermate USB knob

Turning the knob adjusts the current color of the first LED in the strip. All
the other LEDs represent the "color history", creating a sort of snail trail
as you turn the knob.
'''

import argparse
import board
import time
from collections import deque
from pypowermate import Powermate, PowermateTimeoutException
from enum import IntEnum
from adafruit_dotstar import DotStar
from itertools import cycle

class CtrlMode(IntEnum):
    COLOR_R = 0
    COLOR_G = 1
    COLOR_B = 2
    BRIGHTNESS = 3
    SCROLL_SPEED = 4

SCROLL_STEP = 0.1
COLOR_STEP = 32
BRIGHTNESS_STEP = 0.1

def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("ledcount",
        help="Number of daisy-chained DotStar LEDs in strip",
        type=int)
    parser.add_argument("-p", "--powermate",
        help="Powermate device",
        default="/dev/input/by-id/usb-Griffin_Technology_Inc._Griffin_PowerMate-event-if00")
    opts = parser.parse_args()
    return (opts.ledcount, opts.powermate)

def bump(val, incr, minimum, maximum):
    val += incr
    return max(min(val, maximum), minimum)

def redraw_snailtrail(colors, leds):
    ''' Redraw all LEDs except the first '''

    colors = list(colors)
    if len(colors) < len(leds) - 1:
        # If we don't have full history yet, pad with unlit/black LEDs
        colors.extend([(0, 0, 0, 0.0)] * (len(leds) - len(colors) - 1))

    for idx in range(1, len(leds)):
        leds[idx] = colors[idx-1]

def redraw_current(current, leds):
    leds[0] = current

def update_current(old_value, mode, inc):
    new_value = list(old_value)
    if mode in [CtrlMode.COLOR_R, CtrlMode.COLOR_G, CtrlMode.COLOR_B]:
        new_value[mode] = bump(old_value[mode], inc*COLOR_STEP, 0, 255)
    elif mode == CtrlMode.BRIGHTNESS:
        new_value[mode] = bump(old_value[mode], inc*BRIGHTNESS_STEP, 0, 1.0)

    return tuple(new_value)


def main():
    (ledcount, path) = parse_cmdline()
    leds = DotStar(board.SCK, board.MOSI, ledcount, brightness=1.0)
    powermate = Powermate(path)
    cycler = cycle(map(int, CtrlMode))

    mode = next(cycler)
    history = deque(maxlen=ledcount-1)
    rate = 1.0

    last_update = time.time()
    current = [0, 0, 0, 1.0]
    while True:
        now = time.time()
        time_elapsed = now - last_update
        time_left = max(rate - time_elapsed, 0.01)
        if time_elapsed >= rate:
            # Push values of 1st LED to history and redraw snailtrail
            history.appendleft(current)
            redraw_snailtrail(history, leds)
            last_update = now

        try:
            (_, evt, inc) = powermate.read_event(time_left)
            if evt == 'button' and inc == 0:
                # Knob pressed, cycle mode
                mode = next(cycler)
                print("Control mode {}".format(mode))
            elif evt == 'rotate':
                if mode == CtrlMode.SCROLL_SPEED:
                    rate = bump(rate, inc*SCROLL_STEP, 0.0, 5.0)
                    print("Rate adjusted to {}".format(rate))
                else:
                    current = update_current(current, mode, inc)
                    redraw_current(current, leds)
                    print("LED adjusted to {}".format(current))
        except PowermateTimeoutException:
            pass

if __name__ == '__main__':
    main()