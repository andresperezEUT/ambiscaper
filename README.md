# AmbiScaper

<img src="ambiscaper_logo.png" width="450" height="200">

Ambiscaper: a tool for automatic dataset generation and annotation of reverberant Ambisonics audio

[//]: #[![PyPI](https://img.shields.io/pypi/v/scaper.svg)](https://pypi.python.org/pypi/scaper)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Build Status](https://travis-ci.org/andresperezlopez/ambiscaper.svg?branch=master)](https://travis-ci.org/andresperezlopez/ambiscaper)
[![Coverage Status](https://coveralls.io/repos/github/andresperezlopez/ambiscaper/badge.svg?branch=master)](https://coveralls.io/github/andresperezlopez/ambiscaper?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ambiscaper/badge/?version=latest)](http://ambiscaper.readthedocs.io/en/latest/?badge=latest)

[//]: #[![PyPI](https://img.shields.io/badge/python-2.7%2C%203.4%2C%203.5%2C%203.6-blue.svg)]()

Please refer to the [documentation](http://ambiscaper.readthedocs.io/) for implementation details.

Originally forked from [Scaper](http://github.com/justinsalamon/scaper) (commit e0cc1c9, 17th October 2017)


## Motivation

Due to the recent developments on the field of immersive media and virtual reality, there has been a renewed interest into Ambisonics, specially motivated by its potential to capture the spacial qualities of the sound, and the methodologies to dynamically render it to binaural.

Despite the common approach to Ambisonics recordings as "ambiences", some modern Ambisonics microphones feature dozens of capsules. Therefore, it is possible to use such microphones as beamforming devices, with an accurate spatial resolution.

As a consequence, Ambisonics recordings might be useful in the auditory scene analysis field. More specifically, the intrinsic spatial audio representation can be exploited in the Sound Source Localization and Blind Source Separation fields.

However, there is an important lack of Ambisonics recordings databases, specially in the case of Higher Order Ambisonics. Annotation is also needed to design, train and evaluate the algorithms. The related works presented in last years have used custom databases, which hinder experiment reproducibility. A flexible reverberation configuration is as well needed for the state-of-the-art methods. Manual recording and annotation of sound scenes on that scale would imply an excessive amount of work.

We present AmbiScaper, a python library for procedural creation and annotation of reverberant Ambisonics databases. The software is based on a related work by Justin Salamon ( [Scaper](http://github.com/justinsalamon/scaper) ) in the context of scene recognition.

## Installation

### Non-python dependencies
Scaper has two non-python dependencies:
- SoX: http://sox.sourceforge.net/
- FFmpeg: https://ffmpeg.org/

On macOS these can be installed using [homebrew](https://brew.sh/):

```
brew install sox
brew install ffmpeg
```

On linux you can use your distribution's package manager, e.g. on Ubuntu (15.04 "Vivid Vervet" or newer):

```
sudo apt-get install sox
sudo apt-get install ffmpeg
```
NOTE: on earlier versions of Ubuntu [ffmpeg may point to a Libav binary](http://stackoverflow.com/a/9477756/2007700) which is not the correct binary. If you are using anaconda, you can install the correct version by calling `conda install -c conda-forge ffmpeg`. Otherwise, you can [obtain a static binary from the ffmpeg website](https://ffmpeg.org/download.html).

On windows you can use the provided installation binaries:
- SoX: https://sourceforge.net/projects/sox/files/sox/
- FFmpeg: https://ffmpeg.org/download.html#build-windows

### Installing Scaper

The simplest way to install scaper is by using `pip`, which will also install the required python dependencies if needed. To install scaper using pip, simply run:

```
pip install scaper
```

To install the latest version of scaper from source, clone or pull the lastest version:

```
git clone git@github.com:justinsalamon/scaper.git
```

Then enter the source folder and install using pip to handle python dependencies:

```
cd scaper
pip install -e .
```
## Tutorial

To help you get started with scaper, please see this [step-by-step tutorial](http://ambiscaper.readthedocs.io/en/latest/tutorial.html).

Furthermore, we have prepared a bunch of [reference examples](http://ambiscaper.readthedocs.io/en/latest/examples.html).
## Example

```python
import ambiscaper
import numpy as np
import os

# AmbiScaper settings
soundscape_duration = 5.0
ambisonics_order = 1
foreground_folder = os.path.abspath('./samples/Acoustics_Book')

### Create an ambiscaper instance
ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                   ambisonics_order=ambisonics_order,
                                   fg_path=foreground_folder)
                                   
### Add an event
ambiscaper.add_event(source_file=('choose', ['adult_female_speech.wav','bagpipe_music.wav']),
                     source_time=('const', 0),
                     event_time=('const', 0),
                     event_duration=('const', soundscape_duration),
                     event_azimuth=('uniform', 0, 2*np.pi),
                     event_elevation=('uniform', -np.pi/2, np.pi/2),
                     event_spread=('const', 0),
                     snr=('const', 0),
                     pitch_shift=('const', 1),
                     time_stretch=('const', 1))
                     
### Genereate the audio and the annotation
outfolder = '/Volumes/Dinge/ambiscaper/testing/' # watch out! outfolder must exist
destination_path = os.path.join(outfolder,"my_first_ambisonics_soundscape")

ambiscaper.generate(destination_path=destination_path,
                    generate_txt=True)
```
