# CREATED: 10/15/16 7:52 PM by Justin Salamon <justin.salamon@nyu.edu>

'''
Tests for functions in util.py
'''

from ambiscaper.util import _close_temp_files, wrap_number, delta_kronecker, cartesian_to_spherical, \
    spherical_to_cartesian, find_element_in_list, event_background_id_string, event_foreground_id_string, \
    _generate_event_id_from_idx, _get_event_idx_from_id, _validate_distribution, find_closest_spherical_point
from ambiscaper.util import _set_temp_logging_level
from ambiscaper.util import _validate_folder_path
from ambiscaper.util import _get_sorted_files
from ambiscaper.util import _trunc_norm
from ambiscaper.util import max_polyphony
from ambiscaper.util import polyphony_gini
from ambiscaper.util import is_real_number, is_real_array
from ambiscaper.ambiscaper_exceptions import AmbiScaperError
import tempfile
import os
import logging
import pytest
import shutil
import numpy as np
from scipy.stats import truncnorm
import jams
from ambiscaper.core import EventSpec
from ambiscaper import AmbiScaper


# FIXTURES
BG_PATH = 'samples/Acoustics_Book'
FG_PATH = 'samples/Acoustics_Book'

FG_PATH_FILES = ([
    os.path.join(FG_PATH, 'adult_female_speech.wav'),
    os.path.join(FG_PATH, 'bagpipe_music.wav'),
    os.path.join(FG_PATH, 'bagpipe_steady_chord.wav'),
    os.path.join(FG_PATH, 'flute_arpeggio.wav'),
    os.path.join(FG_PATH, 'flute_music.wav'),
    os.path.join(FG_PATH, 'tuba_arpeggio.wav'),
    os.path.join(FG_PATH, 'tuba_music.wav'),
])
# FLUTE_FILE = os.path.join(FG_PATH, 'flute_arpeggio.wav')
FLUTE_FILE = 'flute_arpeggio.wav'


def test_close_temp_files():
    '''
    Create a bunch of temp files and then make sure they've been closed and
    deleted.

    '''
    # With delete=True
    tmpfiles = []
    with _close_temp_files(tmpfiles):
        for _ in range(5):
            tmpfiles.append(
                tempfile.NamedTemporaryFile(suffix='.wav', delete=True))

    for tf in tmpfiles:
        assert tf.file.closed
        assert not os.path.isfile(tf.name)

    # With delete=False
    tmpfiles = []
    with _close_temp_files(tmpfiles):
        for _ in range(5):
            tmpfiles.append(
                tempfile.NamedTemporaryFile(suffix='.wav', delete=False))

    for tf in tmpfiles:
        assert tf.file.closed
        assert not os.path.isfile(tf.name)


def test_set_temp_logging_level():
    '''
    Ensure temp logging level is set as expected

    '''
    logger = logging.getLogger()
    logger.setLevel('DEBUG')
    with _set_temp_logging_level('CRITICAL'):
        assert logging.getLevelName(logger.level) == 'CRITICAL'
    assert logging.getLevelName(logger.level) == 'DEBUG'


def test_get_sorted_files():
    '''
    Ensure files are returned in expected order.

    '''
    assert _get_sorted_files(FG_PATH) == FG_PATH_FILES


def test_validate_folder_path():
    '''
    Make sure invalid folder paths are caught

    '''
    # bad folder path
    pytest.raises(AmbiScaperError, _validate_folder_path,
                  '/path/to/invalid/folder/')

    # good folder path should raise no error
    # make temp folder
    tmpdir = tempfile.mkdtemp()
    # validate
    _validate_folder_path(tmpdir)
    # remove it
    shutil.rmtree(tmpdir)



def test_trunc_norm():
    '''
    Should return values from a truncated normal distribution.

    '''
    # sample values from a distribution
    mu, sigma, trunc_min, trunc_max = 2, 1, 0, 5
    x = [_trunc_norm(mu, sigma, trunc_min, trunc_max) for _ in range(100000)]
    x = np.asarray(x)

    # simple check: values must be within truncated bounds
    assert (x >= trunc_min).all() and (x <= trunc_max).all()

    # trickier check: values must approximate distribution's PDF
    hist, bins = np.histogram(x, bins=np.arange(0, 10.1, 0.2), normed=True)
    xticks = bins[:-1] + 0.1
    a, b = (trunc_min - mu) / float(sigma), (trunc_max - mu) / float(sigma)
    trunc_closed = truncnorm.pdf(xticks, a, b, mu, sigma)
    assert np.allclose(hist, trunc_closed, atol=0.015)


def test_max_polyphony():
    '''
    Test the computation of polyphony of a ambiscaper soundscape instantiation.

    '''
    def __create_annotation_with_overlapping_events(n_events):

        ann = jams.Annotation(namespace='ambiscaper_sound_event')
        ann.duration = n_events / 2. + 10

        for ind in range(n_events):
            instantiated_event = EventSpec(source_file='/the/source/file.wav',
                                           event_id='fg0',
                                           source_time=0,
                                           event_time=ind / 2.,
                                           event_duration=10,
                                           event_azimuth=0.,
                                           event_elevation=0.,
                                           event_spread=0.,
                                           snr=0,
                                           role='foreground',
                                           pitch_shift=None,
                                           time_stretch=None)

            ann.append(time=ind / 2.,
                       duration=10,
                       value=instantiated_event._asdict(),
                       confidence=1.0)

        return ann

    def __create_annotation_without_overlapping_events(n_events):

        ann = jams.Annotation(namespace='ambiscaper_sound_event')
        ann.duration = n_events * 10

        for ind in range(n_events):
            instantiated_event = EventSpec(source_file='/the/source/file.wav',
                                           event_id='fg0',
                                           source_time=0,
                                           event_time=ind * 10,
                                           event_duration=5,
                                           event_azimuth=0.,
                                           event_elevation=0.,
                                           event_spread=0.,
                                           snr=0,
                                           role='foreground',
                                           pitch_shift=None,
                                           time_stretch=None)

            ann.append(time=ind * 10,
                       duration=5,
                       value=instantiated_event._asdict(),
                       confidence=1.0)

        return ann

    # 0 through 10 overlapping events
    for poly in range(11):
        ann = __create_annotation_with_overlapping_events(poly)
        est_poly = max_polyphony(ann)
        assert est_poly == poly

    # 1 through 10 NON-overlapping events
    for n_events in range(1, 11):
        ann = __create_annotation_without_overlapping_events(n_events)
        est_poly = max_polyphony(ann)
        assert est_poly == 1


def test_polyphony_gini():
    '''
    Test computation of polyphony gini
    '''

    # Annotation must have namespace sound_event, otherwise raise error
    ann = jams.Annotation('tag_open', duration=10)
    gini = pytest.raises(AmbiScaperError, polyphony_gini, ann)

    # Annotation without duration set should raise error
    ann = jams.Annotation('ambiscaper_sound_event', duration=None)
    gini = pytest.raises(AmbiScaperError, polyphony_gini, ann)

    # Annotation with no foreground events returns a gini of 0
    ambiscaper = AmbiScaper(duration=10.0,
                            ambisonics_order=3,
                            fg_path=FG_PATH,
                            bg_path=BG_PATH)

    # add background
    ambiscaper.add_background(source_file=('const', 'flute_arpeggio.wav'),
                              source_time=('const', 0))
    jam = ambiscaper._instantiate()
    ann = jam.annotations[0]
    gini = polyphony_gini(ann)
    assert gini == 0

    def __test_gini_from_event_times(event_time_list, expected_gini,
                                     hop_size=0.01):

        print(event_time_list)

        # create ambiscaper
        ambiscaper = AmbiScaper(duration=10.0,
                                ambisonics_order=3,
                                fg_path=FG_PATH,
                                bg_path=BG_PATH)

        # add background
        ambiscaper.add_background(source_file=('choose', []),
                                  source_time=('const', 0))
        # add foreground events based on the event time list
        # always use siren file since it is 26 s long, so we can choose the
        # event duration flexibly
        for onset, offset in event_time_list:

            ambiscaper.add_event(source_file=('const', FLUTE_FILE),
                                 source_time=('const', 0),
                                 event_time=('const', onset),
                                 event_duration=('const', offset - onset),
                                 event_azimuth=('const', 0),
                                 event_elevation=('const', 0),
                                 event_spread=('const', 0),
                                 snr=('uniform', 6, 30),
                                 pitch_shift=('uniform', -3, 3),
                                 time_stretch=None)

        jam = ambiscaper._instantiate()
        ann = jam.annotations[0]
        gini = polyphony_gini(ann, hop_size=hop_size)
        print(gini, expected_gini)
        assert np.allclose([gini], [expected_gini], atol=1e-5)

    event_time_lists = ([
        [],
        [(0, 1)],
        [(0, 5), (5, 10)],
        [(0, 10), (3, 7), (4, 6)]
    ])

    expected_ginis = [0, 0.1, 0.5, 0.2]

    for etl, g in zip(event_time_lists, expected_ginis):
        __test_gini_from_event_times(etl, g, hop_size=0.01)

    for etl, g in zip(event_time_lists, expected_ginis):
        __test_gini_from_event_times(etl, g, hop_size=1.0)


def test_is_real_number():

    non_reals = [None, 1j, 'yes']
    yes_reals = [-1e12, -1, -1.0, 0, 1, 1.0, 1e12]

    # test single value
    for nr in non_reals:
        assert not is_real_number(nr)
    for yr in yes_reals:
        assert is_real_number(yr)


def test_is_real_array():

    non_reals = [None, 1j, 'yes']
    yes_reals = [-1e12, -1, -1.0, 0, 1, 1.0, 1e12]

    # non-list non-array types must return false
    for x in non_reals + yes_reals:
        assert not is_real_array(x)

    # test array
    for nr in non_reals:
        assert not is_real_array([nr])
    for yr in yes_reals:
        assert is_real_array([yr])


def test_wrap_number():

    # test incorrect values
    def __test_bad_wrap_number(bad_entry):
        pytest.raises(AmbiScaperError, wrap_number, *bad_entry)

    bad_entries = [
        ['1',1j,3], # not a number
        [1,3,2]    # min > max
    ]
    for bad_entry in bad_entries:
        __test_bad_wrap_number(bad_entry)

    # test correct values
    def __test_correct_wrap_number(x, min, max, groundtruth):
        assert(np.isclose([groundtruth],[wrap_number(x, min, max)] ))

    correct_entries = [
        # x, min, max, groundtruth
        [0, 0, 2, 0 ],
        [1, 0, 2, 1 ],
        [2, 0, 2, 0 ],
        [2.5, 0, 2, 0.5 ],
        [-1, 0, 2, 1 ],
        [-np.pi, 0, 2*np.pi, np.pi ],
    ]
    for correct_entry in correct_entries:
        __test_correct_wrap_number(*correct_entry)


def test_delta_kronecker():

    # test incorrect values
    def __test_bad_delta_number(bad_entry):
        pytest.raises(AmbiScaperError, delta_kronecker, bad_entry, bad_entry)

    bad_entries = [
        ['1',1.8,-2e-4,1j], # not a number
    ]
    for bad_entry in bad_entries:
        __test_bad_delta_number(bad_entry)

    #test correct values
    def __test_correct_delta_kronecker(q1, q2, groundtruth):
        assert (groundtruth == delta_kronecker(q1,q2))

    correct_entries = [
        # q1, q2, groundtruth
        [0,0,1],
        [0,1,0],
        [-2,-2,1],
        [0,-0,1]
    ]
    for correct_entry in correct_entries:
        __test_correct_delta_kronecker(*correct_entry)


def test_cartesian_to_spherical():

    # test incorrect values
    def __test_bad_cartesian_list(bad_entry):
        pytest.raises(AmbiScaperError, cartesian_to_spherical, bad_entry)
        
    bad_entries = [
        1,
        2j,
        'str',
        None,
        [],
        [1,2,3],    # not float
        [1.3, 4.5]
    ]
    for bad_entry in bad_entries:
        __test_bad_cartesian_list(bad_entry)

    # test correct values
    def __test_correct_cartesian_to_spherical(cartesian, groundtruth):
        assert np.allclose(groundtruth, cartesian_to_spherical(cartesian))

    correct_entries = [
        # cartesian, groundtruth
        [ [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
        [ [0.0, 1.0, 0.0], [np.pi/2, 0.0, 1.0]],
        [ [0.0, 0.0, 1.0], [0.0, np.pi/2, 1.0]],
    ]
    for correct_entry in correct_entries:
        __test_correct_cartesian_to_spherical(*correct_entry)


def test_spherical_to_cartesian():
    # test incorrect values
    def __test_bad_spherical_list(bad_entry):
        pytest.raises(AmbiScaperError, spherical_to_cartesian, bad_entry)

    bad_entries = [
        1,
        2j,
        'str',
        None,
        [],
        [1, 2, 3],  # not float
        [1.3, 4.5]
    ]
    for bad_entry in bad_entries:
        __test_bad_spherical_list(bad_entry)

    # test correct values
    def __test_correct_spherical_to_cartesian(spherical, groundtruth):
        assert np.allclose(groundtruth, spherical_to_cartesian(spherical))

    correct_entries = [
        # spherical, groundtruth
        [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], ],
        [[np.pi / 2, 0.0, 1.0], [0.0, 1.0, 0.0], ],
        [[0.0, np.pi / 2, 1.0], [0.0, 0.0, 1.0], ],
    ]
    for correct_entry in correct_entries:
        __test_correct_spherical_to_cartesian(*correct_entry)


def test_find_element_in_list():
    # test incorrect values
    # basically, second argument not a list

    def __test_bad_list(bad_entry):
        pytest.raises(AmbiScaperError, find_element_in_list, *bad_entry)

    bad_entries = [
        [1, 2],
        [1, None],
        [1, {}],
    ]
    for bad_entry in bad_entries:
        __test_bad_list(bad_entry)

    # test correct values
    def __test_correct_find_element_in_list(element, list, groundtruth):
        assert groundtruth == find_element_in_list(element,list)

    correct_entries = [
        # element, list, groundtruth
        [1, [1,2,3], 0 ],
        [3, [1,2,3], 2 ],
        [None, [None,None,None], 0 ],
        [None, [None,None,None], 0 ],
        [1, [2,3,4], None ],

    ]
    for correct_entry in correct_entries:
        __test_correct_find_element_in_list(*correct_entry)


def test_generate_event_id_from_idx():

    def __test_bad_args(bad_args):
        pytest.raises(AmbiScaperError, _generate_event_id_from_idx, *bad_args)

    bad_entries = [
        [1.0, 'foreground'],
        [None, 'foreground'],
        [-3, 'foreground'],
        [0, 'not_correct_label'],
    ]

    for bad_entry in bad_entries:
        __test_bad_args(bad_entry)

    def __test_correct_args(correct_args,groundtruth):
        assert groundtruth == _generate_event_id_from_idx(*correct_args)

    # idx, label, groundtruth
    correct_entries = [
        [[0,'foreground'],event_foreground_id_string+str(0)],
        [[1,'background'],event_background_id_string+str(1)],
    ]

    for correct_entry in correct_entries:
        __test_correct_args(correct_entry[0],correct_entry[1])


def test_generate_event_idx_from_id():

    def __test_bad_args(bad_args):
        pytest.raises(AmbiScaperError, _get_event_idx_from_id, *bad_args)

    bad_entries = [
        ['fg', 'foreground'],
        [None, 'foreground'],
        ['gg0', 'foreground'],
        ['fgZero', 'foreground'],
        ['fg0', 'not_correct_label'],
    ]

    for bad_entry in bad_entries:
        __test_bad_args(bad_entry)

    def __test_correct_args(correct_args,groundtruth):
        assert groundtruth == _get_event_idx_from_id(*correct_args)

    # idx, label, groundtruth
    correct_entries = [
        [['fg0','foreground'],0],
        [['bg1','background'],1],
    ]

    for correct_entry in correct_entries:
        __test_correct_args(correct_entry[0],correct_entry[1])


def test_validate_distribution():

    def __test_bad_tuple_list(tuple_list):
        for t in tuple_list:
            if isinstance(t, tuple):
                print(t, len(t))
            else:
                print(t)
            pytest.raises(AmbiScaperError, _validate_distribution, t)

    # not tuple = error
    nontuples = [[], 5, 'yes']
    __test_bad_tuple_list(nontuples)

    # tuple must be at least length 2
    shortuples = [tuple(), tuple(['const'])]
    __test_bad_tuple_list(shortuples)

    # unsupported distribution tuple name
    badnames = [('invalid', 1), ('constant', 1, 2, 3)]
    __test_bad_tuple_list(badnames)

    # supported dist tuples, but bad arugments
    badargs = [('const', 1, 2),
               ('choose', 1), ('choose', [], 1),
               ('uniform', 1), ('uniform', 1, 2, 3), ('uniform', 2, 1),
               ('uniform', 'one', 2), ('uniform', 1, 'two'),
               ('uniform', 0, 1j), ('uniform', 1j, 2),
               ('normal', 1),
               ('normal', 1, 2, 3), ('normal', 1, -1),
               ('normal', 0, 1j), ('normal', 1j, 1), ('normal', 'one', 2),
               ('normal', 1, 'two'),
               ('truncnorm', 1), ('truncnorm', 1, 2, 3),
               ('truncnorm', 1, -1, 0, 1),
               ('truncnorm', 0, 1j, 0, 1), ('truncnorm', 1j, 1, 0, 1),
               ('truncnorm', 'one', 2, 0, 1), ('truncnorm', 1, 'two', 0, 1),
               ('truncnorm', 1, 2, 'three', 5), ('truncnorm', 1, 2, 3, 'four'),
               ('truncnorm', 0, 2, 2, 0)]
    __test_bad_tuple_list(badargs)


def test_find_closest_spherical_point():

    # bad arguments
    badargs = [
        # first argument not list of len 2
        (0, [0, 0]),
        ([1, 2, 3], [0, 0]),
        # second argument not list of lists of len 2
        ([0, 0], 0),
        ([0, 0], [0, 0]),
        ([0, 0], [[0, 0], [1, 2, 3]]),
        # bad criterium string
        ([0,0],[[0,0],[1,1]],'fake_criterium')

    ]
    for ba in badargs:
        pytest.raises(AmbiScaperError, find_closest_spherical_point, *ba)

    # correct arguments

    point = [0,0]
    list_of_points = [ [0,0], [1,1], [2,2] ]
    assert( 0 == find_closest_spherical_point(point,list_of_points,criterium='azimuth'))

    point = [0.9,0]
    list_of_points = [ [0,0], [1,1], [2,2] ]
    assert( 1 == find_closest_spherical_point(point,list_of_points,criterium='azimuth'))

    point = [0,0]   # wrapping azimuth around 2pi
    list_of_points = [ [6,0], [1,1], [2,2] ]
    assert( 0 == find_closest_spherical_point(point,list_of_points,criterium='azimuth'))

    point = [0,1]   # wrapping azimuth around 2pi
    list_of_points = [ [0,0], [1,1], [2,2] ]
    assert( 1 == find_closest_spherical_point(point,list_of_points,criterium='elevation'))

    point = [1,1]   # wrapping azimuth around 2pi
    list_of_points = [ [0,0], [4,1] ]
    assert( 0 == find_closest_spherical_point(point,list_of_points,criterium='surface'))

