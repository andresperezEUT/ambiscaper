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
import warnings

from ambiscaper.ambiscaper_warnings import AmbiScaperWarning
from ambiscaper.util import _validate_distribution
from ambiscaper.ambiscaper_exceptions import AmbiScaperError
from ambiscaper.util import find_element_in_list, cartesian_to_spherical



def _validate_smir_reverb_spec(IRlength, room_dimensions,
                               t60, reflectivity,
                               source_type, microphone_type):
    # TODO
    '''
    Check that event parameter values are valid.

    Parameters
    ----------
    label : tuple
    source_file : tuple
    source_time : tuple
    event_time : tuple
    event_duration : tuple
    event_azimuth : tuple
    event_elevation : tuple
    event_spread : tuple
    snr : tuple
    allowed_labels : list
        List of allowed labels for the event.
    pitch_shift : tuple or None
    time_stretch: tuple or None

    Raises
    ------
    AmbiScaperError :
        If any of the input parameters has an invalid format or value.

    See Also
    --------
    AmbiScaper.add_event : Add a foreground sound event to the foreground
    specification.
    '''

    # IR LENGTH
    _validate_IR_length(IRlength)

    # ROOM DIMENSIONS
    _validate_room_dimensions(room_dimensions)

    # We must define either t60 or reflectivity, but not none
    # If both are defined, just raise a warning
    if reflectivity is None:
        if t60 is None:
            raise AmbiScaperError(
                'reverb_config: Neither t60 nor reflectivity defined!')
        else:
            # T60
            _validate_t60(t60)
    elif t60 is None:
        # REFLECTIVITY
        _validate_wall_reflectivity(reflectivity)
    else:
        raise AmbiScaperWarning(
            'reverb_config: Both t60 and reflectivity defined!')

    # SOURCE TYPE
    _validate_source_type(source_type)

    # MYCROPHONE TYPE
    _validate_microphone_type(microphone_type)

def _validate_IR_length(IRlenght_tuple):
    '''
    TODO
    :param IRlenght_tuple:
    :return:
    '''

    # Make sure it's a valid distribution tuple
    _validate_distribution(IRlenght_tuple)

    def __valid_IR_length_values(IRlength):
        if (not isinstance(IRlength, int) or
                    IRlength <= 0):
            return False
        else:
            return True


    # If IR length is specified explicitly
    if IRlenght_tuple[0] == "const":

        # IR length: positive integer
        if IRlenght_tuple[1] is None:
            raise AmbiScaperError(
                'reverb_config: IR length is None')
        elif not __valid_IR_length_values(IRlenght_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: IR length must be a positive integer')

    # Otherwise it must be specified using "choose"
    elif IRlenght_tuple[0] == "choose":
        if not IRlenght_tuple[1]:  # list is empty
            raise AmbiScaperError(
                'reverb_config: IR length list empty')
        elif not all(__valid_IR_length_values(length) for length in IRlenght_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: IR length must be a positive integer')

    # No other labels allowed"
    else:
        raise AmbiScaperError(
            'IR length must be specified using a "const" or "choose" tuple.')

def _validate_room_dimensions(room_dimensions_tuple):
    '''
    TODO
    :param room_dimensions_tuple:
    :return:
    '''

    def _valid_room_dimensions_values(room_dimensions):
        # room_dimensions: list of 3 Numbers
        if (room_dimensions is None or
                not isinstance(room_dimensions, list) or
                not all(isinstance(dim,Number) for dim in room_dimensions) or
                len(room_dimensions) is not 3):
            return False
        else:
            return True

    # Make sure it's a valid distribution tuple
    _validate_distribution(room_dimensions_tuple)

    # If room_dimensions is specified explicitly
    if room_dimensions_tuple[0] == "const":
        if not _valid_room_dimensions_values(room_dimensions_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: room dimensions must be a list of 3 elements')

    elif room_dimensions_tuple[0] == "choose":
        if not room_dimensions_tuple[1]:  # list is empty
            raise AmbiScaperError(
                'reverb_config: room_dimensions_tuple list empty')
        elif not all(_valid_room_dimensions_values(room_dimensions)
                     for room_dimensions in room_dimensions_tuple[1]):
            raise AmbiScaperError(
                     'reverb_config: room dimensions must be a list of 3 elements')

    elif room_dimensions_tuple[0] == "uniform":
        if room_dimensions_tuple[1] < 0:
            raise AmbiScaperError(
                'A "uniform" distribution tuple for room dimensions must have '
                'min_value >= 0')

    elif room_dimensions_tuple[0] == "normal":
        warnings.warn(
            'A "normal" distribution tuple for room dimensions can result in '
            'negative values, in which case the distribution will be '
            're-sampled until a positive value is returned: this can result '
            'in an infinite loop!',
            AmbiScaperWarning)

    elif room_dimensions_tuple[0] == "truncnorm":
        if room_dimensions_tuple[3] < 0:
            raise AmbiScaperError(
                'A "truncnorm" distirbution tuple for room dimensions must specify a non-'
                'negative trunc_min value.')

def _validate_t60(t60_tuple):
    '''
    TODO
    :param beta_tuple:
    :return:
    '''

    def _valid_t60_values(t60):
        # t60: float bigger than 0
        if (t60 is None or
            not isinstance(t60,float) or
            t60 <= 0):
            return False
        else:
            return True

    # Make sure it's a valid distribution tuple
    _validate_distribution(t60_tuple)

    # If t60 is specified explicitly
    if t60_tuple[0] == "const":
        if not _valid_t60_values(t60_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: t60 must be a float >0')

    elif t60_tuple[0] == "choose":
        if not t60_tuple[1]:  # list is empty
            raise AmbiScaperError(
                'reverb_config: t60_tuple list empty')
        elif not all(_valid_t60_values(t60)
                     for t60 in t60_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: t60 must be a float >0')

    elif t60_tuple[0] == "uniform":
        if t60_tuple[1] < 0:
            raise AmbiScaperError(
                'A "uniform" distribution tuple for t60 must have '
                'min_value >= 0')

    elif t60_tuple[0] == "normal":
        warnings.warn(
            'A "normal" distribution tuple for t60 can result in '
            'negative values, in which case the distribution will be '
            're-sampled until a positive value is returned: this can result '
            'in an infinite loop!',
            AmbiScaperWarning)

    elif t60_tuple[0] == "truncnorm":
        if t60_tuple[3] < 0:
            raise AmbiScaperError(
                'A "truncnorm" distirbution tuple for t60 must specify a non-'
                'negative trunc_min value.')

def _validate_wall_reflectivity(wall_reflectivity_tuple):
    '''
    TODO
    :param wall_reflectivity_tuple:
    :return:
    '''

    def _valid_wall_reflectivity_values(wall_reflectivity):
        # wall_reflectivity: list of 6 floats in the range [0,1]
        if (wall_reflectivity is None or
                not isinstance(wall_reflectivity, list) or
                len(wall_reflectivity) is not 6 or
                not all(isinstance(r, float) and 0<=r<=1 for r in wall_reflectivity)):
            return False
        else:
            return True

    # Make sure it's a valid distribution tuple
    _validate_distribution(wall_reflectivity_tuple)

    # If wall_reflectivity is specified explicitly
    if wall_reflectivity_tuple[0] == "const":
        if not _valid_wall_reflectivity_values(wall_reflectivity_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: wall_reflectivity must be a list of 3 elements')

    elif wall_reflectivity_tuple[0] == "choose":
        if not wall_reflectivity_tuple[1]:  # list is empty
            raise AmbiScaperError(
                'reverb_config: wall_reflectivity_tuple list empty')
        elif not all(_valid_wall_reflectivity_values(wall_reflectivity)
                     for wall_reflectivity in wall_reflectivity_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: wall_reflectivity must be a list of 3 elements')

    elif wall_reflectivity_tuple[0] == "uniform":
        if wall_reflectivity_tuple[1] < 0:
            raise AmbiScaperError(
                'A "uniform" distribution tuple for wall_reflectivity must have '
                'min_value >= 0')
        elif wall_reflectivity_tuple[2] > 1:
            raise AmbiScaperError(
                'A "uniform" distribution tuple for wall_reflectivity must have '
                'max_value <= 1')

    elif wall_reflectivity_tuple[0] == "normal":
        warnings.warn(
            'A "normal" distribution tuple for wall_reflectivity can result in '
            'values outside [0,1], in which case the distribution will be '
            're-sampled until a positive value is returned: this can result '
            'in an infinite loop!',
            AmbiScaperWarning)

    elif wall_reflectivity_tuple[0] == "truncnorm":
        if wall_reflectivity_tuple[3] < 0:
            raise AmbiScaperError(
                'A "uniform" distribution tuple for wall_reflectivity must have '
                'min_value >= 0')
        elif wall_reflectivity_tuple[4] > 1:
            raise AmbiScaperError(
                'A "uniform" distribution tuple for wall_reflectivity must have '
                'max_value <= 1')

def _validate_source_type(source_type_tuple):
    '''
    Validate that a source_type tuple is in the right format and that it's values
    are valid.

    Parameters
    ----------
    source_type_tuple : tuple
        Label tuple (see ```AmbiScaper.add_event``` for required format).

    Raises
    ------
    AmbiScaperError
        If the validation fails.

    '''
    # Make sure it's a valid distribution tuple
    _validate_distribution(source_type_tuple)

    # Make sure it's one of the allowed distributions for a source_type and that the
    # source_type value is one of the allowed labels.
    if source_type_tuple[0] == "const":
        if not source_type_tuple[1] in SMIR_ALLOWED_SOURCE_TYPES:
            raise AmbiScaperError(
                'Source type value must match one of the available labels: '
                '{:s}'.format(str(SMIR_ALLOWED_SOURCE_TYPES)))
    elif source_type_tuple[0] == "choose":
        if source_type_tuple[1]:  # list is not empty
            if not set(source_type_tuple[1]).issubset(set(SMIR_ALLOWED_SOURCE_TYPES)):
                raise AmbiScaperError(
                    'Source type provided must be a subset of the available '
                    'labels: {:s}'.format(str(SMIR_ALLOWED_SOURCE_TYPES)))
    else:
        raise AmbiScaperError(
            'Source type must be specified using a "const" or "choose" tuple.')

def _validate_microphone_type(mic_type_tuple):
    '''
    Validate that a mic_type tuple is in the right format and that it's values
    are valid.

    Parameters
    ----------
    mic_type_tuple : tuple
        Label tuple (see ```AmbiScaper.add_event``` for required format).

    Raises
    ------
    AmbiScaperError
        If the validation fails.

    '''
    # Make sure it's a valid distribution tuple
    _validate_distribution(mic_type_tuple)

    # Make sure it's one of the allowed distributions for a mic_type and that the
    # mic_type value is one of the allowed labels.
    if mic_type_tuple[0] == "const":
        if not mic_type_tuple[1] in SMIR_SUPPORTED_VIRTUAL_MICS.keys():
            raise AmbiScaperError(
                'Microphone type value must match one of the available labels: '
                '{:s}'.format(str(SMIR_SUPPORTED_VIRTUAL_MICS.keys())))
    elif mic_type_tuple[0] == "choose":
        if mic_type_tuple[1]:  # list is not empty
            if not set(mic_type_tuple[1]).issubset(set(SMIR_SUPPORTED_VIRTUAL_MICS.keys())):
                raise AmbiScaperError(
                    'Microphone type provided must be a subset of the available '
                    'labels: {:s}'.format(str(SMIR_SUPPORTED_VIRTUAL_MICS.keys())))
    else:
        raise AmbiScaperError(
            'Microphone type must be specified using a "const" or "choose" tuple.')


def _validate_s3a_reverb_spec(reverb_name_tuple):

    # Just one element for the moment
    _validate_s3a_reverb_name(reverb_name_tuple)

    return


def _validate_s3a_reverb_name(reverb_name_tuple):

    # Make sure it's a valid distribution tuple
    _validate_distribution(reverb_name_tuple)

    # Make sure that type matches
    def __valid_s3a_reverb_name_types(reverb_name):
        if (not isinstance(reverb_name, str)):
            return False
        else:
            return True

    # Make sure that the audio and position files exist and are valid
    def __valid_s3a_reverb_name_configuration(reverb_name):
        # Folder structure should be something like:
        # - S3A_top_folder (:s3a_folder_path: defined in ambisonics.py)
        #     - reverb_name (:name: in the config struct)
        #         - (maybe a pdf)
        #         - "Soundfield"
        #             - "lsN.wav" with the N actual impulse responses, starting from 1
        #             - "LsPos.txt" with the loudspeaker positions
        #             - (maybe a "Metadata_SoundField.txt")

        try:
            # The provided name should exist in s3a_
            reverb_folder_path = os.path.join(S3A_FOLDER_PATH, reverb_name)
            if not os.path.exists(os.path.expanduser(reverb_folder_path)):
                raise AmbiScaperError(
                    'reverb_config: folder does not exist: ' + reverb_name)

            # Inside the reverb folder should be a "Soundfield" folder
            soundfield_path = os.path.join(reverb_folder_path, 'Soundfield')
            if not os.path.exists(os.path.expanduser(soundfield_path)):
                raise AmbiScaperError(
                    'reverb_config: Soundfield folder does not exist inside : ' + os.path.expanduser(
                        reverb_folder_path))

            # Check that the "LsPos.txt" file contains as many xyz positions as wav files in the folder

            # Count number of audio files (the actual IRs)
            num_wav_files = len(glob.glob(os.path.expanduser(soundfield_path) + "/*.wav"))

            # Count number of lines in speakers file
            speakers_positions_file = os.path.join(soundfield_path, S3A_LOUDSPEAKER_POSITIONS_TXTFILE)
            num_lines = sum(1 for line in open(os.path.expanduser(speakers_positions_file)))

            # Check
            if num_wav_files is not num_lines:
                raise AmbiScaperError(
                    'reverb_config: the number of audio files does not match with the speaker description')

            result = True

        except AmbiScaperError:
            pass
            result = False

        return result


    # If reverb name is specified explicitly
    if reverb_name_tuple[0] == "const":

        # reverb name: allowed string
        if reverb_name_tuple[1] is None:
            raise AmbiScaperError(
                'reverb_config: reverb name is None')
        elif not __valid_s3a_reverb_name_types(reverb_name_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: reverb name must be a string')
        elif not __valid_s3a_reverb_name_configuration(reverb_name_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: reverb name not valid:' + reverb_name_tuple[1])

    # Otherwise it must be specified using "choose"
    # Empty list is allowed, meaning all avaiable IRS
    elif reverb_name_tuple[0] == "choose":

        if not all(__valid_s3a_reverb_name_types(length) for length in reverb_name_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: reverb name must be a positive integer')
        elif not all(__valid_s3a_reverb_name_configuration(name) for name in reverb_name_tuple[1]):
            raise AmbiScaperError(
                'reverb_config: reverb names not valid: ' + reverb_name_tuple[1])

    # No other labels allowed"
    else:
        raise AmbiScaperError(
            'Reverb name must be specified using a "const" or "choose" tuple.')



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




def retrieve_available_recorded_IRs():

    # List all dirs inside S3A folder path
    # TODO: implement it in a more elegant way

    return [e for e in os.listdir(S3A_FOLDER_PATH) if not e == 'README.md' and not e == '.DS_Store']

def generate_RIR_path(recorded_reverb_name):
    '''
    TODO
    :param s3a_reverg_config:
    :return:
    '''
    # TODO: remove hardcoded reference to Soundfield
    return os.path.expanduser(os.path.join(S3A_FOLDER_PATH, recorded_reverb_name, 'Soundfield'))


def retrieve_RIR_positions(recorded_reverb_name):
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

    speakers_positions_file = os.path.join(generate_RIR_path(recorded_reverb_name), S3A_LOUDSPEAKER_POSITIONS_TXTFILE)

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


# Smir default (non-configurable) values

SMIR_SOUND_SPEED = 343.0
SMIR_NUM_HARMONICS = 36.0
SMIR_OVERSAMPLING_FACTOR = 1.0
SMIR_DEFAULT_SOURCE_RADIUS = 2.0
SMIR_HIGH_PASS_FILTER = 0.0
SMIR_REFLECTION_ORDER = 10.0
SMIR_REFLECTION_COEF_ANGLE_DEPENDENCY = 0.0

# Container for storing specfic SMIR reverb configuration values
SmirReverbSpec = namedtuple(
    'SmirReverbSpec',
    ['IRlength',
     'room_dimensions',
     't60',
     'reflectivity',
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
        "sph_type": 'open',
        "sph_radius": 0.02, # todo: get real measurement!
        "max_ambi_order": 1,
        "capsule_position_sph":  [[0.0, 0.61547970867038726],       # FLU
                [np.pi/2, -0.61547970867038726],  # FRD
                [np.pi, -0.61547970867038726],  # BLD
                [3*np.pi/2, 0.61547970867038726]]   # BRU
    },

    "tetramic": {
        "sph_type": 'open',
        "sph_radius": 0.02, # todo: get real measurement!
        "max_ambi_order": 1,
        "capsule_position_sph":  [[0.0, 0.61547970867038726],       # FLU
                [np.pi/2, -0.61547970867038726],  # FRD
                [np.pi, -0.61547970867038726],  # BLD
                [3*np.pi/2, 0.61547970867038726]]   # BRU
    },

    "em32":  {
        "sph_type": 'rigid',
        "sph_radius": 0.042, # todo: get real measurement!
        "max_ambi_order": 4,
        "capsule_position_sph":  [[0.0, 0.3665191429188092],
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

def get_receiver_position(room_dimensions):
    '''
    TODO: for the moment just the center
    :param room_dimensions:
    :return:
    '''
    return [float(l) / 2.0 for l in room_dimensions]