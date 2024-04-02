import astropy.units as u
import numpy as np

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


@u.quantity_input
def arbitrary_noise_gen(frequencies: u.Hz, psd: (u.one / u.Hz**0.5), time_step: u.s): # type: ignore
    """Generate a noise spectrum using an arbitrary power spectral density (PSD)

    :param frequencies: Frequencies of PSD
    :type frequencies: u.Hz
    :param psd: Power spectral density
    :type psd: u.one
    :param time_step: Time step of sampled data used to compute PSD.
    :type time_step: u.s
    :return: Function wrapped with `PSDGenerator`
    :rtype: Callable
    """    ''''''
    def wrap(f):
        return np.interp(
            f / time_step.to_value(u.s),
            frequencies.to_value(u.Hz),
            psd.to_value(u.one / u.Hz**0.5),
            left=0,
            right=0
        )
    return PSDGenerator(wrap)



COLORS = {}
for key, value in list(locals().items()):
    if callable(value) and key.endswith('_noise'):
        name = key.split('_noise')[0]
        COLORS[name] = value

