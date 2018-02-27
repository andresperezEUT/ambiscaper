import pytest

import ambiscaper
from ambiscaper.ambiscaper_exceptions import AmbiScaperError
from ambiscaper.ambiscaper_warnings import AmbiScaperWarning
from ambiscaper.reverb_ambisonics import _validate_IR_length, RecordedReverbSpec, SmirReverbSpec, \
    get_max_ambi_order_from_reverb_config, retrieve_available_recorded_IRs, generate_RIR_path


#################### SMIR

def test_validate_smir_reverb_spec():

    def __test_bad_smir_reverb_spec(smir_reverb_spec):
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_smir_reverb_spec, *smir_reverb_spec)

    def __test_warn_smir_reverb_spec(smir_reverb_spec):
        pytest.raises(AmbiScaperWarning, ambiscaper.reverb_ambisonics._validate_smir_reverb_spec, *smir_reverb_spec)

    def __test_good_smir_reverb_spec(smir_reverb_spec):
        try:
            ambiscaper.reverb_ambisonics._validate_smir_reverb_spec(*smir_reverb_spec)
        except AmbiScaperError:
            raise

    IRlengt = ('const',1024)
    room_dimensions = ('const',[1,2,3])
    source_type = ('const','o')
    microphone_type = ('const','soundfield')

    # Incorrect specs: no t60/reflectivity
    t60 = None
    reflectivity = None
    spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
    __test_bad_smir_reverb_spec(spec)

    # Incorrect specs: both t60/reflectivity
    t60 = ('const',0.5)
    reflectivity = ('const',[0.1,0.2,0.3,0.4,0.5,0.6])
    spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
    __test_warn_smir_reverb_spec(spec)

    # Correct entries
    t60 = ('const',0.5)
    reflectivity = None
    spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
    __test_good_smir_reverb_spec(spec)

    t60 = None
    reflectivity = ('const',[0.1,0.2,0.3,0.4,0.5,0.6])
    spec = [IRlengt,room_dimensions,t60,reflectivity,source_type,microphone_type]
    __test_good_smir_reverb_spec(spec)



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




#################### RECORDED

def test_validate_recorded_reverb_name():

    def __test_bad_tuple(tuple):
        pytest.raises(AmbiScaperError, ambiscaper.reverb_ambisonics._validate_recorded_reverb_name, tuple)

    # bad consts
    bad_values = [None, -1, 1j, 'yes', 'CoolReverb']

    for bv in bad_values:
        __test_bad_tuple(('const', bv))

    # empty list for choose
    __test_bad_tuple(('choose', []))
    __test_bad_tuple(('choose', 'CoolReverb'))

    # bad consts in list for choose
    for bv in bad_values:
        __test_bad_tuple(('choose', [bv]))

    # no other labels allowed
    __test_bad_tuple(('uniform', -1, 1))
    __test_bad_tuple(('normal', -1, 1))
    __test_bad_tuple(('truncnorm', -1, 1, 0 ,))

    def __assert_correct_tuple(tuple):
        try:
            ambiscaper.reverb_ambisonics._validate_recorded_reverb_name(tuple)
        except AmbiScaperError:
            raise AmbiScaperError

    __assert_correct_tuple(('const','MainChurch'))
    __assert_correct_tuple(('choose',['Vislab','OldChurch']))

def test_get_max_ambi_order_from_reverb_config():

    def __test_not_valid(arg):
        pytest.raises(AmbiScaperError, get_max_ambi_order_from_reverb_config, arg)

    # spec
    not_valid_values = [
        ['reverb_spec',1],
    ]
    for not_valid_value in not_valid_values:
        __test_not_valid(not_valid_value)

    def __test_incorrect_values(arg,groundtruth):
        assert groundtruth != get_max_ambi_order_from_reverb_config(arg)

    # [spec, groundtruth]
    incorrect_values = [
        [RecordedReverbSpec(name='OldChurch'),2],
        [SmirReverbSpec(IRlength=1024,
                        room_dimensions=[1.0, 1.0, 1.0],
                        t60=0.5,
                        reflectivity=None,
                        source_type='o',
                        microphone_type='soundfield'), 2],
    ]
    for iv in incorrect_values:
        __test_incorrect_values(*iv)


    def __test_correct_values(arg,groundtruth):
        assert groundtruth == get_max_ambi_order_from_reverb_config(arg)

    # [spec, groundtruth]
    correct_values = [
        [RecordedReverbSpec(name='OldChurch'),1],
        [SmirReverbSpec(IRlength=1024,
                        room_dimensions=[1.0, 1.0, 1.0],
                        t60=0.5,
                        reflectivity=None,
                        source_type='o',
                        microphone_type='soundfield'), 1],
    ]
    for cv in correct_values:
        __test_correct_values(*cv)


def test_retrieve_available_recorded_IRs():

    # At this moment we have these
    groundtruth = ['AudioBooth','MainChurch','OldChurch','Studio1','Vislab']

    # Check with unordered lists
    assert set(retrieve_available_recorded_IRs()) == set(groundtruth)

def test_generate_RIR_path():

    # Not valid arg
    pytest.raises(AmbiScaperError,generate_RIR_path,'FakeReverb')
    pytest.raises(AmbiScaperError,generate_RIR_path,123)

    # test valid
    # Hardcoded path
    path = "/Users/andres.perez/source/ambiscaper/IRs/AudioBooth/Soundfield"
    assert path == generate_RIR_path('AudioBooth')