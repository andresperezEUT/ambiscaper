# Example 2: 15th order, variable spread Ambisonics soundscape
# -------------------------------------------------------------

from ambiscaper import *
import numpy as np
import os

# AmbiScaper settings
soundscape_duration = 10.0
ambisonics_order = 15
ambisonics_spread_slope = 0.25 # soft curve

# We want to use the full samples folder as potential events
samples_folder = os.path.abspath('../../samples/')

### Create an ambiscaper instance
ambiscaper = AmbiScaper(duration=soundscape_duration,
                        ambisonics_order=ambisonics_order,
                        fg_path=samples_folder)

# Make everything a little bit softer to avoid clipping
ambiscaper.ref_db = -40
ambiscaper.ambisonics_spread_slope = ambisonics_spread_slope

# add 10 events!
num_events = 10
for event_idx in range(num_events):
    ### Add an event
    ambiscaper.add_event(source_file=('choose',[]),
                         source_time=('uniform', 0, soundscape_duration),
                         event_time=('uniform', 0, soundscape_duration),
                         event_duration=('const', soundscape_duration),
                         event_azimuth=('uniform', 0, 2 * np.pi),
                         event_elevation=('uniform', -np.pi / 2, np.pi / 2),
                         event_spread=('truncnorm', 0.1, 0.2, 0.0, 0.5),
                         snr=('uniform', 0, 10),
                         pitch_shift=('uniform', -2, 2),
                         time_stretch=('uniform', 0.8, 1.2))

### Genereate the audio and the annotation
outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
destination_path = os.path.join(outfolder, "example2")

ambiscaper.generate(destination_path=destination_path,
                    generate_txt=True,
                    allow_repeated_source=True)