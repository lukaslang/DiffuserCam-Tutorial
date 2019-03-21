#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2019 Lukas F. Lang
#
# This script allows to capture a burst of images with different settings in
# order to figure out the best settings.
#
# See also the chapter "Capturing consistent images" in
# https://picamera.readthedocs.io/en/release-1.13/recipes1.html
import datetime
import fractions
import itertools as it
import os
import picamera
from time import sleep
from timeit import default_timer as timer
import sys

# Define framerate (check for flickering due to 50 Hz alternating current).
fr = fractions.Fraction(17, 1)

# Define resolution (this is MAX_RESOLUTION for v2 Pi camera).
res = (3280, 2464)

# Set a range of ISOs.
iso_rng = [100]

# Set a range of shutter speeds (docu says in microseconds).
shutter_rng = [1000, 2500, 5000, 10000]

# Set name.
name = 'raw'

# Set output folder.
folder = 'capture'

# Set format.
output_format = 'jpg'


def filename(name, iso, shutter_speed):
    return '{0}-{1}-{2}.{3}'.format(name, iso, shutter_speed, output_format)


if __name__ == '__main__':
    """Takes a burst of images and saves them to a folder.

    Args:
        name (str): Identifier used in name of files (optional).

    """
    # Set filename if provided as argument.
    if len(sys.argv) == 2:
        name = str(sys.argv[1])

    # Create output folder with timestamp.
    path = os.path.join(folder,
                        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    os.makedirs(path, exist_ok=True)

    print('Taking {} pictures.'.format(len(iso_rng) * len(shutter_rng)))
    with picamera.PiCamera(framerate=fr, resolution=res) as camera:

        # Start preview.
        camera.start_preview(resolution=(410, 313),
                             fullscreen=False,
                             window=(100, 100, 820, 616))

        # Initialise camera by setting ISO and shutter speed.
        camera.iso = iso_rng[0]
        sleep(2)
        camera.shutter_speed = shutter_rng[0]
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        print('Gains fixed to: {}'.format(g))

        for idx, p in enumerate(it.product(iso_rng, shutter_rng)):
            start_loop = timer()

            # Get settings.
            iso, shutter_speed = p
            print(('Setting ISO={}, ' +
                  'shutter speed={}').format(iso, shutter_speed))

            # Set ISO and shutter speed.
            camera.iso = iso
            camera.shutter_speed = shutter_speed

            # Capture image.
            start_capture = timer()
            camera.capture(os.path.join(path,
                                        filename(name, iso, shutter_speed)))
            end_loop = timer()
            print(('Capture took {0:.2f} s and iteration ' +
                   '{1:.2f} s.').format(end_loop - start_capture,
                                        end_loop - start_loop))

        camera.stop_preview()

        # Write settings to file.
        with open(os.path.join(path, 'params.txt'), 'w') as params_file:
            print('Exposure mode: {}'.format(camera.exposure_mode),
                  file=params_file)
            print('AWB mode: {}'.format(camera.awb_mode), file=params_file)
            print('Gains: {}'.format(g), file=params_file)
            print('ISOs: {}'.format(iso_rng), file=params_file)
            print('Shutter speeds: {}'.format(shutter_rng), file=params_file)

        print('Done.')
