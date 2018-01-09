'''
reverb_ambisonics.py
Created by Andres Perez Lopez on 09/01/2018

Convenience declarations and methods
for the ambisonics reverb

Currently supporrting two IR acquisition methods:
- Recorded: S3A material
- Modelled: SMIR generator
'''

import csv
from collections import namedtuple
from numbers import Number
import numpy as np
import os
import glob
from scaper.scaper_exceptions import ScaperError
from scaper.util import find_element_in_list, cartesian_to_spherical



######### METHODS #########

def _validate_reverb_config(reverb_config, target_ambisonics_order):
    '''

    :param reverb_config:
    :param target_ambisonics_order:
    :return:
    '''

    if reverb_config is None:
        raise ScaperError(
            'reverb_config is None')

    # Check all different supported reverb types
    # smir
    if type(reverb_config) is SmirReverbSpec:
        _validate_smir_reverb_spec(reverb_config)
    # s3a
    elif type(reverb_config) is S3aReverbSpec:
        _validate_s3a_reverb_spec(reverb_config)
    else:
        raise ScaperError(
            'reverb_config of unknown type: ' + str(type(reverb_config)))


def _validate_smir_reverb_spec(reverb_config):
    '''
    TODO
    :param reverb_config:
    :return:
    '''
    # IR length: positive integer
    if reverb_config.IRlength is None:
        raise ScaperError(
            'reverb_config: IR length is None')
    elif not isinstance(reverb_config.IRlength, int) or reverb_config.IRlength <= 0:
        raise ScaperError(
            'reverb_config: IR length must be a positive integer')

    # room_dimensions: list of 3 elements
    if reverb_config.room_dimensions is None:
        raise ScaperError(
            'reverb_config: room_dimensions is None')
    elif not isinstance(reverb_config.room_dimensions, list):
        raise ScaperError(
            'reverb_config: room_dimensions is not a List')
    elif len(reverb_config.room_dimensions) is not 3:
        raise ScaperError(
            'reverb_config: room_dimensions must have 3 elements')

    # beta: float > 0 (T_60) or list of 6 floats
    if reverb_config.beta is None:
        raise ScaperError(
            'reverb_config: beta is None')

    # If it's T_60, it should be bigger than 0
    if isinstance(reverb_config.beta, Number):

        if reverb_config.beta <= 0:
            raise ScaperError(
                'reverb_config: beta (T_60) must be a positive number')

    # If list, it should be a list of 6 numbers
    elif isinstance(reverb_config.beta, list):

        if len(reverb_config.beta) is not 6:
            raise ScaperError(
                'reverb_config: beta must have 6 elements; found '
                + str(len(reverb_config.beta)))

        if not all([isinstance(e, Number) for e in reverb_config.beta]):
            raise ScaperError(
                'reverb_config: beta must contain numbers')

    # If none of them, wrong type
    else:
        raise ScaperError(
            'reverb_config: beta must be a T_60 value, or '
            'the walls reflectivity (list of 6 numbers)')

    # Valid source types: 'o','c','s','h','b'
    if reverb_config.source_type is None:
        raise ScaperError(
            'reverb_config: source_type is None')

    elif not isinstance(reverb_config.source_type, str):
        ScaperError(
            'reverb_config: source_type must be a string')

    elif find_element_in_list(reverb_config.source_type, SMIR_ALLOWED_SOURCE_TYPES) is None:
        ScaperError(
            'reverb_config: source_type not known: '
            + reverb_config.source_type)

    # Mic type: defined SUPPORTED_VIRTUAL_MICS
    if reverb_config.microphone_type is None:
        raise ScaperError(
            'reverb_config: microphone_type is None')

    elif not isinstance(reverb_config.microphone_type, str):
        ScaperError(
            'reverb_config: microphone_type must be a string')

    else:
        if not SMIR_SUPPORTED_VIRTUAL_MICS.has_key(reverb_config.microphone_type):
            raise ScaperError(
                'reverb_config: unsupported microphone_type: '
                + reverb_config.microphone_type)



def _validate_s3a_reverb_spec(reverb_config):
    # Folder structure should be something like:
    # - S3A_top_folder (:s3a_folder_path: defined in ambisonics.py)
    #     - reverb_name (:name: in the config struct)
    #         - (maybe a pdf)
    #         - "Soundfield"
    #             - "lsN.wav" with the N actual impulse responses, starting from 1
    #             - "LsPos.txt" with the loudspeaker positions
    #             - (maybe a "Metadata_SoundField.txt")

    # Check that reverb name is str
    if reverb_config.name is None:
        raise ScaperError(
            'reverb_config: path is None')
    elif type(reverb_config.name) is not str:
        raise ScaperError(
            'reverb path not a string')

    # The provided name should exist in s3a_
    reverb_folder_path = os.path.join(S3A_FOLDER_PATH, reverb_config.name)
    if not os.path.exists(os.path.expanduser(reverb_folder_path)):
        raise ScaperError(
            'reverb_config: folder does not exist: ' + reverb_folder_path)

    # Inside the reverb folder should be a "Soundfield" folder
    soundfield_path = os.path.join(reverb_folder_path, 'Soundfield')
    if not os.path.exists(os.path.expanduser(soundfield_path)):
        raise ScaperError(
            'reverb_config: Soundfield folder does not exist inside : ' + os.path.expanduser(reverb_folder_path))

    # Check that the "LsPos.txt" file contains as many xyz positions as wav files in the folder

    # Count number of audio files (the actual IRs)
    num_wav_files = len(glob.glob(os.path.expanduser(soundfield_path) + "/*.wav"))

    # Count number of lines in speakers file
    speakers_positions_file = os.path.join(soundfield_path, S3A_LOUDSPEAKER_POSITIONS_TXTFILE);
    num_lines = sum(1 for line in open(os.path.expanduser(speakers_positions_file)))

    # Check
    if num_wav_files is not num_lines:
        raise ScaperError(
            'reverb_config: the number of audio files does not match with the speaker description')



def get_max_ambi_order_from_reverb_config(reverb_config):
    '''
    TODO
    :param reverb_config:
    :param target_ambisonics_order:
    :return:
    '''

    # smir
    if type(reverb_config) is SmirReverbSpec:
        # Max ambisonics order is defined in the mic spec...
        return SMIR_SUPPORTED_VIRTUAL_MICS[reverb_config.microphone_type]['max_ambi_order']

    # s3a
    elif type(reverb_config) is S3aReverbSpec:
        # Check the maximum ambisonics order
        # Max ambisonics order given by the number of channels of the IRs
        # TODO: for the moment we only have order 1 recordings, so let's just do a dirty hardcode
        return 1


def generate_RIR_path(s3a_reverg_config):
    '''
    TODO
    :param s3a_reverg_config:
    :return:
    '''
    # TODO: remove hardcoded reference to Soundfield
    return os.path.expanduser(os.path.join(S3A_FOLDER_PATH, s3a_reverg_config.name, 'Soundfield'))


def retrieve_RIR_positions(s3a_reverg_config):
    '''
    TODO

    Folder structure should be something like:
    - S3A_top_folder (:path: in the config struct)
        - reverb_name (:name: in the config struct)
            - (maybe a pdf)
            - "Soundfield"
                - "lsN.wav" with the N actual impulse responses, starting from 1
                - "LsPos.txt" with the loudspeaker positions
                - (maybe a "Metadata_SoundField.txt")

    :param s3a_reverg_config:
    :return:
    '''

    # Go to Soundfield folder
    # todo: maybe better implementation for txt file open?

    speakers_positions_file = os.path.join(generate_RIR_path(s3a_reverg_config), S3A_LOUDSPEAKER_POSITIONS_TXTFILE)

    # Retrieve the file content into speaker_positions
    speaker_positions_cartesian = []
    with open(os.path.expanduser(speakers_positions_file)) as tsv:
        for line in csv.reader(tsv, delimiter='\t'):  # You can also use delimiter="\t" rather than giving a dialect.
            speaker_positions_cartesian.append([float(element) for element in line])

    # Convert speaker_positions to spherical coordinates
    speaker_positions_spherical = [cartesian_to_spherical(pos) for pos in speaker_positions_cartesian]

    return speaker_positions_spherical

######### S3A CONFIG #########

# Container for storing specfic S3A reverb configuration values
S3aReverbSpec = namedtuple(
    'S3aReverbSpec',
    ['name'
     # TODO: add source position constrains type (random, magnet, etc)
     ], verbose=False)

S3A_LOUDSPEAKER_POSITIONS_TXTFILE = "LsPos.txt"

# Filters are named by 'lsX.wav', with X the speaker number
S3A_FILTER_NAME = 'ls'
S3A_FILTER_EXTENSION = '.wav'

S3A_FOLDER_NAME = "IRs"
S3A_FOLDER_PATH = os.path.join(os.getcwd(), S3A_FOLDER_NAME)



######### SMIR CONFIG #########

# Container for storing specfic SMIR reverb configuration values
SmirReverbSpec = namedtuple(
    'SmirReverbSpec',
    ['IRlength',
     'room_dimensions',
     'beta',
     'source_type',
     'microphone_type'
     ], verbose=False)

# omnidirectional/subcardioid/cardioid/hypercardioid/bidirectional
SMIR_ALLOWED_SOURCE_TYPES = ['o', 'c', 's', 'h', 'b']


# Location of the smir module
SMIR_FOLDER_NAME = "SMIR-Generator-master"
SMIR_FOLDER_PATH = os.path.join(os.getcwd(), SMIR_FOLDER_NAME)

# Location of the matlab app
MATLAB_ROOT = "/Applications/MATLAB_R2017b.app"

# Store useful information from each mic:
# - Sphere type (rigid or open)
# - Sphere radius
# - Maximum ambisonics order (it could be computed from the number of capsules,
#     but we specify it for avoiding computations)
# - Spherical coordinates of the capsules
#
# Info gathered from Farina, http://pcfarina.eng.unipr.it/SPS-conversion.htm
# More info at https://www.mhacoustics.com/sites/default/files/ReleaseNotes.pdf
SMIR_SUPPORTED_VIRTUAL_MICS = {

    "soundfield": {
        "sph_type": 'rigid',
        "sph_radius": 0.02, # todo: get real measurement!
        "max_ambi_order": 1,
        "mic":  [[0.0, 0.61547970867038726],       # FLU
                [np.pi/2, -0.61547970867038726],  # FRD
                [np.pi, -0.61547970867038726],  # BLD
                [3*np.pi/2, 0.61547970867038726]]   # BRU
    },

    "tetramic": {
        "sph_type": 'rigid',
        "sph_radius": 0.02, # todo: get real measurement!
        "max_ambi_order": 1,
        "mic":  [[0.0, 0.61547970867038726],       # FLU
                [np.pi/2, -0.61547970867038726],  # FRD
                [np.pi, -0.61547970867038726],  # BLD
                [3*np.pi/2, 0.61547970867038726]]   # BRU
    },

    "em32":  {
        "sph_type": 'rigid',
        "sph_radius": 0.042, # todo: get real measurement!
        "max_ambi_order": 4,
        "mic":  [[0.0, 0.3665191429188092],
                [0.5585053606381855, 0.0],
                [0.0, -0.3665191429188092],
                [5.7246799465414, 0.0],
                [0.0, 1.0122909661567112],
                [np.pi / 4, 0.61547970867038726],  # FLU
                [1.2042771838760873, 0.0],
                [np.pi / 4, -0.61547970867038726],  # FLD
                [0.0, -1.0122909661567112],
                [7 * np.pi / 4, -0.61547970867038726],  # FRD
                [5.078908123303498, 0.0],
                [7 * np.pi / 4, 0.61547970867038726],  # FRU
                [1.5882496193148399, 1.2042771838760873],
                [np.pi / 2, 0.5585053606381855],
                [np.pi / 2, -0.5410520681182421],
                [1.5533430342749535, -1.2042771838760873],
                [np.pi, 0.3665191429188092],
                [3.7000980142279785, 0.0],
                [np.pi, -0.3665191429188092],
                [2.5830872929516078, 0.0],
                [np.pi, 1.0122909661567112],
                [5 * np.pi / 4, 0.61547970867038726],  # BRU
                [4.34586983746588, 0.0],
                [5 * np.pi / 4, -0.61547970867038726],  # BRD
                [np.pi, -1.0122909661567112],
                [3 * np.pi / 4, -0.61547970867038726],  # BLD
                [1.9373154697137058, 0.0],
                [3 * np.pi / 4, 0.61547970867038726],  # BLU
                [4.694935687864747, 1.2042771838760873],
                [4.71238898038469, 0.5585053606381855],
                [4.71238898038469, -0.5585053606381855],
                [4.729842272904633, -1.2042771838760873]]
    }
}