import argparse
import astropy.units as u
import numpy as np

import pwl_helpers as helpers
import noise_generators as ngen


@helpers.PWLGenerator
def noise(
    color: str,
    min_val: u.Quantity,
    max_val: u.Quantity,
    duration: u.Quantity,
    time_step: u.Quantity,
) -> tuple[
    u.Quantity, u.Quantity
]:
    color_func = ngen.COLORS[color.lower()]

    time_step = time_step << duration.unit
    nsamples = int( duration / time_step )
    times = np.arange(0, duration.value, time_step.value)[:nsamples] << time_step.unit
    values = color_func(nsamples)
    values = helpers.normalize_to_range(values, (min_val, max_val))

    return times, values


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
    noise(
        arg.col,
        arg.min << u.volt,
        arg.max << u.volt,
        arg.dur << u.second,
        arg.step << u.second
    )


if __name__ == '__main__':
    main()