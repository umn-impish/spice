import argparse
from typing import Callable
import astropy.units as u
import numpy as np

from . import noise_generators as ngen
from . import generate_pwl_noise as gpn


def main():
    parser = argparse.ArgumentParser(
        description='Generates a PWL file of colored noise for use in LTSpice\'s PWL voltage source.',
        epilog='Example of use: python generate_noise_pwl.py --col white --min -1 --max 1 --dur 1 --step 1e-3'
    )
    parser.add_argument(
        '--col', type=str, help=f'noise color',
        choices=list(ngen.COLORS.keys()), required=True)
    parser.add_argument(
        '--min', type=float, help='min noise amplitude, in volts', required=True)
    parser.add_argument(
        '--max', type=float, help='max noise amplitude, in volts', required=True)
    parser.add_argument(
        '--dur', type=float, help='duration, in seconds', required=True)
    parser.add_argument(
        '--step', type=float, help='time step, in seconds', required=True)
    
    arg = parser.parse_args()
    gpn.noise(
        ngen.COLORS[arg.col.lower()],
        arg.min << u.volt,
        arg.max << u.volt,
        arg.dur << u.second,
        arg.step << u.second,
        name=arg.col.lower()
    )


if __name__ == '__main__':
    main()
