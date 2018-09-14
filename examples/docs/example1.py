# Example 1: Foreground and background
# ------------------------------------

from ambiscaper import *
import os

# AmbiScaper settings
soundscape_duration = 5.0
ambisonics_order = 1

# We want to use the full samples folder as potential events
samples_folder = '../../samples/Handel_Trumpet'

### Create an ambiscaper instance
ambiscaper = AmbiScaper(duration=soundscape_duration,
                        ambisonics_order=ambisonics_order,
                        fg_path=samples_folder,
                        bg_path=samples_folder)

# Configure reference noise floor level
ambiscaper.ref_db = -30

### Add a background event

# Background events, by definition, have maximum spread
# That means that they will only contain energy in the W channel (the first one)
ambiscaper.add_background(source_file=('const', 'tr-1788d-piece4-sl.wav'),
                          source_time=('const', 5.))

### Add an event
ambiscaper.add_event(source_file=('const', 'tr-1888d-high.wav'),
                     source_time=('const', 0),
                     event_time=('const', 0),
                     event_duration=('const', soundscape_duration),
                     event_azimuth=('const', 0),
                     event_elevation=('const', 0),
                     event_spread=('const', 0),
                     snr=('const', 10),
                     pitch_shift=('const', 1),
                     time_stretch=('const', 1)
                     )

### Genereate the audio and the annotation
outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
destination_path = os.path.join(outfolder, "example1")

ambiscaper.generate(destination_path=destination_path,
                    generate_txt=True)