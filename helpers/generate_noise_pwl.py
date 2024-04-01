import argparse
import astropy.units as u
import numpy as np

import pwl_helpers as helpers


# PSD generator from: https://stackoverflow.com/a/67127726
def noise_psd(N, psd = lambda f: 1):
    X_white = np.fft.rfft(np.random.randn(N))
    S = psd(np.fft.rfftfreq(N))
    S = S / np.sqrt(np.mean(S**2)) # Normalize
    X_shaped = X_white * S
    return np.fft.irfft(X_shaped)


def PSDGenerator(func):
    return lambda N: noise_psd(N, func)


@PSDGenerator
def white_noise(f):
    return 1


@PSDGenerator
def blue_noise(f):
    return np.sqrt(f)


@PSDGenerator
def violet_noise(f):
    return f


@PSDGenerator
def brownian_noise(f):
    return 1/np.where(f == 0, float('inf'), f)


@PSDGenerator
def pink_noise(f):
    return 1/np.where(f == 0, float('inf'), np.sqrt(f))


@PSDGenerator
def baby_pink_noise(f):
    return 1/np.where(f == 0, float('inf'), f**(1/3))


COLORS = {}
for key, value in list(locals().items()):
    if callable(value) and key.endswith('_noise'):
        name = key.split('_noise')[0]
        COLORS[name] = value


@helpers.PWLGenerator
def noise(
    color: str,
    min_val: u.Quantity,
    max_val: u.Quantity,
    duration: u.Quantity,
    time_step: u.Quantity,
) -> tuple[u.Quantity, u.Quantity]:
    
    color = color.lower()
    try:
        color_func = COLORS[color]
    except KeyError as e:
        raise ValueError(
            f'Noise color \'{color}\' not supported. '
            f'Try the following {list(COLORS.keys())} or add your own.'
        )

    time_step = time_step << duration.unit
    nsamples = int( duration / time_step )
    times = np.arange(0, duration.value, time_step.value)[:nsamples] << time_step.unit
    values = color_func(nsamples)
    values = helpers.normalize_to_range(values, (min_val, max_val))

    return times, values


"""@helpers.PWLGenerator
def white_noise(
    min_val: u.Quantity,
    max_val: u.Quantity,
    duration: u.Quantity,
    time_step: u.Quantity,
) -> tuple[u.Quantity, u.Quantity]:
    
    time_step = time_step << duration.unit
    nsamples = int( duration / time_step )
    times = np.arange(0, duration.value, time_step.value)[:nsamples] << time_step.unit
    noise = helpers.white_noise(nsamples, min_val, max_val)

    return times, noise"""


def main():

    parser = argparse.ArgumentParser(
        description='Generates a PWL file of colored noise for use in LTSpice\'s PWL voltage source.',
        epilog='Example of use: python generate_noise_pwl.py --col white --min -1 --max 1 --dur 1 --step 1e-3'
    )
    parser.add_argument('--col', type=str, help=f'noise color, supported: {list(COLORS.keys())}')
    parser.add_argument('--min', type=float, help='min noise amplitude, in volts')
    parser.add_argument('--max', type=float, help='max noise amplitude, in volts')
    parser.add_argument('--dur', type=float, help='duration, in seconds')
    parser.add_argument('--step', type=float, help='time step, in seconds')
    
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