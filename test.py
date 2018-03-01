### EXAMPLE 3

import ambiscaper
import numpy as np
import os

# AmbiScaper settings
soundscape_duration = 5.0
ambisonics_order = 2
samples_folder = os.path.abspath('./samples/Bicycle_Horn')

### Create an ambiscaper instance
ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                   ambisonics_order=ambisonics_order,
                                   fg_path=samples_folder)

num_events = 2
for event_idx in range(num_events):
    ### Add an event
    ambiscaper.add_event(source_file=('const','chokedhorn.wav'),
                         source_time=('uniform', 0, soundscape_duration),
                         event_time=('uniform', 0, soundscape_duration),
                         event_duration=('const', soundscape_duration),
                         event_azimuth=('uniform', 0, 2 * np.pi),
                         event_elevation=('uniform', -np.pi / 2, np.pi / 2),
                         event_spread=('uniform',0 ,1),
                         snr=('uniform', 0, 10),
                         pitch_shift=('const', 1),
                         time_stretch=('const', 1))

# Add a recorded reverb
ambiscaper.add_recorded_reverb(name=('const','MainChurch'),
                               wrap=('const','wrap_azimuth'))

### Genereate the audio and the annotation
outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
destination_path = os.path.join(outfolder, "example3_4")

ambiscaper.generate(destination_path=destination_path,
                    generate_txt=True,
                    allow_repeated_source=True)