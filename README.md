# AmbiScaper

<img src="ambiscaper_logo.png" width="450" height="200">

Ambiscaper: a tool for automatic dataset generation and annotation of reverberant Ambisonics audio

Originally forked from [Scaper](http://github.com/justinsalamon/scaper) (commit e0cc1c9, 17th October 2017)

[//]: #[![PyPI](https://img.shields.io/pypi/v/scaper.svg)](https://pypi.python.org/pypi/scaper)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Build Status](https://travis-ci.org/andresperezlopez/ambiscaper.svg?branch=master)](https://travis-ci.org/andresperezlopez/ambiscaper)
[![Coverage Status](https://coveralls.io/repos/github/andresperezlopez/ambiscaper/badge.svg?branch=master)](https://coveralls.io/github/andresperezlopez/ambiscaper?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ambiscaper/badge/?version=latest)](http://ambiscaper.readthedocs.io/en/latest/?badge=latest)

[//]: #[![PyPI](https://img.shields.io/badge/python-2.7%2C%203.4%2C%203.5%2C%203.6-blue.svg)]()

Please refer to the [documentation](http://ambiscaper.readthedocs.io/) for implementation detailsdetails.

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

To help you get started with scaper, please see this [step-by-step tutorial](http://scaper.readthedocs.io/en/latest/tutorial.html).

## Example

```python
import scaper
import numpy as np

# OUTPUT FOLDER
outfolder = 'audio/soundscapes/'

# SCAPER SETTINGS
fg_folder = 'audio/soundbank/foreground/'
bg_folder = 'audio/soundbank/background/'

n_soundscapes = 1000
ref_db = -50
duration = 10.0 

min_events = 1
max_events = 9

event_time_dist = 'truncnorm'
event_time_mean = 5.0
event_time_std = 2.0
event_time_min = 0.0
event_time_max = 10.0

source_time_dist = 'const'
source_time = 0.0

event_duration_dist = 'uniform'
event_duration_min = 0.5
event_duration_max = 4.0

snr_dist = 'uniform'
snr_min = 6
snr_max = 30

pitch_dist = 'uniform'
pitch_min = -3.0
pitch_max = 3.0

time_stretch_dist = 'uniform'
time_stretch_min = 0.8
time_stretch_max = 1.2
    
# Generate 1000 soundscapes using a truncated normal distribution of start times

for n in range(n_soundscapes):
    
    print('Generating soundscape: {:d}/{:d}'.format(n+1, n_soundscapes))
    
    # create a scaper
    sc = scaper.Scaper(duration, fg_folder, bg_folder)
    sc.protected_labels = []
    sc.ref_db = ref_db
    
    # add background
    sc.add_background(label=('const', 'noise'), 
                      source_file=('choose', []), 
                      source_time=('const', 0))

    # add random number of foreground events
    n_events = np.random.randint(min_events, max_events+1)
    for _ in range(n_events):
        sc.add_event(label=('choose', []), 
                     source_file=('choose', []), 
                     source_time=(source_time_dist, source_time), 
                     event_time=(event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max), 
                     event_duration=(event_duration_dist, event_duration_min, event_duration_max), 
                     snr=(snr_dist, snr_min, snr_max),
                     pitch_shift=(pitch_dist, pitch_min, pitch_max),
                     time_stretch=(time_stretch_dist, time_stretch_min, time_stretch_max))
    
    # generate
    audiofile = os.path.join(outfolder, "soundscape_unimodal{:d}.wav".format(n))
    jamsfile = os.path.join(outfolder, "soundscape_unimodal{:d}.jams".format(n))
    txtfile = os.path.join(outfolder, "soundscape_unimodal{:d}.txt".format(n))
    
    sc.generate(audiofile, jamsfile,
                allow_repeated_label=True,
                allow_repeated_source=False,
                reverb=0.1,
                disable_sox_warnings=True,
                no_audio=False,
                txt_path=txtfile)
```
