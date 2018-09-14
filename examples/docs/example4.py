### EXAMPLE 4

import ambiscaper
import numpy as np
import os

# AmbiScaper settings
soundscape_duration = 5.0
ambisonics_order = 1
samples_folder = '../../samples/Handel_Trumpet'

### Create an ambiscaper instance
ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                   ambisonics_order=ambisonics_order,
                                   fg_path=samples_folder)

### Add an event
ambiscaper.add_event(source_file=('choose', []),
                     source_time=('uniform', 0, soundscape_duration),
                     event_time=('uniform', 0, soundscape_duration),
                     event_duration=('const', soundscape_duration),
                     event_azimuth=('const', 0),
                     event_elevation=('const', 0),
                     event_spread=('const', 0.5),
                     snr=('uniform', 0, 10),
                     pitch_shift=('const', 1),
                     time_stretch=('const', 1))

# Add Simulated Reverb
ambiscaper.add_simulated_reverb(IRlength=('const', 2048),  # in samples
                                room_dimensions=('const', [3, 3, 2]),  # [x,y,z]
                                t60=('const', 0.2),  # in seconds
                                source_type=('const', 'o'),  # omnidirectional
                                microphone_type=('const', 'soundfield'))  # order 1

### Genereate the audio and the annotation
outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
destination_path = os.path.join(outfolder, "example4")