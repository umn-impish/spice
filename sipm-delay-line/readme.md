# SiPM readout with delay line + op amp difference circuit
This circuit is a "proof of concept" of SiPM readout using a transimpedance amplifier and 10ns delay line.

The SiPM pulse is modeled as a current source with some passives around it,
    following [Corsi+2009](https://iopscience.iop.org/article/10.1088/1748-0221/4/03/P03004).
The quench resistor was measured and the capacitance was estimated from the data sheet,
    along with proportionalities in the Corsi paper.

The current pulse is immediately transformed into a voltage pulse by a fast (4GHz gain bandwidth)
    transimpedance amplifier implemented with an
    [AD6268-10](https://www.analog.com/media/en/technical-documentation/data-sheets/626810f.pdf) op amp.

The SiPM pulse is delayed by 10ns through an ideal transmission line of length ~1.5 meters.
Then the difference between the delayed- and non-delayed pulses is taken.
Even with the amplified pulse buried in the (simulated) white noise,
    the SiPM pulse is recovered:
![signal recovery](signal-recovery.png)

More work needs to be done to incorporate a summing amplifier for multiple SiPM to be read out simultaneously.
But this is a good start.
