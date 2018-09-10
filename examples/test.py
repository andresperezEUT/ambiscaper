### JUST SOME SANDBOX FOR TESTING STUFF

import ambiscaper
import numpy as np
import os
import random

#
# # AmbiScaper settings
# soundscape_duration = 5.0
# ambisonics_order = 1
# samples_folder = '/Volumes/Dinge/audio/anechoic_openAIRlib_ccsa'
#
#
# num_soundscapes = 1
# for i in range(num_soundscapes):
#
#     print('Creating soundscape: '+str(i))
#
#     ### Create an ambiscaper instance
#     asc = ambiscaper.AmbiScaper(duration=soundscape_duration,
#                                 ambisonics_order=ambisonics_order,
#                                 fg_path=samples_folder)
#     # just in case...
#     asc.ref_db = -15
#
#     num_events = 1
#     for event_idx in range(num_events):
#         ### Add an event
#         asc.add_event(source_file=('choose',[]),
#                              source_time=('uniform', 0, soundscape_duration),
#                              event_time=('uniform', 0, soundscape_duration),
#                              event_duration=('const', soundscape_duration/2),
#                              event_azimuth=('uniform', 0, 2 * np.pi),
#                              event_elevation=('uniform', -np.pi / 2, np.pi / 2),
#                              event_spread=('const', 0),
#                              snr=('uniform', 0, 10),
#                              pitch_shift=('uniform', -2., 2.),
#                              time_stretch=('uniform', 0.8,1.2))
#
#     # Add a recorded reverb
#
#     # TODO
#     asc.set_sofa_reverb_folder_path('/Volumes/Dinge/SOFA/pinakothek/')
#
#     asc.add_sofa_reverb(name=('const', 'foyer.sofa'),
#                         wrap=('const', 'random'))
#     # asc.add_sofa_reverb(name=('choose',[]),
#     #                         wrap=('const','wrap_azimuth'))
#
#     ### Genereate the audio and the annotation
#     outfolder = '/Volumes/Dinge/ambiscaper/SOFAtesting/'  # watch out! outfolder must exist
#     destination_path = os.path.join(outfolder, "soundscape{:d}".format(i))
#
#     asc.generate(destination_path=destination_path,
#                  generate_txt=True,
#                  allow_repeated_source=True)
#
# print('Finished! Enjoy')