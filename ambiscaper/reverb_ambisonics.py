'''
Ambisonics reverb related methods
=================================
'''
from pysofaconventions import SOFAError

'''
reverb_ambisonics.py
Created by Andres Perez Lopez on 09/01/2018

Convenience declarations and methods
for the ambisonics reverb

Currently supporrting two IR acquisition methods:
- Recorded Ambisonics IRs
- Synthetic Ambisonic IRs through SMIR generator (matlab)
'''

import csv
from collections import namedtuple
from numbers import Number
import numpy as np
import os
import glob
import warnings

from ambiscaper.ambiscaper_warnings import AmbiScaperWarning
from ambiscaper.util import _validate_distribution, degree_to_radian, radian_to_degree, cartesian_to_spherical_degree, \
    spherical_degree_to_cartesian
from ambiscaper.ambiscaper_exceptions import AmbiScaperError
from ambiscaper.util import find_element_in_list, cartesian_to_spherical

import pysofaconventions




# class AmbiScaperReverb():
#
    # @classmethod
    # def get_maximum_ambisonics_order_from_spec(self, reverb_spec):
    #     '''
    #     Compute the maximum ambisonics order given a reverb configuration
    #
    #     :param reverb_spec:
    #
    #         a valid instance of ``reverb_spec``
    #
    #     :raises: AmbiScaperError
    #
    #         If ``reverb_spec`` is not valid.
    #
    #     :return: The maximum ambisonics order allowed
    #
    #     .. note::
    #         The maximum ambisonics order L is defined by the number of microphone capsules,
    #         ``K <= Q``,
    #         where ``K`` is the number of ambisonics components ``K = (L+1)^2``,
    #         and ``Q`` the number of capsules.
    #
    #         For more information, please refer to
    #         *3D Sound Field Recording With Higher Order Ambisonics - Objective Measurements and Validation of a 4th Order Spherical Microphone
    #         (Moreau, Daniel and Bertet, 2006)*.
    #         http://160.78.24.2/Public/phd-thesis/aes120_hoamicvalidation.pdf (accessed January 2018)
    #     '''
    #
    #     # TODO TODO TODO TODO TODO probably move to core
    #
    #     if isinstance(reverb_spec, SmirReverbSpec):
    #         Q = len(SmirReverb.supported_virtual_mics[reverb_spec.microphone_type]['capsule_position_sph'])
    #         return int(np.floor(np.sqrt(Q) - 1))
    #
    #     elif isinstance(reverb_spec, SOFAReverbSpec):
    #         # TODO: for the moment we only have order 1 recordings, so let's just do a dirty hardcode
    #         sofafile = pysofaconventions.SOFAAmbisonicsDRIR(reverb_spec.name, 'r')
    #         order = sofafile.getGlobalAttributeValue('AmbisonicsOrder')
    #         sofafile.close()
    #         return int(order)
    #
    #     else:
    #         raise AmbiScaperError(
    #             'Not valid reverb_spec'
    #         )

### SIMULATED REVERBS ------------------------


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


# class SmirReverb(AmbiScaperReverb):
class SmirReverb():
    ######### SMIR CONFIG #########


    # Smir default (non-configurable) values

    sound_speed = 343.0
    num_harmonics = 30.0
    oversampling_factor = 1.0
    defualt_source_radius = 1.0
    high_pass_filter = 1.0
    reflection_order = -1.0
    reflection_coef_angle_dependency = 0.0



    allowed_source_types = ['o', 'c', 's', 'h', 'b']
    ''' 
    The source directivity patterns allowed in SMIR Generator
            - 'o': omnidirectional 
            - 'c': cardioid 
            - 's': subcardioid 
            - 'h': hypercardioid 
            - 'b': bidirectional 
    '''

    # Location of the smir module
    folder_name = "SMIR-Generator-master"
    folder_path = os.path.join(os.getcwd(), folder_name)

    # Location of the matlab app
    matlab_root = "/Applications/MATLAB_R2017b.app"

    supported_virtual_mics = {
        '''Store useful information from each mic
    
            - Sphere type (rigid or open)
            - Sphere radius
            - Maximum ambisonics order (it could be computed from the number of capsules, but we specify it for avoiding computations)
            - Spherical coordinates of the capsules
    
        Info gathered from Farina, http://pcfarina.eng.unipr.it/SPS-conversion.htm
    
        More info at https://www.mhacoustics.com/sites/default/files/ReleaseNotes.pdf
        '''
        
        "soundfield": {
            "sph_type": 'open',
            "sph_radius": 0.042,  # todo: get real measurement!
            "capsule_position_sph": [[0.0, np.pi / 4],  # FLU
                                     [np.pi / 2, -1 * np.pi / 4],  # FRD
                                     [np.pi, np.pi / 4],  # BLD
                                     [3 * np.pi / 2, -1 * np.pi / 4]]  # BRU
        },

        "tetramic": {
            "sph_type": 'open',
            "sph_radius": 0.02,  # todo: get real measurement!
            "capsule_position_sph": [[0.0, 0.61547970867038726],  # FLU
                                     [np.pi / 2, -0.61547970867038726],  # FRD
                                     [np.pi, 0.61547970867038726],  # BLD
                                     [3 * np.pi / 2, -0.61547970867038726]]  # BRU
        },

        "em32": {
            "sph_type": 'rigid',
            "sph_radius": 0.042,  # todo: get real measurement!
            "capsule_position_sph": [[0.0, 0.3665191429188092],
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



    def _validate_smir_reverb_spec(self,IRlength, room_dimensions,
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
        self._validate_IR_length(IRlength)

        # ROOM DIMENSIONS
        self._validate_room_dimensions(room_dimensions)

        # We must define either t60 or reflectivity, but not none
        # If both are defined, just raise a warning
        if reflectivity is None:
            if t60 is None:
                raise AmbiScaperError(
                    'reverb_config: Neither t60 nor reflectivity defined!')
            else:
                # T60
                self._validate_t60(t60)
        elif t60 is None:
            # REFLECTIVITY
            self._validate_wall_reflectivity(reflectivity)
        else:
            # T60
            self._validate_t60(t60)
            raise AmbiScaperWarning(
                'reverb_config: Both t60 and reflectivity defined!' +
                'Using t60 by default')

        # SOURCE TYPE
        self._validate_source_type(source_type)

        # MYCROPHONE TYPE
        self._validate_microphone_type(microphone_type)

    def _validate_IR_length(self,IRlenght_tuple):
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

    def _validate_room_dimensions(self,room_dimensions_tuple):
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

    def _validate_t60(self,t60_tuple):
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

    def _validate_wall_reflectivity(self,wall_reflectivity_tuple):
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
                    'reverb_config: wall_reflectivity must be a list of 6 floats between 0 and 1')

        elif wall_reflectivity_tuple[0] == "choose":
            if not wall_reflectivity_tuple[1]:  # list is empty
                raise AmbiScaperError(
                    'reverb_config: wall_reflectivity_tuple list empty')
            elif not all(_valid_wall_reflectivity_values(wall_reflectivity)
                         for wall_reflectivity in wall_reflectivity_tuple[1]):
                raise AmbiScaperError(
                    'reverb_config: wall_reflectivity must be a list of 6 floats between 0 and 1')

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

    def _validate_source_type(self,source_type_tuple):
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

    def _validate_microphone_type(self,mic_type_tuple):
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
            if not mic_type_tuple[1] in self.supported_virtual_mics.keys():
                raise AmbiScaperError(
                    'Microphone type value must match one of the available labels: '
                    '{:s}'.format(str(self.supported_virtual_mics.keys())))
        elif mic_type_tuple[0] == "choose":
            if mic_type_tuple[1]:  # list is not empty
                if not set(mic_type_tuple[1]).issubset(set(self.supported_virtual_mics.keys())):
                    raise AmbiScaperError(
                        'Microphone type provided must be a subset of the available '
                        'labels: {:s}'.format(str(self.supported_virtual_mics.keys())))
        else:
            raise AmbiScaperError(
                'Microphone type must be specified using a "const" or "choose" tuple.')



    def get_max_ambi_order_from_reverb_config(self, reverb_spec):
        '''
        Compute the maximum ambisonics order given a reverb configuration

        :param reverb_spec:

            a valid instance of ``reverb_spec``

        :raises: AmbiScaperError

            If ``reverb_spec`` is not valid.

        :return: The maximum ambisonics order allowed

        .. note::
            The maximum ambisonics order L is defined by the number of microphone capsules,
            ``K <= Q``,
            where ``K`` is the number of ambisonics components ``K = (L+1)^2``,
            and ``Q`` the number of capsules.

            For more information, please refer to
            *3D Sound Field Recording With Higher Order Ambisonics - Objective Measurements and Validation of a 4th Order Spherical Microphone
            (Moreau, Daniel and Bertet, 2006)*.
            http://160.78.24.2/Public/phd-thesis/aes120_hoamicvalidation.pdf (accessed January 2018)
        '''

        # TODO TODO TODO TODO TODO probably move to core

        Q = len(self.supported_virtual_mics[reverb_spec.microphone_type]['capsule_position_sph'])
        return int(np.floor(np.sqrt(Q) - 1))



    def get_receiver_position(room_dimensions):
        '''
        TODO: for the moment just the center
        :param room_dimensions:
        :return:
        '''

        if not isinstance(room_dimensions,list) or len(room_dimensions) != 3:
            raise AmbiScaperError(
                'Incorrect room dimensions'
            )

        return [float(l) / 2.0 for l in room_dimensions]


### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------
### RECORDED REVERBS ------------------------



# Container for storing specfic recorded reverb configuration values
SOFAReverbSpec = namedtuple(
    'SOFAReverbSpec',
    ['name',
     'wrap'
    ], verbose=False)

######## CLASS

# class SOFAReverb(AmbiScaperReverb):
class SOFAReverb():

    valid_wrap_values = ['random', 'wrap_azimuth', 'wrap_elevation', 'wrap_surface']

    def __init__(self):
        self.sofa_reverb_folder_path = None


    def get_sofa_reverb_folder_path(self):
        """
        Retrieve the base path where to find the AmbisonicsDRIR SOFA files

        :return: The path to the folder, or None if not set
        """
        return self.sofa_reverb_folder_path


    def set_sofa_reverb_folder_path(self, path):
        """
        Set the base path where to find the AmbisonicsDRIR SOFA files

        :param path:

            The path to the folder

        :raises: AmbiScaperError

            If the provided path does not exist or is not a folder
        """
        if not os.path.exists(path):
            raise AmbiScaperError(
                "The provided SOFA reverb folder path does not exist! " + path)

        if not os.path.isdir(path):
            raise AmbiScaperError(
                "The provided SOFA reverb path is not a folder! " + path)

        self.sofa_reverb_folder_path = path



    def retrieve_available_sofa_reverb_files(self):
        '''
        Get a list of the existing SOFA files at the current SOFA path (recursively).

        :return:

            An array containing all available sofa files (not tested for validity)

        :raises: AmbiScaper error

            If the sofa folder is not specified
        '''

        if not self.sofa_reverb_folder_path:
            raise AmbiScaperError(
                "SOFA reverb folder path is not specified!")

        available_sofa_files = []
        for (dirpath, dirnames, filenames) in os.walk(self.sofa_reverb_folder_path):
            for file in filenames:
                if os.path.splitext(file)[-1] == '.sofa':
                    available_sofa_files.append(os.path.join(os.path.split(dirpath)[-1], file))

        return available_sofa_files

    def generate_sofa_file_full_path(self, sofa_reverb_name):
        '''
        Return full path to a SOFA Ambisonics reverb given a reverb name

        :param sofa_reverb_name: string referencing to a valid recorded reverb name

        :raises: AmbiScaper Error if reverb name is not valid, or if sofa path is not specified
        '''

        if not isinstance(sofa_reverb_name,str):
            raise AmbiScaperError(
                'Not valid reverb name type')
        elif not self.sofa_reverb_folder_path:
            raise AmbiScaperError(
                "SOFA reverb folder path is not specified!")
        elif find_element_in_list(sofa_reverb_name, self.retrieve_available_sofa_reverb_files()) is None:
            raise AmbiScaperError(
                'Reverb name does not exist: ', sofa_reverb_name)

        return os.path.expanduser(os.path.join(self.sofa_reverb_folder_path, sofa_reverb_name))





    def _validate_reverb_spec(self, reverb_name_tuple, reverb_wrap_tuple):

        self._validate_reverb_name(reverb_name_tuple)
        self._validate_reverb_wrap(reverb_wrap_tuple)
        return



    def _validate_reverb_name(self, reverb_name_tuple):

        # Make sure that type matches
        def __validate_reverb_name_types(reverb_name):
            if not isinstance(reverb_name, str):
                raise AmbiScaperError(
                    'reverb_config: reverb name must be a string')

        # Make sure that the sofa file exists and is valid
        def __validate_reverb_name_configuration(reverb_name):

            reverb_full_path = self.sofa_reverb_folder_path +'/' +reverb_name

            # The provided name should exist in sofa_reverb_folder_path
            if not os.path.exists(os.path.expanduser(reverb_full_path)):
                raise AmbiScaperError(
                    'reverb_config: file does not exist: ' + reverb_full_path)

            # TODO
            # The file should be a valid AmbisonicsDRIR file
            sofa_file = pysofaconventions.SOFAAmbisonicsDRIR(reverb_full_path,'r')
            if not sofa_file.isValid():
                sofa_file.close()
                raise AmbiScaperError(
                    'reverb_config: file is not a valid AmbisonicsDRIR SOFA file: ' + reverb_name)
            sofa_file.close()


        # Make sure it's a valid distribution tuple
        _validate_distribution(reverb_name_tuple)

        # If reverb name is specified explicitly
        if reverb_name_tuple[0] == "const":

            # reverb name: allowed string
            if reverb_name_tuple[1] is None:
                raise AmbiScaperError(
                    'reverb_config: reverb name is None'
                )
            __validate_reverb_name_types(reverb_name_tuple[1])
            __validate_reverb_name_configuration(reverb_name_tuple[1])

        # Otherwise it must be specified using "choose"
        # Empty list is allowed, meaning all avaiable IRS
        elif reverb_name_tuple[0] == "choose":
            # Empty list
            [__validate_reverb_name_types(name) for name in reverb_name_tuple[1]]
            [__validate_reverb_name_configuration(name) for name in reverb_name_tuple[1]]

        # No other labels allowed"
        else:
            raise AmbiScaperError(
                'Reverb name must be specified using a "const" or "choose" tuple.')


    def _validate_reverb_wrap(self, reverb_wrap_tuple):
        '''

        :param reverb_wrap:
        :return:
        '''

        # Make sure it's a valid distribution tuple
        _validate_distribution(reverb_wrap_tuple)

        # Make sure that type matches
        def __valid_reverb_wrap_types(reverb_wrap):
            if (not isinstance(reverb_wrap, str)):
                return False
            else:
                return True

        def __valid_reverb_wrap_values(reverb_wrap):
            if reverb_wrap not in self.valid_wrap_values:
                return False
            else:
                return True

        # If reverb wrap is specified explicitly
        if reverb_wrap_tuple[0] == "const":

            # reverb wrap: allowed string
            if reverb_wrap_tuple[1] is None:
                raise AmbiScaperError(
                    'reverb_config: reverb wrap is None')
            elif not __valid_reverb_wrap_types(reverb_wrap_tuple[1]):
                raise AmbiScaperError(
                    'reverb_config: reverb wrap must be a string')
            elif not __valid_reverb_wrap_values(reverb_wrap_tuple[1]):
                raise AmbiScaperError(
                    'reverb_config: reverb wrap not valid:' + reverb_wrap_tuple[1])

        # Otherwise it must be specified using "choose"
        # Empty list is allowed, meaning all avaiable IRS
        elif reverb_wrap_tuple[0] == "choose":

            if not all(__valid_reverb_wrap_types(length) for length in reverb_wrap_tuple[1]):
                raise AmbiScaperError(
                    'reverb_config: reverb wrap must be a string')
            elif not all(__valid_reverb_wrap_values(name) for name in reverb_wrap_tuple[1]):
                raise AmbiScaperError(
                    'reverb_config: reverb names not valid: ' + str(reverb_wrap_tuple[1]))

        # No other labels allowed"
        else:
            raise AmbiScaperError(
                'Reverb wrap must be specified using a "const" or "choose" tuple.')



    def get_relative_speaker_positions_spherical(self, sofa_reverb_name):
        '''
        Retrieve apparent speaker positions from a SOFA file.
        The method takes into account the Listener position and ordientation,
        so it is not necessarily equal to the EmitterPosition list

        :param sofa_reverb_name: string referencing to a valid SOFA reverb name

        :return: ndarray of shape (E,C) containing speaker positions in the format ``[azimuth, elevation, distance]`` (in radians).

        :raises: AmbiScaperError

            If ``sofa_reverb_name`` is not valid

        :raises: SOFAError

            If there is a problem associated with the SOFA file

        '''

        # TODO: only using M=0 for the moment!!!

        # Open the file
        try:
            sofa_reverb_file_path = self.generate_sofa_file_full_path(sofa_reverb_name)
            sofa_file = pysofaconventions.SOFAAmbisonicsDRIR(sofa_reverb_file_path, 'r')

            # Load dimensions
            m = 0 # Hardcoded. Extend it when needed
            num_emitters = sofa_file.getDimensionSize('E')

            # Load variables
            listener_position = sofa_file.getListenerPositionValues()
            listener_position_units, listener_position_coordinates = sofa_file.getListenerPositionInfo()
            if sofa_file.hasListenerUp():
                # TODO: up not used
                listener_up = sofa_file.getListenerUpValues()
                listener_up_units, listener_up_coordinates = sofa_file.getListenerUpInfo()
                listener_view = sofa_file.getListenerViewValues()
                listener_view_units, listener_view_coordinates = sofa_file.getListenerViewInfo()

            source_position = sofa_file.getSourcePositionValues()
            source_position_units, source_position_coordinates = sofa_file.getSourcePositionInfo()
            if sofa_file.hasSourceUp():
                # TODO: up not used
                source_up = sofa_file.getSourceUpValues()
                source_up_units, source_up_coordinates = sofa_file.getSourceUpInfo()
                source_view = sofa_file.getSourceViewValues()
                source_view_units, source_view_coordinates = sofa_file.getSourceViewInfo()

            emitter_position = sofa_file.getEmitterPositionValues()
            emitter_position_units, emitter_position_coordinates = sofa_file.getEmitterPositionInfo()

            sofa_file.close()

            # iterate over emitters...
            relative_speaker_positions = []
            for e in range(num_emitters):

                # Compute triangle!!
                E_local_spherical = emitter_position[e, :, m] # Only first measurement!
                if emitter_position_coordinates == 'cartesian':
                    E_local_spherical = np.asarray(cartesian_to_spherical_degree(E_local_spherical))
                if sofa_file.hasSourceView():
                    S_view_spherical = source_view[m, :]
                    if source_view_coordinates == 'cartesian':
                        S_view_spherical = np.asarray(cartesian_to_spherical_degree(S_view_spherical))
                    E_local_spherical[:-1] -= S_view_spherical[:-1]

                # 1.2 Translation with respect to SourcePosition
                E_local_cartesian = np.asarray(spherical_degree_to_cartesian(E_local_spherical))

                S = source_position[m, :]
                if source_position_coordinates == 'spherical':
                    S = np.asarray(spherical_degree_to_cartesian(S))
                E = E_local_cartesian + S
                L = listener_position[m, :]
                if listener_position_coordinates == 'spherical':
                    L = np.asarray(spherical_degree_to_cartesian(L))

                # 2. Get listener view
                if sofa_file.hasListenerView():
                    L_view = listener_view[m, :]
                    if listener_view_coordinates == 'cartesian':
                        L_view = np.asarray(cartesian_to_spherical_degree(L_view))
                else:
                    L_view = np.asarray([0., 0., 1.])  # Nop, in spherical

                # 4. Compute relative angle from L to E
                LE_vector = E - L

                # Source and Listener are at the same position: no triangle
                if np.allclose(LE_vector,np.zeros(3)):
                    # Force not nan in elevation
                    LE_angle = np.zeros(3)
                else:
                    LE_angle = np.asarray(cartesian_to_spherical_degree(LE_vector))  # this is already the angle respect to center

                LE_angle[2] = np.linalg.norm(LE_vector)

                # 5. Get relative position
                relative_position = LE_angle - L_view
                # to radians...
                relative_position[0] = degree_to_radian(relative_position[0])
                relative_position[1] = degree_to_radian(relative_position[1])
                relative_position[2] = np.linalg.norm(LE_vector)

                relative_speaker_positions.append(relative_position)

            return np.asarray(relative_speaker_positions)

        except (AmbiScaperError,SOFAError) as e:
            raise e


######### RECORDED REVERB CONFIG #########

    def get_maximum_ambisonics_order_from_spec(self, reverb_spec):
        '''
        Compute the maximum ambisonics order given a reverb configuration

        :param reverb_spec:

            a valid instance of ``SOFAReverbSpec``

        :raises: AmbiScaperError

            If ``reverb_spec`` is not valid

        :raises: SOFAError

            If attribute 'AmbisonicsOrder' is not found

        :return: The maximum ambisonics order allowed, as int

        '''
        try:
            full_path = self.generate_sofa_file_full_path(reverb_spec.name)
        except AmbiScaperError as e:
            raise e
        sofafile = pysofaconventions.SOFAAmbisonicsDRIR(full_path, 'r')
        try:
            # TODO
            order = sofafile.getGlobalAttributeValue('AmbisonicsOrder')
        except pysofaconventions.SOFAError as e:
            sofafile.close()
            raise e
        sofafile.close()
        return int(order)



# RECORDED_REVERB_LOUDSPEAKER_POSITIONS_TXTFILE = "LsPos.txt"

# Filters are named by 'lsX.wav', with X the speaker number
# RECORDED_REVERB_FILTER_NAME = 'ls'
# RECORDED_REVERB_FILTER_EXTENSION = '.wav'

# RECORDED_REVERB_FOLDER_NAME = "IRs"
# RECORDED_REVERB_FOLDER_PATH = os.path.join(os.getcwd(), RECORDED_REVERB_FOLDER_NAME)



