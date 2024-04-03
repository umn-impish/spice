import astropy.units as u
import multiprocessing as mp
import numpy as np
import time
import typing
import os


OUT_DIR = os.path.join(os.getcwd(), 'pwl')
os.makedirs(OUT_DIR, exist_ok=True)


def write_file(times: u.Quantity, values: u.Quantity, file_name: str):
    cols = np.vstack(((times<<u.second).value, (values<<u.volt).value)).T
    np.savetxt(os.path.join(OUT_DIR, file_name), cols)


def normalize_to_range(values: np.ndarray, range: tuple[float, float]) -> np.ndarray:
    """
    Renormalizes given values to the specified range (min, max).
    """

    min_val, max_val = range
    normed = ( values - values.min() ) / ( values.max() - values.min() ) # from 0 to 1
    
    return (max_val - min_val) * normed + min_val


def weave_arrays(
    *arrs: typing.Iterable[np.ndarray],
    dtype = object
) -> np.ndarray:
    """
    Weaves N 1-D arrays together into one array of length N * original length.
    Each array in arrs must have the same length.

    Example:
    a1 = [1, 3, 5]
    a2 = [2, 4, 6]
    weave_arrays(a1, a2) = [1, 2, 3, 4, 5, 6]

    This method is the most time efficient: https://stackoverflow.com/a/5347492
    """
    
    num_arrs = len(arrs)
    arr_length = len(arrs[0])

    # Enforce all arrays must be same length.
    for i in range(1, num_arrs):
        if len(arrs[i]) != arr_length:
            raise ValueError('All arrays must have the same length '\
                             'in order to be woven together.')

    woven = np.empty((num_arrs * arr_length,), dtype=dtype)
    for i in range(num_arrs):
        woven[i::num_arrs] = arrs[i]
    
    return woven


def _white_noise_helper(size: int):
    """
    Old.
    A different seed is needed for each process.
    """

    np.random.seed((os.getpid() * int(time.time())) % 123456789)
    return np.random.random_sample(size)


def white_noise(nsamples: int, min_val: u.Quantity = 0, max_val: u.Quantity = 1) -> u.Quantity:
    """
    Old.
    Generates nsamples of white noise over the interval [min_val, max_val).
    """

    cpus = mp.cpu_count()
    chunks = np.array([nsamples // cpus] * cpus)
    chunks[-1] += (nsamples - np.sum(chunks))
    
    with mp.Pool(cpus) as pool:
        noise_chunks = pool.map(_white_noise_helper, chunks)
    
    noise = np.concatenate(noise_chunks)
    noise = (max_val - min_val) * noise + min_val

    return noise


def _test_weave_arrays1():
    
    a1 = np.array([1, 3, 5])
    a2 = np.array([2, 4, 6])

    total = weave_arrays(a1, a2)
    print(total)


def _test_weave_arrays2():
    
    a1 = np.array([1, 4, 7])
    a2 = np.array([2, 5, 8])
    a3 = np.array([3, 6, 9])

    total = weave_arrays(a1, a2, a3)
    print(total)


def _test_weave_arrays3():
    
    a1 = np.array([1, 4, 7])
    a2 = np.array([2, 5, 8])
    a3 = np.array([3, 6, 9, 10])

    total = weave_arrays(a1, a2, a3)
    print(total)


def _test_white_noise_trueness():

    import matplotlib.pyplot as plt
    from scipy.fft import fft, fftfreq

    # Number of sample points
    time_step = 1e-5 * u.second
    amplitude = 10 * u.volt
    duration = 1 * u.second
    nsamples = int(duration / time_step)

    x = np.linspace(0.0, duration.value, nsamples, endpoint=False)
    y = white_noise(nsamples, 0, amplitude.value)
    yf = fft(y)
    xf = fftfreq(nsamples, time_step.value)[:nsamples//2]
    yplot = 2.0/nsamples * np.abs(yf[0:nsamples//2])
    plt.plot(xf[1:], yplot[1:], c='k', lw=0.05)
    plt.grid()
    plt.show()
