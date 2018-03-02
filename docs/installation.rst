.. _installation:

Installation instructions
=========================

Installing AmbiScaper
---------------------
To install the latest version of ambiscaper from source:

1. Clone or pull the lastest version:

>>> git clone https://github.com/andresperezlopez/ambiscaper.git

2. Install using pip to handle python dependencies:

>>> cd ambiscaper
>>> pip install -e .

This procedure will automatically install the required python and non-python dependencies.

Pip online installer comming soon!

Matlab dependency
-----------------
If you wish to use the simulated reverb feature implemented by SmirGenerator, you will need to have a valid working version of Matlab.


Non-python dependencies (manual installation)
---------------------------------------------
AmbiScaper has two non-python dependencies:

- SoX: http://sox.sourceforge.net/
- FFmpeg: https://ffmpeg.org/

On macOS these can be installed using `homebrew <https://brew.sh/>`_:

>>> brew install sox
>>> brew install ffmpeg

On linux you can use your distribution's package manager, e.g. on Ubuntu (15.04 "Vivid Vervet" or newer):

>>> sudo apt-get install sox
>>> sudo apt-get install ffmpeg

NOTE: on earlier versions of Ubuntu `ffmpeg may point to a Libav binary <http://stackoverflow.com/a/9477756/2007700>`_
which is not the correct binary. If you are using anaconda, you can install the correct version by calling:

>>> conda install -c conda-forge ffmpeg

Otherwise, you can `obtain a static binary from the ffmpeg website <https://ffmpeg.org/download.html>`_.

On windows you can use the provided installation binaries:

- SoX: https://sourceforge.net/projects/sox/files/sox/
- FFmpeg: https://ffmpeg.org/download.html#build-windows