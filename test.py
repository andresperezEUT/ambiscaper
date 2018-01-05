import scaper
import numpy as np
import os

# OUTPUT FOLDER
outfolder = '/Volumes/Dinge/scaper/generated/'

# SCAPER SETTINGS
foreground_folder = '~/audio/scaper/foreground/'
background_folder = '~/audio/scaper/background/'
# smir_reverb_path  = '~/Documents/MATLAB/SMIR-Generator-master'
s3a_reverb_path   = '~/source/scaper/IRs/S3A'

n_soundscapes = 1
ref_db = -50
duration = 10.0
ambisonics_order = 3
ambisonics_spread_slope = 1.0

num_events = 2

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

# event_azimuth_dist = 'uniform'
# event_azimuth_min = 0
# event_azimuth_max = 2*np.pi
#
# event_elevation_dist = 'uniform'
# event_elevation_min = -np.pi/2
# event_elevation_max = np.pi/2

event_azimuth_dist = 'const'
event_azimuth = 0

event_elevation_dist = 'const'
event_elevation = 0

event_spread_dist = 'const'
event_spread = 0

snr_dist = 'uniform'
snr_min = 6
snr_max = 30

pitch_dist = 'const'
pitch = 1

time_stretch_dist = 'const'
time_stretch = 2

# Generate 1000 soundscapes using a truncated normal distribution of start times

for n in range(n_soundscapes):

    print('Generating soundscape: {:d}/{:d}'.format(n+1, n_soundscapes))

    # create a scaper
    sc = scaper.Scaper(duration, ambisonics_order, ambisonics_spread_slope, foreground_folder, background_folder)
    sc.protected_labels = []
    sc.ref_db = ref_db

    # add background
    # sc.add_background(label=('choose', []),
    #                   source_file=('choose', []),
    #                   source_time=('const', 0))

    n_events = num_events
    for _ in range(n_events):
        sc.add_event(label=('choose', []),
                     source_file=('choose', []),
                     source_time=(source_time_dist, source_time),
                     event_time=(event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max),
                     event_duration=(event_duration_dist, event_duration_min, event_duration_max),
                     # event_azimuth=(event_azimuth_dist,event_azimuth_min,event_azimuth_max),
                     event_azimuth=(event_azimuth_dist,event_azimuth),
                     # event_elevation=(event_elevation_dist,event_elevation_min,event_elevation_max),
                     event_elevation=(event_elevation_dist,event_elevation),
                     event_spread=(event_spread_dist,event_spread),
                     snr=(snr_dist, snr_min, snr_max),
                     pitch_shift=(pitch_dist, pitch),
                     time_stretch=(time_stretch_dist, time_stretch))



    # configure reverb
    reverb_config = scaper.core.SmirReverbSpec(
        # path = smir_reverb_path,
        IRlength=1024,
        room_dimensions=[30,30,30],
        beta= [1, 0.7, 0.7, 0.5, 0.2, 1],
        source_type='o',
        microphone_type='soundfield'
    )

    # SmirReverbSpec = namedtuple(
    #     'SmirReverbSpec',
    #     ['IRlength',
    #      'room_dimensions',
    #      'beta',
    #      'source_location',
    #      'source_type',
    #      'receiver_location',
    #      'sphere_radius',
    #      'sphere_type',
    #      'capsule_positions'
    #      ], verbose=False)

    # reverb_config = scaper.core.S3aReverbSpec(
    #     path= s3a_reverb_path,
    #     name = 'MainChurch'
    # )

    sc.set_reverb(reverb_config)

    # generate
    destination_path = os.path.join(outfolder,"soundscape{:d}".format(n))

    sc.generate(destination_path=destination_path,
                allow_repeated_label=True,
                allow_repeated_source=True,
                disable_sox_warnings=True,
                no_audio=False,
                generate_txt=True)