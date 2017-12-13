import scaper
import numpy as np
import os

# OUTPUT FOLDER
outfolder = '/Volumes/Dinge/scaper/generated'

# SCAPER SETTINGS
foreground_folder = '~/audio/scaper/foreground/'
background_folder = '~/audio/scaper/background/'

n_soundscapes = 1
ref_db = -50
duration = 10.0
ambisonics_order = 3

num_events = 10

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

event_azimuth_dist = 'uniform'
event_azimuth_min = 0
event_azimuth_max = 2*np.pi

event_elevation_dist = 'uniform'
event_elevation_min = -np.pi/2
event_elevation_max = np.pi/2

event_spread_dist = 'const'
event_spread = 0

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
    sc = scaper.Scaper(duration, ambisonics_order, foreground_folder, background_folder)
    sc.protected_labels = []
    sc.ref_db = ref_db

    # add background
    sc.add_background(label=('choose', []),
                      source_file=('choose', []),
                      source_time=('const', 0))

    n_events = num_events
    for _ in range(n_events):
        sc.add_event(label=('choose', []),
                     source_file=('choose', []),
                     source_time=(source_time_dist, source_time),
                     event_time=(event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max),
                     event_duration=(event_duration_dist, event_duration_min, event_duration_max),
                     event_azimuth=(event_azimuth_dist,event_azimuth_min,event_azimuth_max),
                     event_elevation=(event_elevation_dist,event_elevation_min,event_elevation_max),
                     event_spread=(event_spread_dist,event_spread),
                     snr=(snr_dist, snr_min, snr_max),
                     pitch_shift=(pitch_dist, pitch_min, pitch_max),
                     time_stretch=(time_stretch_dist, time_stretch_min, time_stretch_max))

    # generate
    audiofile = os.path.join(outfolder, "soundscape_unimodal{:d}.wav".format(n))
    jamsfile = os.path.join(outfolder, "soundscape_unimodal{:d}.jams".format(n))
    txtfile = os.path.join(outfolder, "soundscape_unimodal{:d}.txt".format(n))

    sc.generate(audiofile, jamsfile,
                allow_repeated_label=True,
                allow_repeated_source=True,
                reverb=0,
                disable_sox_warnings=True,
                no_audio=False,
                txt_path=txtfile)