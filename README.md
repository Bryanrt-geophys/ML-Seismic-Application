# Applying deep learning methods to picking phase arrivals in continoues seismic-signal recorded in the western Delaware basin

The New Mexico Bureau of Geology has interest in converting thier approach to cataloging seismic events, from a by-hand method to one performed by deep learning algorithms. For this project I am initially testing three methodoligies, [EQTransformer](https://github.com/smousavi05/EQTransformer), [FAST](https://github.com/stanford-futuredata/FAST), and [easyQuake](https://github.com/jakewalter/easyQuake). The progress made in application of each mothodoligy will be documented below for future Bureau epmloyees to replicate or continue the work.

## Progress
[EQTransformer progress documentation](docs/EQTransformer.md)

[easyQuake progress documentation](docs/easyQuake.md)

[FAST progress documentation](docs/FAST.md)

# sac2EQTransformR
[VibRation](https://gitlab.com/Bryanrt-geophys/vibration) is a package I am creating in R to work in tandem with EQTransformer, mseed2sac, and the by-hand picking method with .dat file outputs and is currently undergoing the process of be published under CRAN. This will provide the data sets necessary to retrain the EQTransformer algorithms used in this project.
