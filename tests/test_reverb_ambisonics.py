import pytest

import ambiscaper
from ambiscaper.ambiscaper_exceptions import AmbiScaperError
from ambiscaper.ambiscaper_warnings import AmbiScaperWarning

from ambiscaper.reverb_ambisonics import SOFAReverb, SOFAReverbSpec
import numpy as np

import os

#################### SMIR

# def test_validate_smir_reverb_spec():
#
#     def __test_bad_smir_reverb_spec(smir_reverb_spec):
#         pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_smir_reverb_spec, *smir_reverb_spec)
#
#     def __test_warn_smir_reverb_spec(smir_reverb_spec):
#         pytest.raises(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_smir_reverb_spec, *smir_reverb_spec)
#
#     def __test_good_smir_reverb_spec(smir_reverb_spec):
#         try:
#             ambiscaper.reverb_ambisonics._validate_smir_reverb_spec(*smir_reverb_spec)
#         except AmbiScaperError:
#             raise
#
#     IRlengt = ('const',1024)
#     room_dimensions = ('const',[1,2,3])
#     source_type = ('const','o')
#     microphone_type = ('const','soundfield')
#
#     # Incorrect specs: no t60/reflectivity
#     t60 = None
#     reflectivity = None
#     spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
#     __test_bad_smir_reverb_spec(spec)
#
#     # Incorrect specs: both t60/reflectivity
#     t60 = ('const',0.5)
#     reflectivity = ('const',[0.1,0.2,0.3,0.4,0.5,0.6])
#     spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
#     __test_warn_smir_reverb_spec(spec)
#
#     # Correct entries
#     t60 = ('const',0.5)
#     reflectivity = None
#     spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
#     __test_good_smir_reverb_spec(spec)
#
#     t60 = None
#     reflectivity = ('const',[0.1,0.2,0.3,0.4,0.5,0.6])
#     spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
#     __test_good_smir_reverb_spec(spec)
#
#
#
# def test_validate_IR_length():
#
#     def __test_bad_IR_length_tuple(IR_length_tuple):
#         pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_IR_length, IR_length_tuple)
#
#     # bad consts
#     bad_IR_length_values = [None, -1, 1j, 'yes', [], [5]]
#     for biv in bad_IR_length_values:
#         __test_bad_IR_length_tuple(('const', biv))
#
#     # empty list for choose
#     __test_bad_IR_length_tuple(('choose', []))
#
#     # bad consts in list for choose
#     for biv in bad_IR_length_values:
#         __test_bad_IR_length_tuple(('choose', [biv]))
#
#     # no other labels allowed
#     __test_bad_IR_length_tuple(('uniform', -1, 1))
#     __test_bad_IR_length_tuple(('normal', -1, 1))
#     __test_bad_IR_length_tuple(('truncnorm', -1, 1, 0 ,))
#
#     def __assert_correct_IR_length_tuple(IR_length_tuple):
#         try:
#             ambiscaper.reverb_ambisonics._validate_IR_length(IR_length_tuple)
#         except AmbiScaperError:
#             raise AmbiScaperError
#
#     __assert_correct_IR_length_tuple(('const',1024))
#     __assert_correct_IR_length_tuple(('choose',[256,512,1024]))
#
#
# def test_validate_room_dimensions():
#
#     def __test_bad_room_dimensions_tuple(room_dimensions_tuple):
#         pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_room_dimensions, room_dimensions_tuple)
#
#     # bad consts
#     bad_room_dimensions_values = [None,-1,1j,'yes',[],[5],[1,2,3,4],[1,2,'3']]
#
#     for brv in bad_room_dimensions_values:
#         __test_bad_room_dimensions_tuple(('const', brv))
#
#     # empty list for choose
#     __test_bad_room_dimensions_tuple(('choose', []))
#
#     # bad consts in list for choose
#     for brv in bad_room_dimensions_values:
#         __test_bad_room_dimensions_tuple(('choose', [brv]))
#
#     # uniform can't have negative min value
#     __test_bad_room_dimensions_tuple(('uniform', -1, 1))
#
#     # using normal will issue a warning since it can generate neg values
#     pytest.warns(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_room_dimensions, ('normal', 5, 2))
#
#     # truncnorm can't have negative min value
#     __test_bad_room_dimensions_tuple(('truncnorm', 0, 1, -1, 1))
#
#     def __assert_correct_room_dimensions(room_dimensions_tuple):
#         try:
#             ambiscaper.reverb_ambisonics._validate_room_dimensions(room_dimensions_tuple)
#         except AmbiScaperError:
#             raise AmbiScaperError
#
#     __assert_correct_room_dimensions(('const',[1,2,3]))
#     __assert_correct_room_dimensions(('choose',[[1,2,3],[2,3,4],[4,5,6]]))
#     __assert_correct_room_dimensions(('uniform',1,5))
#     __assert_correct_room_dimensions(('truncnorm', 0, 1, 1, 3))
#
#
# def test_validate_t60():
#
#     def __test_bad_t60_tuple(t60_tuple):
#         pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_t60, t60_tuple)
#
#     # bad consts
#     bad_t60_values = [None,-1,1j,2,'yes',[],[5],[1,2,3,4,5,'6']]
#     for bbv in bad_t60_values:
#         __test_bad_t60_tuple(('const', bbv))
#
#     # empty list for choose
#     __test_bad_t60_tuple(('choose', []))
#
#     # bad consts in list for choose
#     for bbv in bad_t60_values:
#         __test_bad_t60_tuple(('choose', [bbv]))
#
#     # uniform can't have negative min value
#     __test_bad_t60_tuple(('uniform', -1, 1))
#
#     # using normal will issue a warning since it can generate neg values
#     pytest.warns(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_t60, ('normal', 5, 2))
#
#     # truncnorm can't have negative min value
#     __test_bad_t60_tuple(('truncnorm', 0, 1, -1, 1))
#
#     def __assert_correct_t60(t60):
#         try:
#             ambiscaper.reverb_ambisonics._validate_t60(t60)
#         except AmbiScaperError:
#             raise AmbiScaperError
#
#     __assert_correct_t60(('const',0.3))
#     # __assert_correct_t60(('const',[0.1,0.2,0.3,0.4,0.5,0.6]))
#     __assert_correct_t60(('choose',[0.1,0.5,3.0]))
#     __assert_correct_t60(('uniform',1,5))
#     __assert_correct_t60(('truncnorm', 0, 1, 1, 3))
#
#
# def test_validate_wall_reflectivity():
#
#     def __test_bad_wall_reflectivity_tuple(wall_reflectivity_tuple):
#         pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_wall_reflectivity, wall_reflectivity_tuple)
#
#     # bad consts
#     bad_room_dimensions_values = [None,-1,1j,'yes',[],[5],[1,2,3,4],[1,2,'3',4,5,6]]
#
#     for brv in bad_room_dimensions_values:
#         __test_bad_wall_reflectivity_tuple(('const', brv))
#
#     # empty list for choose
#     __test_bad_wall_reflectivity_tuple(('choose', []))
#
#     # bad consts in list for choose
#     for brv in bad_room_dimensions_values:
#         __test_bad_wall_reflectivity_tuple(('choose', [brv]))
#
#     # uniform must be in the range [0,1]
#     __test_bad_wall_reflectivity_tuple(('uniform', -1, 1))
#     __test_bad_wall_reflectivity_tuple(('uniform', 0, 3))
#
#     # using normal will issue a warning since it can generate values outside the range [0,1]
#     pytest.warns(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_wall_reflectivity, ('normal', 5, 2))
#
#     # truncnorm must be in the range [0,1]
#     __test_bad_wall_reflectivity_tuple(('truncnorm', 0, 1, -1, 1))
#     __test_bad_wall_reflectivity_tuple(('truncnorm', 0, 1, 0.3, 2))
#
#     def __assert_correct_wall_reflectivity(wall_reflectivity_tuple):
#         try:
#             ambiscaper.reverb_ambisonics._validate_wall_reflectivity(wall_reflectivity_tuple)
#         except AmbiScaperError:
#             raise AmbiScaperError
#
#     __assert_correct_wall_reflectivity(('const',[float(r)/10 for r in range(1,7)]))
#     __assert_correct_wall_reflectivity(('choose',
#                                         [[float(r)/10 for r in range(1,7)],
#                                         [float(r)/10 for r in range(2,8)],
#                                         [float(r)/10 for r in range(3,9)]]))
#     __assert_correct_wall_reflectivity(('uniform',0,1))
#     __assert_correct_wall_reflectivity(('truncnorm', 0, 1, 0,1))
#
#
# def test_validate_source_type():
#
#     # Defined in reverb_ambisonics
#     # SMIR_ALLOWED_SOURCE_TYPES = ['o', 'c', 's', 'h', 'b']
#
#     # source_type must be defined in SMIR_ALLOWED_SOURCE_TYPES
#     pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_source_type, ('const', 'X'))
#
#     # Choose list must be subset of SMIR_ALLOWED_SOURCE_TYPES
#     pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_source_type, ('choose', ['X']))
#
#     # Source type tuple must start with either 'const' or 'choose'
#     bad_source_type_dists = [('uniform', 0, 1), ('normal', 0, 1),
#                              ('truncnorm', 0, 1, 0, 1)]
#     for bsd in bad_source_type_dists:
#         pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_source_type, bsd)
#
#     # Correct values
#     try:
#         ambiscaper.reverb_ambisonics._validate_source_type(('const','s'))
#         ambiscaper.reverb_ambisonics._validate_source_type(('choose',['s','c']))
#     except AmbiScaperError:
#         raise AmbiScaperError
#
#
# def test_validate_microphone_type():
#
#     # Defined in reverb_ambisonics
#     # SMIR_SUPPORTED_VIRTUAL_MICS.keys() = ["soundfield","tetramic","em32"]
#
#     # source_type must be defined in SMIR_SUPPORTED_VIRTUAL_MICS.keys()
#     pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_microphone_type, ('const', 'X'))
#
#     # Choose list must be subset of SMIR_SUPPORTED_VIRTUAL_MICS.keys()
#     pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_microphone_type, ('choose', ['X']))
#
#     # Microphone type tuple must start with either 'const' or 'choose'
#     bad_microphone_type_dists = [('uniform', 0, 1), ('normal', 0, 1),
#                                  ('truncnorm', 0, 1, 0, 1)]
#     for bmd in bad_microphone_type_dists:
#         pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_microphone_type, bmd)
#
#     # Correct values
#     try:
#         ambiscaper.reverb_ambisonics._validate_microphone_type(('const',"em32"))
#         ambiscaper.reverb_ambisonics._validate_microphone_type(('choose',["soundfield","tetramic"]))
#     except AmbiScaperError:
#         raise AmbiScaperError




#################### SOFA-RECORDED



def test_validate_SOFA_reverb_spec():

    sofa_path = os.path.abspath('./SOFA')
    sofa_reverb = SOFAReverb()
    sofa_reverb.set_sofa_reverb_folder_path(sofa_path)

    # bad name
    pytest.raises(AmbiScaperError, sofa_reverb._validate_reverb_spec, *[('const', 'fakeReverb'), ('const', 'wrap_azimuth')])
    # bad wrap
    pytest.raises(AmbiScaperError, sofa_reverb._validate_reverb_spec, *[('const', 'testpysofa.sofa'), ('const', 'fakeWrap')])
    # correct values
    try:
        sofa_reverb._validate_reverb_spec(('const', 'testpysofa.sofa'), ('const', 'wrap_azimuth'))
    except AmbiScaperError:
        raise AmbiScaperError


def test_validate_SOFA_reverb_wrap():

    def __test_bad_tuple(tuple):
        pytest.raises(AmbiScaperError, SOFAReverb()._validate_reverb_wrap, tuple)

    # bad types
    bad_values = [None, -1, 1j]
    for bv in bad_values:
        __test_bad_tuple(('const', bv))

    # Incorrect name
    __test_bad_tuple(('const', 'wrap_fake'))
    # Not valid distribution
    __test_bad_tuple(('choose', 'wrap_azimuth'))
    # Bad choose list
    __test_bad_tuple(('choose', ['wrap_azimuth',123]))
    __test_bad_tuple(('choose', ['wrap_azimuth','wrap_fake']))

    # no other labels allowed
    __test_bad_tuple(('uniform', -1, 1))
    __test_bad_tuple(('normal', -1, 1))
    __test_bad_tuple(('truncnorm', -1, 1, 0,))


    def __assert_correct_tuple(tuple):
        try:
            SOFAReverb()._validate_reverb_wrap(tuple)
        except AmbiScaperError:
            raise AmbiScaperError

    __assert_correct_tuple(('const', 'wrap_elevation'))
    __assert_correct_tuple(('choose', ['wrap_azimuth', 'random']))
    __assert_correct_tuple(('choose', []))


def test_validate_SOFA_reverb_name():

    def __test_bad_tuple(tuple):
        sofa_path = os.path.abspath('./SOFA')
        sofa_reverb = SOFAReverb()
        sofa_reverb.set_sofa_reverb_folder_path(sofa_path)
        pytest.raises(AmbiScaperError, sofa_reverb._validate_reverb_name, tuple)

    # bad types
    bad_values = [None, -1, 1j]
    for bv in bad_values:
        __test_bad_tuple(('const', bv))

    # Incorrect name
    __test_bad_tuple(('const', 'CoolReverb'))
    # Not valid distribution
    __test_bad_tuple(('choose', 'testpysofa.sofa'))
    # Bad choose list
    __test_bad_tuple(('choose', ['testpysofa.sofa', 123]))

    # bad consts in list for choose
    for bv in bad_values:
        __test_bad_tuple(('choose', [bv]))

    # no other labels allowed
    __test_bad_tuple(('uniform', -1, 1))
    __test_bad_tuple(('normal', -1, 1))
    __test_bad_tuple(('truncnorm', -1, 1, 0 ,))

    def __assert_correct_tuple(tuple):
        sofa_path = os.path.abspath('./SOFA')
        sofa_reverb = SOFAReverb()
        sofa_reverb.set_sofa_reverb_folder_path(sofa_path)
        try:
            sofa_reverb._validate_reverb_name(tuple)
        except AmbiScaperError:
            raise AmbiScaperError

    __assert_correct_tuple(('const','testpysofa.sofa'))
    __assert_correct_tuple(('choose',['testpysofa.sofa','testpysofa.sofa']))
    __assert_correct_tuple(('choose',[]))

def test_get_maximum_ambisonics_order_from_spec():

    def __test_not_valid(arg):
        sofa_path = os.path.abspath('./SOFA')
        sofa_reverb = SOFAReverb()
        sofa_reverb.set_sofa_reverb_folder_path(sofa_path)
        pytest.raises(AmbiScaperError, sofa_reverb.get_maximum_ambisonics_order_from_spec, arg)

    # spec
    not_valid_values = [
        [SOFAReverbSpec(name='incorrectfile.sofa', wrap='azimuth')],
        # ['reverb_spec',1],
    ]
    for not_valid_value in not_valid_values:
        __test_not_valid(*not_valid_value)

    def __test_incorrect_values(arg,groundtruth):
        sofa_path = os.path.abspath('./SOFA')
        sofa_reverb = SOFAReverb()
        sofa_reverb.set_sofa_reverb_folder_path(sofa_path)
        assert groundtruth != sofa_reverb.get_maximum_ambisonics_order_from_spec(arg)

    # [spec, groundtruth]
    incorrect_values = [
        [SOFAReverbSpec(name='testpysofa.sofa',wrap='azimuth'),2],
        # [SmirReverbSpec(IRlength=1024,
        #                 room_dimensions=[1.0, 1.0, 1.0],
        #                 t60=0.5,
        #                 reflectivity=None,
        #                 source_type='o',
        #                 microphone_type='soundfield'), 2],
    ]
    for iv in incorrect_values:
        __test_incorrect_values(*iv)


    def __test_correct_values(arg,groundtruth):
        sofa_path = os.path.abspath('./SOFA')
        sofa_reverb = SOFAReverb()
        sofa_reverb.set_sofa_reverb_folder_path(sofa_path)
        assert groundtruth == sofa_reverb.get_maximum_ambisonics_order_from_spec(arg)

    # [spec, groundtruth]
    correct_values = [
        [SOFAReverbSpec(name='testpysofa.sofa',wrap='azimuth'),1],
        # [SmirReverbSpec(IRlength=1024,
        #                 room_dimensions=[1.0, 1.0, 1.0],
        #                 t60=0.5,
        #                 reflectivity=None,
        #                 source_type='o',
        #                 microphone_type='soundfield'), 1],
    ]
    for cv in correct_values:
        __test_correct_values(*cv)


def test_retrieve_available_sofa_reverb_files():

    # Error if path not specified
    sofa_reverb = SOFAReverb()
    pytest.raises(AmbiScaperError,sofa_reverb.retrieve_available_sofa_reverb_files)

    sofa_path = os.path.abspath('./SOFA')
    sofa_reverb.set_sofa_reverb_folder_path(sofa_path)

    # At the moment we have only one
    groundtruth = ['testpysofa.sofa']

    # Check with unordered lists
    assert set(sofa_reverb.retrieve_available_sofa_reverb_files()) == set(groundtruth)


def test_generate_sofa_file_full_path():

    # SOFA path not specified
    sofa_reverb = SOFAReverb()
    pytest.raises(AmbiScaperError, sofa_reverb.generate_sofa_file_full_path, 'testpysofa.sofa')

    # Not valid arg
    sofa_path = os.path.abspath('./SOFA')
    sofa_reverb.set_sofa_reverb_folder_path(sofa_path)

    pytest.raises(AmbiScaperError,sofa_reverb.generate_sofa_file_full_path,123)
    pytest.raises(AmbiScaperError,sofa_reverb.generate_sofa_file_full_path,'FakeReverb')

    # test valid
    rootpath =  os.path.abspath('./SOFA')
    path = os.path.join(rootpath,'testpysofa.sofa')
    assert path == sofa_reverb.generate_sofa_file_full_path('testpysofa.sofa')


def test_get_sofa_reverb_folder_path():

    # Path not defined
    sofa_reverb = SOFAReverb()
    assert sofa_reverb.get_sofa_reverb_folder_path() == None

    # Test correct
    sofa_path = os.path.abspath('./SOFA')
    sofa_reverb.set_sofa_reverb_folder_path(sofa_path)
    assert sofa_reverb.get_sofa_reverb_folder_path() == sofa_path


def test_set_sofa_reverb_folder_path():

    # Path does not exist
    sofa_path = os.path.abspath('./fake_path')
    sofa_reverb = SOFAReverb()
    pytest.raises(AmbiScaperError, sofa_reverb.set_sofa_reverb_folder_path, sofa_path)

    # Path not a folder
    sofa_path = os.path.abspath('./SOFA/testpysofa.sofa')
    pytest.raises(AmbiScaperError, sofa_reverb.set_sofa_reverb_folder_path, sofa_path)

    # Test correct
    sofa_path = os.path.abspath('./SOFA')
    sofa_reverb.set_sofa_reverb_folder_path(sofa_path)
    assert sofa_reverb.get_sofa_reverb_folder_path() == sofa_path

# def test_get_receiver_position():
#
#     # Incorrect args
#     pytest.raises(AmbiScaperError, get_receiver_position, 3)
#     pytest.raises(AmbiScaperError, get_receiver_position, [4,5,6,7])
#
#     # Correct args
#     assert(get_receiver_position([2,4,6]) == [1,2,3])


def test_get_relative_speaker_positions_spherical():

    # Path does not exist
    sofa_reverb_name = 'fake_reverb.sofa'
    sofa_reverb = SOFAReverb()
    pytest.raises(AmbiScaperError, sofa_reverb.get_relative_speaker_positions_spherical, sofa_reverb_name)

    # In testpysofa.sofa there is only one emitter, located at [1,0,0] cartesian
    # EmitterPosition has dimensions (E,C,I)

    sofa_path = os.path.abspath('./SOFA')
    # sofa_path = os.path.abspath('/Volumes/Dinge/SOFA/pinakothek/')

    sofa_reverb.set_sofa_reverb_folder_path(sofa_path)

    sofa_reverb_name = 'testpysofa.sofa'
    # sofa_reverb_name = 'room7_eigenmike.sofa'
    # 8 speakers distributed in azimuth, elevation 8, distance 1
    # Since Listener view is +90, everything will be shifted...
    groundtruth = [
        [-np.pi/2., 0., 1.],
        [-np.pi/4, 0., 1.],
        [0., 0., 1.],
        [np.pi/4., 0., 1.],
        [np.pi/2, 0., 1.],
        [-5*np.pi/4, 0., 1.],
        [-1*np.pi, 0., 1.],
        [-3*np.pi/4, 0., 1.]
    ]

    assert np.allclose(groundtruth, sofa_reverb.get_relative_speaker_positions_spherical(sofa_reverb_name))