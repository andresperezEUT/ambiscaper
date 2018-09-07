## CREATE THE FILES REQUIRED FOR THE UNIT TESTING


import ambiscaper
import os

samples_folder = os.path.abspath('../samples')

sc = ambiscaper.AmbiScaper(10.0, 1, fg_path=samples_folder, bg_path=samples_folder)
sc.ref_db = -50

# background
sc.add_background(
    source_file=(
        'const',
        'Acoustics_Book/adult_female_speech.wav'),
    source_time=('const', 0))

# foreground events
sc.add_event(
    source_file=('const',
                 'Bicycle_Horn/chokedhorn.wav'),
    source_time=('const', 5),
    event_time=('const', 2),
    event_duration=('const', 5),
    event_azimuth=('const', 0),
    event_elevation=('const', 0),
    event_spread=('const', 0),
    snr=('const', 5),
    pitch_shift=None,
    time_stretch=None)

sc.add_event(
    source_file=('const',
                 'Bicycle_Horn/classichorn.wav'),
    source_time=('const', 0),
    event_time=('const', 5),
    event_duration=('const', 2),
    event_azimuth=('const', 0),
    event_elevation=('const', 0),
    event_spread=('const', 0),
    snr=('const', 20),
    pitch_shift=('const', 1),
    time_stretch=None)

sc.add_event(
    source_file=('const',
                 'Bicycle_Horn/paphorn.wav'),
    source_time=('const', 0),
    event_time=('const', 7),
    event_duration=('const', 2),
    event_azimuth=('const', 0),
    event_elevation=('const', 0),
    event_spread=('const', 0),
    snr=('const', 10),
    pitch_shift=None,
    time_stretch=('const', 1.2))

## Genereate the audio and the annotation
outfolder = '/Users/andres.perez/source/ambiscaper/tests/data/soundscape_for_test'

sc.generate(destination_path=outfolder,
             generate_txt=True,
             allow_repeated_source=True)