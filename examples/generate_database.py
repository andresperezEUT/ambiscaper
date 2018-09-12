### GENERATE SOME DATABASES FOR LOCALIZATION ANALYSIS

import ambiscaper
import numpy as np
import os
import random


# AmbiScaper settings
soundscape_duration = 5
ambisonics_order = 1
samples_folder = '/Volumes/Dinge/audio/anechoic_openAIRlib_ccsa'

# 3 Different datasets, each one with 100 soundscapes containing 1 to 3 simultaneous sounds
num_datasets = 3
num_soundscapes = 100

for dataset_idx in range(1):

    print('Creating dataset: ' + str(dataset_idx))

    for soundscape_idx in range(num_soundscapes):

        print('Creating soundscape: '+str(soundscape_idx))

        ### Create an ambiscaper instance
        asc = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                    ambisonics_order=ambisonics_order,
                                    fg_path=samples_folder)
        # just in case...
        asc.ref_db = -40

        num_events = dataset_idx +1
        for event_idx in range(num_events):
            ### Add an event
            asc.add_event(source_file=('choose',[]),
                          source_time=('const', 0),
                          event_time=('const', 0),
                          event_duration=('const', 2),
                          event_azimuth=('uniform', 0, 2 * np.pi),
                          event_elevation=('uniform', -np.pi / 2, np.pi / 2),
                          event_spread=('const', 0),
                          snr=('const', 10),
                          pitch_shift=('uniform', -2., 2.),
                          time_stretch=('uniform', 0.8,1.2))

        # Add a recorded reverb
        asc.set_sofa_reverb_folder_path('/Volumes/Dinge/SOFA/pinakothek/')
        asc.add_sofa_reverb(name=('choose', []),
                            wrap=('const', 'random'))

        ### Genereate the audio and the annotation

        outfolder = '/Volumes/Dinge/ambiscaper/IWAENC2018/'+'dataset'+str(dataset_idx)
        if not os.path.exists(outfolder):
            os.mkdir(outfolder) # watch out! outfolder must exist
        destination_path = os.path.join(outfolder, "soundscape{:d}".format(soundscape_idx))

        asc.generate(destination_path=destination_path,
                     generate_txt=True,
                     allow_repeated_source=True)

print('Finished! Enjoy')