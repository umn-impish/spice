import argparse
import os

import astropy.units as u
import numpy as np
import scipy.signal as sig

from . import noise_generators as ngen
from . import generate_pwl_noise as gpn

'''
This script takes a directory containing SiPM dark counts
(or otherwise noisy output) and resamples it statistically
to generate a spectrally-similar waveform.

Output is saved to current working directory in a folder called 'pwl'
'''

def main():
    parser = argparse.ArgumentParser(
        description='Generates a PWL file spectrally similar to '\
                    'SiPM noise for use in LTSpice\'s PWL voltage source.'
    )
    parser.add_argument(
        '-d', '--directory', type=str,
        help='directory containing oscilloscope CSV files of SiPM noise to resample',
        required=True)
    parser.add_argument(
        '-m', '--min', type=float, help='min noise amplitude, in volts', required=True)
    parser.add_argument(
        '-M', '--max', type=float, help='max noise amplitude, in volts', required=True)
    parser.add_argument(
        '-t', '--dur', type=float, help='duration, in seconds', required=True)
    parser.add_argument(
        '-s', '--step', type=float, help='time step, in seconds', required=True)
    
    args = parser.parse_args()
    noise_gen = resample_sipm_noise(args.directory)

    # Auto-saves file to current working dir
    gpn.noise(
        noise_gen,
        args.min << u.volt,
        args.max << u.volt,
        args.dur << u.s,
        args.step << u.s,
    )


def resample_sipm_noise(direc: str) -> None:
    '''
    Given a bunch of SiPM dark count files, we:
        - Estimate their power spectral density
        - Resample the PSD at random intervals
        - Filter white noise by the resampled PSD:
          Filtered(w) = White(w) * PSD(w)
          (which is equivalent to convolving the PSD with a delta function in the time domain
           via the convolution theorem)
        - Write out a file
    '''
    data, times = read_scope_data(direc)
    dt = (times[0, 1] - times[0, 0]) << u.s

    window = 'nuttall'
    f, psd = sig.welch(
        data,
        window=window,
        nfft=2400,
        axis=1
    )

    avg_psd = psd.mean(axis=0)
    assert avg_psd.size == f.size
    phys_frequency = (f / dt)
    sipm_noise_gen = ngen.arbitrary_noise_gen(
        frequencies=phys_frequency << u.Hz,
        psd=np.sqrt(avg_psd << u.one / u.Hz),
        time_step=dt
    )

    return sipm_noise_gen


def read_scope_data(fold: str) -> tuple[np.ndarray, np.ndarray]:
    '''Reads in oscilloscope data from a given directory into two big 2D arrays'''
    files = [f for f in os.listdir(fold) if f.endswith('.CSV')]
    all_data = []
    all_times = []
    for fn in files:
        with open(f'{fold}/{fn}') as f:
            # First 18 lines are garbargio so skip them
            [next(f) for _ in range(18)]
            t = []
            dat = []
            for line in f:
                splitted = line.split(',')
                t.append(float(splitted[3]))
                dat.append(float(splitted[4]))
        all_times.append(t)
        all_data.append(dat)

    return np.array(all_data), np.array(all_times)


if __name__ == '__main__':
    main()
