from typing import Callable

import astropy.units as u
import numpy as np

from . import pwl_helpers as helpers

def noise(
    noise_function: Callable[[int], np.ndarray],
    min_val: u.Quantity,
    max_val: u.Quantity,
    duration: u.Quantity,
    time_step: u.Quantity,
    name: str | None=None
) -> tuple[
    u.Quantity, u.Quantity
]:
    time_step = time_step << duration.unit
    nsamples = int( duration / time_step )
    times = np.arange(
        0, duration.to_value(u.s), time_step.to_value(u.s)
    )[:nsamples] << time_step.unit
    values = noise_function(nsamples)
    values = helpers.normalize_to_range(values, (min_val, max_val))

    fn = f'{name or noise_function.__name__}.pwl'
    helpers.write_file(times, values, fn)
