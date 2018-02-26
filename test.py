import ambiscaper
import numpy as np
import os

# OUTPUT FOLDER
# outfolder = '/Volumes/Dinge/ambiscaper/generated/'
outfolder = '/Volumes/Dinge/ambiscaper/testing/'

# SCAPER SETTINGS
# foreground_folder = '/Volumes/Dinge/audio/scaper/foreground/'
foreground_folder = '/Volumes/Dinge/audio/anechoic_openAIRlib/Acoustics_Book'
background_folder = '/Volumes/Dinge/audio/scaper/background/'

n_soundscapes = 10
ref_db = -50
duration = 5.0
ambisonics_order = 1
ambisonics_spread_slope = 1.0

num_events = 2

# Event time is the time at which the event will start, with respect to the soundscape time
event_time_dist = 'const'
event_time = 0.0

# Source time is the offset between the beginning of the audio event and the actual audio clip beginning
source_time_dist = 'const'
source_time = 0.0

# Event duration specifies the duration of the sound event, with respect to source_time
event_duration_dist = 'const'
event_duration = 5.0

event_azimuth_dist = 'uniform'
event_azimuth_min = 0
event_azimuth_max = 2*np.pi

event_elevation_dist = 'uniform'
event_elevation_min = -np.pi/2
event_elevation_max = np.pi/2

# event_azimuth_dist = 'const'
# event_azimuth = np.pi/4
#
# event_elevation_dist = 'const'
# event_elevation = np.pi/4

event_spread_dist = 'const'
event_spread = 0

snr_dist = 'uniform'
snr_min = 6
snr_max = 30

pitch_dist = 'const'
pitch = 1

time_stretch_dist = 'const'
time_stretch = 1

# reverb = 'simulated'
# reverb = 'recorded'
reverb = None

# Generate 1000 soundscapes using a truncated normal distribution of start times

for n in range(n_soundscapes):

    print('Generating soundscape: {:d}/{:d}'.format(n, n_soundscapes))

    # create a scaper
    sc = ambiscaper.AmbiScaper(duration, ambisonics_order, ambisonics_spread_slope, foreground_folder, background_folder)
    sc.protected_labels = []
    sc.ref_db = ref_db

    # add background
    # sc.add_background(label=('choose', []),
    #                   source_file=('choose', []),
    #                   source_time=('const', 0))

    n_events = num_events
    for _ in range(n_events):
        sc.add_event(source_file=('choose',[]),
                     source_time=(source_time_dist, source_time),
                     event_time=(event_time_dist, event_time),
                     event_duration=(event_duration_dist, event_duration),
                     # event_azimuth=(event_azimuth_dist,event_azimuth_min,event_azimuth_max),
                     event_azimuth=(event_azimuth_dist,event_azimuth_min,event_azimuth_max),
                     # event_elevation=(event_elevation_dist,event_elevation_min,event_elevation_max),
                     event_elevation=(event_elevation_dist,event_elevation_min,event_elevation_max),
                     event_spread=(event_spread_dist,event_spread),
                     snr=(snr_dist, snr_min, snr_max),
                     pitch_shift=(pitch_dist, pitch),
                     time_stretch=(time_stretch_dist, time_stretch))


    # Simulated Reverb
    if reverb is 'simulated':
        sc.add_simulated_reverb(IRlength=('const', 1024),
                                room_dimensions=('const',[6,3,3]),
                                t60=('uniform',0.1,0.5),
                                source_type=('const','o'),
                                microphone_type=('const','soundfield'))

    # Recorded Reverb
    elif reverb is 'recorded':
        # sc.add_recorded_reverb(name=('choose',[]))
        sc.add_recorded_reverb(name=('const','AudioBooth'))

    # Nothing: no reverb

    # generate
    destination_path = os.path.join(outfolder,"soundscape{:d}".format(n+1))

    sc.generate(destination_path=destination_path,
                allow_repeated_source=True,
                disable_sox_warnings=True,
                no_audio=False,
                generate_txt=True)