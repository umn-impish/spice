import argparse
import astropy.units as u
import numpy as np
import random

import pwl_helpers as helpers


@helpers.PWLGenerator
def transient_spikes(
    duration: u.Quantity,
    amplitude: u.Quantity,
    width: u.Quantity = 1e-9 * u.second,
    num_spikes: int = None
) -> tuple[u.Quantity, u.Quantity]:
    """
    Generates transient spikes with values between [-ampltiude, +amplitude].
    """

    width = width << duration.unit
    if num_spikes is None:
        num_spikes = random.randint(50, 500)

    print(f'Generating PWL with {num_spikes} spikes with widths {width} over '\
          f'a duration {duration} and max amplitude {amplitude}')
    
    # We sample over duration - width * num_spikes so that we can rescale the
    # start array in order to prevent overlap in the pulses.
    starts = np.sort(np.random.uniform(0, duration.value - width.value * num_spikes, num_spikes))
    starts = starts + width.value * np.linspace(0, num_spikes-1, num_spikes)
    mids = starts + width.value / 2
    ends = mids + width.value / 2

    zeros = np.zeros(starts.shape)
    amplitudes = np.random.uniform(-amplitude.value, amplitude.value, len(starts))

    times = helpers.weave_arrays(starts, mids, ends, dtype=starts.dtype)
    voltages = helpers.weave_arrays(zeros, amplitudes, zeros, dtype=amplitudes.dtype)

    return times, voltages


def main():
    
    parser = argparse.ArgumentParser(
        description='Generates a PWL file containing transient voltage spikes for use in LTSpice\'s PWL voltage source.',
        epilog='Example of use: python generate_transient_spike_pwl.py --dur 1e-2 --amp 2 --wid 1e-9 --num 1000'
    )
    parser.add_argument('--dur', type=float, help='simulation duration, in seconds')
    parser.add_argument('--amp', type=float, help='max transient amplitude, in volts')
    parser.add_argument('--wid', type=float, default=1e-9, help='[optional] transient pulse width, in seconds')
    parser.add_argument('--num', type=int, default=None, help='[optional] number of transient spikes')

    arg = parser.parse_args()
    transient_spikes(
        arg.dur << u.second,
        arg.amp << u.volt,
        arg.wid << u.second,
        arg.num
    )


if __name__ == '__main__':
    main()