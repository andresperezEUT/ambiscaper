import pytest

import ambiscaper
from ambiscaper.ambiscaper_exceptions import AmbiScaperError
from ambiscaper.ambiscaper_warnings import AmbiScaperWarning
from ambiscaper.reverb_ambisonics import _validate_IR_length


def test_validate_IR_length():

    def __test_bad_IR_length_tuple(IR_length_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_IR_length, IR_length_tuple)

    # bad consts
    bad_IR_length_values = [None, -1, 1j, 'yes', [], [5]]
    for biv in bad_IR_length_values:
        __test_bad_IR_length_tuple(('const', biv))

    # empty list for choose
    __test_bad_IR_length_tuple(('choose', []))

    # bad consts in list for choose
    for biv in bad_IR_length_values:
        __test_bad_IR_length_tuple(('choose', [biv]))

    # no other labels allowed
    __test_bad_IR_length_tuple(('uniform', -1, 1))
    __test_bad_IR_length_tuple(('normal', -1, 1))
    __test_bad_IR_length_tuple(('truncnorm', -1, 1, 0 ,))

    def __assert_correct_IR_length_tuple(IR_length_tuple):
        try:
            ambiscaper.reverb_ambisonics._validate_IR_length(IR_length_tuple)
        except AmbiScaperError:
            raise AmbiScaperError

    __assert_correct_IR_length_tuple(('const',1024))
    __assert_correct_IR_length_tuple(('choose',[256,512,1024]))


def test_validate_room_dimensions():

    def __test_bad_room_dimensions_tuple(room_dimensions_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_room_dimensions, room_dimensions_tuple)

    # bad consts
    bad_room_dimensions_values = [None,-1,1j,'yes',[],[5],[1,2,3,4],[1,2,'3']]

    for brv in bad_room_dimensions_values:
        __test_bad_room_dimensions_tuple(('const', brv))

    # empty list for choose
    __test_bad_room_dimensions_tuple(('choose', []))

    # bad consts in list for choose
    for brv in bad_room_dimensions_values:
        __test_bad_room_dimensions_tuple(('choose', [brv]))

    # uniform can't have negative min value
    __test_bad_room_dimensions_tuple(('uniform', -1, 1))

    # using normal will issue a warning since it can generate neg values
    pytest.warns(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_room_dimensions, ('normal', 5, 2))

    # truncnorm can't have negative min value
    __test_bad_room_dimensions_tuple(('truncnorm', 0, 1, -1, 1))

    def __assert_correct_room_dimensions(room_dimensions_tuple):
        try:
            ambiscaper.reverb_ambisonics._validate_room_dimensions(room_dimensions_tuple)
        except AmbiScaperError:
            raise AmbiScaperError

    __assert_correct_room_dimensions(('const',[1,2,3]))
    __assert_correct_room_dimensions(('choose',[[1,2,3],[2,3,4],[4,5,6]]))
    __assert_correct_room_dimensions(('uniform',1,5))
    __assert_correct_room_dimensions(('truncnorm', 0, 1, 1, 3))


def test_validate_t60():

    def __test_bad_t60_tuple(t60_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_t60, t60_tuple)

    # bad consts
    bad_t60_values = [None,-1,1j,2,'yes',[],[5],[1,2,3,4,5,'6']]
    for bbv in bad_t60_values:
        __test_bad_t60_tuple(('const', bbv))

    # empty list for choose
    __test_bad_t60_tuple(('choose', []))

    # bad consts in list for choose
    for bbv in bad_t60_values:
        __test_bad_t60_tuple(('choose', [bbv]))

    # uniform can't have negative min value
    __test_bad_t60_tuple(('uniform', -1, 1))

    # using normal will issue a warning since it can generate neg values
    pytest.warns(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_t60, ('normal', 5, 2))

    # truncnorm can't have negative min value
    __test_bad_t60_tuple(('truncnorm', 0, 1, -1, 1))

    def __assert_correct_t60(t60):
        try:
            ambiscaper.reverb_ambisonics._validate_t60(t60)
        except AmbiScaperError:
            raise AmbiScaperError

    __assert_correct_t60(('const',0.3))
    # __assert_correct_t60(('const',[0.1,0.2,0.3,0.4,0.5,0.6]))
    __assert_correct_t60(('choose',[0.1,0.5,3.0]))
    __assert_correct_t60(('uniform',1,5))
    __assert_correct_t60(('truncnorm', 0, 1, 1, 3))


def test_validate_wall_reflectivity():

    def __test_bad_wall_reflectivity_tuple(wall_reflectivity_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_wall_reflectivity, wall_reflectivity_tuple)

    # bad consts
    bad_room_dimensions_values = [None,-1,1j,'yes',[],[5],[1,2,3,4],[1,2,'3',4,5,6]]

    for brv in bad_room_dimensions_values:
        __test_bad_wall_reflectivity_tuple(('const', brv))

    # empty list for choose
    __test_bad_wall_reflectivity_tuple(('choose', []))

    # bad consts in list for choose
    for brv in bad_room_dimensions_values:
        __test_bad_wall_reflectivity_tuple(('choose', [brv]))

    # uniform must be in the range [0,1]
    __test_bad_wall_reflectivity_tuple(('uniform', -1, 1))
    __test_bad_wall_reflectivity_tuple(('uniform', 0, 3))

    # using normal will issue a warning since it can generate values outside the range [0,1]
    pytest.warns(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_wall_reflectivity, ('normal', 5, 2))

    # truncnorm must be in the range [0,1]
    __test_bad_wall_reflectivity_tuple(('truncnorm', 0, 1, -1, 1))
    __test_bad_wall_reflectivity_tuple(('truncnorm', 0, 1, 0.3, 2))

    def __assert_correct_wall_reflectivity(wall_reflectivity_tuple):
        try:
            ambiscaper.reverb_ambisonics._validate_wall_reflectivity(wall_reflectivity_tuple)
        except AmbiScaperError:
            raise AmbiScaperError

    __assert_correct_wall_reflectivity(('const',[float(r)/10 for r in range(1,7)]))
    __assert_correct_wall_reflectivity(('choose',
                                        [[float(r)/10 for r in range(1,7)],
                                        [float(r)/10 for r in range(2,8)],
                                        [float(r)/10 for r in range(3,9)]]))
    __assert_correct_wall_reflectivity(('uniform',0,1))
    __assert_correct_wall_reflectivity(('truncnorm', 0, 1, 0,1))


def test_validate_source_type():

    # Defined in reverb_ambisonics
    # SMIR_ALLOWED_SOURCE_TYPES = ['o', 'c', 's', 'h', 'b']

    # source_type must be defined in SMIR_ALLOWED_SOURCE_TYPES
    pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_source_type, ('const', 'X'))

    # Choose list must be subset of SMIR_ALLOWED_SOURCE_TYPES
    pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_source_type, ('choose', ['X']))

    # Source type tuple must start with either 'const' or 'choose'
    bad_source_type_dists = [('uniform', 0, 1), ('normal', 0, 1),
                             ('truncnorm', 0, 1, 0, 1)]
    for bsd in bad_source_type_dists:
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_source_type, bsd)

    # Correct values
    try:
        ambiscaper.reverb_ambisonics._validate_source_type(('const','s'))
        ambiscaper.reverb_ambisonics._validate_source_type(('choose',['s','c']))
    except AmbiScaperError:
        raise AmbiScaperError


def test_validate_microphone_type():

    # Defined in reverb_ambisonics
    # SMIR_SUPPORTED_VIRTUAL_MICS.keys() = ["soundfield","tetramic","em32"]

    # source_type must be defined in SMIR_SUPPORTED_VIRTUAL_MICS.keys()
    pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_microphone_type, ('const', 'X'))

    # Choose list must be subset of SMIR_SUPPORTED_VIRTUAL_MICS.keys()
    pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_microphone_type, ('choose', ['X']))

    # Microphone type tuple must start with either 'const' or 'choose'
    bad_microphone_type_dists = [('uniform', 0, 1), ('normal', 0, 1),
                                 ('truncnorm', 0, 1, 0, 1)]
    for bmd in bad_microphone_type_dists:
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_microphone_type, bmd)

    # Correct values
    try:
        ambiscaper.reverb_ambisonics._validate_microphone_type(('const',"em32"))
        ambiscaper.reverb_ambisonics._validate_microphone_type(('choose',["soundfield","tetramic"]))
    except AmbiScaperError:
        raise AmbiScaperError


