# WLAN Gate Opener

TODO: readme

Pico W MicroPython UF2 -- <https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2>
<https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython>

<https://www.raspberrypi.com/documentation/microcontrollers/images/picow-pinout.svg>

`cp .\env.py.example .\src\env.py`

<https://docs.micropython.org/en/latest/>

## Setup

TODO: setup instructions

## Components

- Mosfet -- [IRLI540NPbF](https://www.infineon.com/dgdl/irli540npbf.pdf?fileId=5546d462533600a401535664018125c1)
- Relay -- [LMR2-3D](https://www.tme.eu/Document/cb95bab3047ea17130b1da862f2b7351/LMR-series.pdf)
   > Most likely not needed and mosfet can be used instead but I like the audio feedback it gives.
   >
   >Only one side is used so LMR1 is totally fine, this was just locally available.
- Microcontroller -- [Pico W](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico-1-family)

## Circuit

TODO: diagram of circuit picture of breadcrumb board
