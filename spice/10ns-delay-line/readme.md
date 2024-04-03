# 10 nanosecond delay line circuit + symbol
This circuit+symbol is a 10ns delay line which should work up to a few hundred MHz.
It's made up of 256 LC filters in series,
    which correspond to a L and C per 8mm of length of a
    lossless 50 ohm transmission line.
It is a single-ended delay line (the "shield" is tied to ground).

## Python delay?
The Jupyter notebook is just a mathematical playground to see how the delay line will affect our signals.
