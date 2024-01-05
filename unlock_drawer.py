import subprocess
import database

import RPi.GPIO as GPIO
import time

from enum import Enum

class Shelf(Enum):
    TOP = 16
    MIDDLE = 20
    BOTTOM = 21

def unlock_shelf(shelf):
    print("Unlocking shelf")

    # Set up GPIO using BCM numbering
    GPIO.setmode(GPIO.BCM)

    # Set up pin 26 as an output
    GPIO.setup(shelf.value, GPIO.OUT)

    # Turn on GPIO 26
    GPIO.output(shelf.value, True)

    # Wait for 20 seconds
    time.sleep(20)

    # Turn off GPIO 26
    GPIO.output(shelf.value, False)

    # Clean up GPIO
    GPIO.cleanup()

def unlock_all():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Shelf.TOP.value, GPIO.OUT)
    GPIO.setup(Shelf.MIDDLE.value, GPIO.OUT)
    GPIO.setup(Shelf.BOTTOM.value, GPIO.OUT)

    GPIO.output(Shelf.TOP.value, True)
    GPIO.output(Shelf.MIDDLE.value, True)
    GPIO.output(Shelf.BOTTOM.value, True)

    time.sleep(30) #300: 5 minutes

    GPIO.output(Shelf.TOP.value, False)
    GPIO.output(Shelf.MIDDLE.value, False)
    GPIO.output(Shelf.BOTTOM.value, False)

    GPIO.cleanup()
