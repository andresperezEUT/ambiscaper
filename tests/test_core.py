import shutil

import ambiscaper
from ambiscaper.ambiscaper_exceptions import AmbiScaperError
from ambiscaper.ambiscaper_warnings import AmbiScaperWarning
from ambiscaper.reverb_ambisonics import SOFAReverbSpec, SOFAReverb
from ambiscaper.util import _close_temp_files, _get_sorted_audio_files_recursive
import pytest
from ambiscaper.core import EventSpec
# import tempfile
from backports import tempfile
# import backports.tempfile
import os
import numpy as np
import soundfile
import jams
import pandas as pd
import warnings


# FIXTURES
# Paths to files for testing


FG_PATH = os.path.abspath('./samples')
BG_PATH = os.path.abspath('./samples')


ALT_FG_PATH = 'tests/data/audio_alt_path/foreground'
ALT_BG_PATH = 'tests/data/audio_alt_path/background'

REG_WAV_PATH = 'tests/data/soundscape_for_test/soundscape_for_test.wav'
REG_JAM_PATH = 'tests/data/soundscape_for_test/soundscape_for_test.jams'
REG_TXT_PATH = 'tests/data/soundscape_for_test/soundscape_for_test.txt'

# REG_BGONLY_WAV_PATH = 'tests/data/regression/bgonly_soundscape_20170928.wav'
# REG_BGONLY_JAM_PATH = 'tests/data/regression/bgonly_soundscape_20170928.jams'
# REG_BGONLY_TXT_PATH = 'tests/data/regression/bgonly_soundscape_20170928.txt'
#
# REG_REVERB_WAV_PATH = 'tests/data/regression/reverb_soundscape_20170928.wav'
# REG_REVERB_JAM_PATH = 'tests/data/regression/reverb_soundscape_20170928.jams'
# REG_REVERB_TXT_PATH = 'tests/data/regression/reverb_soundscape_20170928.txt'

# fg and bg labels for testing
FB_LABELS = ['car_horn', 'human_voice', 'siren']
BG_LABELS = ['park', 'restaurant', 'street']


# def test_generate_from_jams():
#
#     # Test for invalid jams: no annotations
#     tmpfiles = []
#     with _close_temp_files(tmpfiles):
#         jam = jams.JAMS()
#         jam.file_metadata.duration = 10
#
#         jam_file = tempfile.NamedTemporaryFile(suffix='.jams', delete=True)
#         gen_file = tempfile.NamedTemporaryFile(suffix='.jams', delete=True)
#
#         jam.save(jam_file.name)
#
#         pytest.raises(AmbiScaperError, ambiscaper.generate_from_jams, jam_file.name,
#                       gen_file.name)
#
#     # Test for valid jams files
#     tmpfiles = []
#     with _close_temp_files(tmpfiles):
#
#         # Create all necessary temp files
#         orig_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=True)
#         orig_jam_file = tempfile.NamedTemporaryFile(suffix='.jams', delete=True)
#
#         gen_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=True)
#         gen_jam_file = tempfile.NamedTemporaryFile(suffix='.jams', delete=True)
#
#         tmpfiles.append(orig_wav_file)
#         tmpfiles.append(orig_jam_file)
#         tmpfiles.append(gen_wav_file)
#         tmpfiles.append(gen_jam_file)
#
#         # --- Define ambiscaper --- *
#         sc = ambiscaper.AmbiScaper(10, 1, FG_PATH, BG_PATH)
#         sc.ref_db = -50
#         sc.add_background(source_file=('choose', []),
#                           source_time=('const', 0))
#         # Add 5 events
#         for _ in range(5):
#             sc.add_event(source_file=('choose', []),
#                          source_time=('const', 0),
#                          event_time=('uniform', 0, 9),
#                          event_duration=('choose', [1, 2, 3]),
#                          event_azimuth=('const', 0),
#                          event_elevation=('const', 0),
#                          event_spread=('const', 0),
#                          snr=('uniform', 10, 20),
#                          pitch_shift=('uniform', -1, 1),
#                          time_stretch=('uniform', 0.8, 1.2))
#
#         # generate, then generate from the jams and compare audio files
#         # repeat 5 time
#         for _ in range(5):
#             sc.generate(orig_wav_file.name, orig_jam_file.name,
#                         disable_instantiation_warnings=True)
#             ambiscaper.generate_from_jams(orig_jam_file.name, gen_wav_file.name)
#
#             # validate audio
#             orig_wav, sr = soundfile.read(orig_wav_file.name)
#             gen_wav, sr = soundfile.read(gen_wav_file.name)
#             assert np.allclose(gen_wav, orig_wav, atol=1e-8, rtol=1e-8)
#
#         # Now add in trimming!
#         for _ in range(5):
#             sc.generate(orig_wav_file.name, orig_jam_file.name,
#                         disable_instantiation_warnings=True)
#             ambiscaper.trim(orig_wav_file.name, orig_jam_file.name,
#                         orig_wav_file.name, orig_jam_file.name,
#                         np.random.uniform(0, 5), np.random.uniform(5, 10))
#             ambiscaper.generate_from_jams(orig_jam_file.name, gen_wav_file.name)
#
#             # validate audio
#             orig_wav, sr = soundfile.read(orig_wav_file.name)
#             gen_wav, sr = soundfile.read(gen_wav_file.name)
#             assert np.allclose(gen_wav, orig_wav, atol=1e-8, rtol=1e-8)
#
#         # Double trimming
#         for _ in range(2):
#             sc.generate(orig_wav_file.name, orig_jam_file.name,
#                         disable_instantiation_warnings=True)
#             ambiscaper.trim(orig_wav_file.name, orig_jam_file.name,
#                         orig_wav_file.name, orig_jam_file.name,
#                         np.random.uniform(0, 2), np.random.uniform(8, 10))
#             ambiscaper.trim(orig_wav_file.name, orig_jam_file.name,
#                         orig_wav_file.name, orig_jam_file.name,
#                         np.random.uniform(0, 2), np.random.uniform(4, 6))
#             ambiscaper.generate_from_jams(orig_jam_file.name, gen_wav_file.name)
#
#         # Tripple trimming
#         for _ in range(2):
#             sc.generate(orig_wav_file.name, orig_jam_file.name,
#                         disable_instantiation_warnings=True)
#             ambiscaper.trim(orig_wav_file.name, orig_jam_file.name,
#                         orig_wav_file.name, orig_jam_file.name,
#                         np.random.uniform(0, 2), np.random.uniform(8, 10))
#             ambiscaper.trim(orig_wav_file.name, orig_jam_file.name,
#                         orig_wav_file.name, orig_jam_file.name,
#                         np.random.uniform(0, 1), np.random.uniform(5, 6))
#             ambiscaper.trim(orig_wav_file.name, orig_jam_file.name,
#                         orig_wav_file.name, orig_jam_file.name,
#                         np.random.uniform(0, 1), np.random.uniform(3, 4))
#             ambiscaper.generate_from_jams(orig_jam_file.name, gen_wav_file.name)
#
#             # validate audio
#             orig_wav, sr = soundfile.read(orig_wav_file.name)
#             gen_wav, sr = soundfile.read(gen_wav_file.name)
#             assert np.allclose(gen_wav, orig_wav, atol=1e-8, rtol=1e-8)
#
#         # Test with new FG and BG paths
#         for _ in range(5):
#             sc.generate(orig_wav_file.name, orig_jam_file.name,
#                         disable_instantiation_warnings=True)
#             ambiscaper.generate_from_jams(orig_jam_file.name, gen_wav_file.name,
#                                       fg_path=ALT_FG_PATH, bg_path=ALT_BG_PATH)
#             # validate audio
#             orig_wav, sr = soundfile.read(orig_wav_file.name)
#             gen_wav, sr = soundfile.read(gen_wav_file.name)
#             assert np.allclose(gen_wav, orig_wav, atol=1e-8, rtol=1e-8)
#
#         # Ensure jam file saved correctly
#         ambiscaper.generate_from_jams(orig_jam_file.name, gen_wav_file.name,
#                                   jams_outfile=gen_jam_file.name)
#         orig_jam = jams.load(orig_jam_file.name)
#         gen_jam = jams.load(gen_jam_file.name)
#         assert orig_jam == gen_jam


# def test_trim():
#
#     # Things we want to test:
#     # 1. Jam trimmed correctly (mainly handled by jams.slice)
#     # 2. value dict updated correctly (event_time, event_duration, source_time)
#     # 3. ambiscaper sandbox updated correctly (n_events, poly, gini, duration)
#     # 4. audio trimmed correctly
#
#     tmpfiles = []
#     with _close_temp_files(tmpfiles):
#
#         # Create all necessary temp files
#         orig_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=True)
#         orig_jam_file = tempfile.NamedTemporaryFile(suffix='.jams', delete=True)
#
#         trim_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=True)
#         trim_jam_file = tempfile.NamedTemporaryFile(suffix='.jams', delete=True)
#
#         trimstrict_wav_file = tempfile.NamedTemporaryFile(
#             suffix='.wav', delete=True)
#         trimstrict_jam_file = tempfile.NamedTemporaryFile(
#             suffix='.jams', delete=True)
#
#         tmpfiles.append(orig_wav_file)
#         tmpfiles.append(orig_jam_file)
#         tmpfiles.append(trim_wav_file)
#         tmpfiles.append(trim_jam_file)
#         tmpfiles.append(trimstrict_wav_file)
#         tmpfiles.append(trimstrict_jam_file)
#
#         # --- Create soundscape and save to tempfiles --- #
#         sc = ambiscaper.AmbiScaper(10, 1, FG_PATH, BG_PATH)
#         sc.protected_labels = []
#         sc.ref_db = -50
#         sc.add_background(source_file=('choose', []),
#                           source_time=('const', 0))
#         # Add 5 events
#         start_times = [0.5, 2.5, 4.5, 6.5, 8.5]
#         for event_time in start_times:
#             sc.add_event(source_file=('choose', []),
#                          source_time=('const', 5),
#                          event_time=('const', event_time),
#                          event_duration=('const', 1),
#                          event_azimuth=('const', 0),
#                          event_elevation=('const', 0),
#                          event_spread=('const', 0),
#                          snr=('const', 10),
#                          pitch_shift=None,
#                          time_stretch=None)
#         sc.generate(orig_wav_file.name, orig_jam_file.name,
#                     disable_instantiation_warnings=True)
#
#         # --- Trim soundscape using ambiscaper.trim with strict=False --- #
#         ambiscaper.trim(orig_wav_file.name, orig_jam_file.name,
#                     trim_wav_file.name, trim_jam_file.name,
#                     3, 7, no_audio=False)
#
#         # --- Validate output --- #
#         # validate JAMS
#         trimjam = jams.load(trim_jam_file.name)
#         trimann = trimjam.annotations.search(namespace='ambiscaper_sound_event')[0]
#
#         # Time and duration of annotation observation must be changed, but
#         # values in the value dict must remained unchanged!
#         for idx, event in trimann.data.iterrows():
#             if event.value['role'] == 'background':
#                 assert (event.time.total_seconds() == 0 and
#                         event.duration.total_seconds() == 4 and
#                         event.value['event_time'] == 0 and
#                         event.value['event_duration'] == 10 and
#                         event.value['source_time'] == 0)
#             else:
#                 if event.time.total_seconds() == 0:
#                     assert (event.duration.total_seconds() == 0.5 and
#                             event.value['event_time'] == 2.5 and
#                             event.value['event_duration'] == 1 and
#                             event.value['source_time'] == 5)
#                 elif event.time.total_seconds() == 1.5:
#                     assert (event.duration.total_seconds() == 1 and
#                             event.value['event_time'] == 4.5 and
#                             event.value['event_duration'] == 1 and
#                             event.value['source_time'] == 5)
#                 elif event.time.total_seconds() == 3.5:
#                     assert (event.duration.total_seconds() == 0.5 and
#                             event.value['event_time'] == 6.5 and
#                             event.value['event_duration'] == 1 and
#                             event.value['source_time'] == 5)
#                 else:
#                     assert False
#
#         # validate audio
#         orig_wav, sr = soundfile.read(orig_wav_file.name)
#         trim_wav, sr = soundfile.read(trim_wav_file.name)
#         assert np.allclose(trim_wav, orig_wav[3*sr:7*sr], atol=1e-8, rtol=1e-8)


def test_get_value_from_dist():

    # const
    x = ambiscaper.core._get_value_from_dist(('const', 1))
    assert x == 1

    # choose
    for _ in range(10):
        x = ambiscaper.core._get_value_from_dist(('choose', [1, 2, 3]))
        assert x in [1, 2, 3]

    # uniform
    for _ in range(10):
        x = ambiscaper.core._get_value_from_dist(('choose', [1, 2, 3]))
        assert x in [1, 2, 3]

    # normal
    for _ in range(10):
        x = ambiscaper.core._get_value_from_dist(('normal', 5, 1))
        assert ambiscaper.util.is_real_number(x)

    # truncnorm
    for _ in range(10):
        x = ambiscaper.core._get_value_from_dist(('truncnorm', 5, 10, 0, 10))
        assert ambiscaper.util.is_real_number(x)
        assert 0 <= x <= 10

    # COPY TESTS FROM test_validate_distribution (to ensure validation applied)
    def __test_bad_tuple_list(tuple_list):
        for t in tuple_list:
            pytest.raises(AmbiScaperError, ambiscaper.core._get_value_from_dist, t)

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
               ('truncnorm', 1, 2, 'three', 5),
               ('truncnorm', 1, 2, 3, 'four'),
               ('truncnorm', 0, 2, 2, 0)]
    __test_bad_tuple_list(badargs)


def test_validate_source_file():

    # file must exist
    # create temp folder so we have path to file we know doesn't exist
    with tempfile.TemporaryDirectory() as tmpdir:
        nonfile = os.path.join(tmpdir, 'notafile')
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_source_file,
                      ('const', nonfile))

    # if choose, all files in list of files must exist
    sourcefile = 'Bycicle_Horn/chokedhorn.wav'
    with tempfile.TemporaryDirectory() as tmpdir:
        nonfile = os.path.join(tmpdir, 'notafile')
        source_file_list = [sourcefile, nonfile]
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_source_file,
                      ('choose', source_file_list))



def test_validate_time():

    def __test_bad_time_tuple(time_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_time, time_tuple)

    # bad consts
    bad_time_values = [None, -1, 1j, 'yes', [], [5]]
    for btv in bad_time_values:
        __test_bad_time_tuple(('const', btv))

    # empty list for choose
    __test_bad_time_tuple(('choose', []))

    # bad consts in list for choose
    for btv in bad_time_values:
        __test_bad_time_tuple(('choose', [btv]))

    # uniform can't have negative min value
    __test_bad_time_tuple(('uniform', -1, 1))

    # using normal will issue a warning since it can generate neg values
    pytest.warns(AmbiScaperWarning, ambiscaper.core._validate_time, ('normal', 5, 2))

    # truncnorm can't have negative min value
    __test_bad_time_tuple(('truncnorm', 0, 1, -1, 1))


def test_validate_duration():

    def __test_bad_duration_tuple(duration_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_duration,
                      duration_tuple)

    # bad consts
    bad_dur_values = [None, -1, 0, 1j, 'yes', [], [5]]
    for bdv in bad_dur_values:
        __test_bad_duration_tuple(('const', bdv))

    # empty list for choose
    __test_bad_duration_tuple(('choose', []))

    # bad consts in list for choose
    for bdv in bad_dur_values:
        __test_bad_duration_tuple(('choose', [bdv]))

    # uniform can't have negative or 0 min value
    __test_bad_duration_tuple(('uniform', -1, 1))
    __test_bad_duration_tuple(('uniform', 0, 1))

    # using normal will issue a warning since it can generate neg values
    pytest.warns(AmbiScaperWarning, ambiscaper.core._validate_duration,
                 ('normal', 5, 2))

    # truncnorm must be inside value range
    __test_bad_duration_tuple(('truncnorm', 0, 1, -1, 1))
    __test_bad_duration_tuple(('truncnorm', 0, 1, 0, 1))


def test_validate_azimuth():

    def __test_bad_azimuth_tuple(azimuth_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_azimuth,
                      azimuth_tuple)

    # bad consts
    bad_azi_values = [None, -1, 3*np.pi, 1j, 'yes', [], [8]]
    for bav in bad_azi_values:
        __test_bad_azimuth_tuple(('const', bav))

    # empty list for choose
    __test_bad_azimuth_tuple(('choose', []))

    # bad consts in list for choose
    for bav in bad_azi_values:
        __test_bad_azimuth_tuple(('const', [bav]))

    # uniform ranges must be within (0, 2pi)
    __test_bad_azimuth_tuple(('uniform',-1,1))
    __test_bad_azimuth_tuple(('uniform',0,3*np.pi))

    # using normal will issue a warning since it can generate values out of range
    pytest.warns(AmbiScaperWarning, ambiscaper.core._validate_azimuth,
                 ('normal', 5, 2))

    # truncnorm must be inside value range
    __test_bad_azimuth_tuple(('truncnorm', 0, 1, -1, 1))
    __test_bad_azimuth_tuple(('truncnorm', 0, 1, 0, 10))


def test_validate_elevation():

    def __test_bad_elevation_tuple(elevation_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_elevation,
                      elevation_tuple)

    # bad consts
    bad_ele_values = [None, -4, np.pi, 1j, 'yes', [], [5]]
    for bev in bad_ele_values:
        __test_bad_elevation_tuple(('const', bev))

    # empty list for choose
    __test_bad_elevation_tuple(('choose', []))

    # bad consts in list for choose
    for bev in bad_ele_values:
        __test_bad_elevation_tuple(('const', [bev]))

    # uniform ranges must be within (-pi, pi)
    __test_bad_elevation_tuple(('uniform',-4,1))
    __test_bad_elevation_tuple(('uniform',0,2*np.pi))

    # using normal will issue a warning since it can generate values out of range
    pytest.warns(AmbiScaperWarning, ambiscaper.core._validate_elevation,
                 ('normal', 5, 2))

    # truncnorm must be inside value range
    __test_bad_elevation_tuple(('truncnorm', 0, 1, -4, 1))
    __test_bad_elevation_tuple(('truncnorm', 0, 1, 0, 2*np.pi))

def test_validate_spread():

    def __test_bad_spread_tuple(spread_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_spread,
                      spread_tuple)

    # bad consts
    bad_spr_values = [None, -4, 1.001, 1j, 'yes', [], [5]]
    for bsv in bad_spr_values:
        __test_bad_spread_tuple(('const', bsv))

    # empty list for choose
    __test_bad_spread_tuple(('choose', []))

    # bad consts in list for choose
    for bsv in bad_spr_values:
        __test_bad_spread_tuple(('const', [bsv]))

    # uniform ranges must be within (0, 1)
    __test_bad_spread_tuple(('uniform',-1,1))
    __test_bad_spread_tuple(('uniform',0,5))
    __test_bad_spread_tuple(('uniform',-2,2))

    # using normal will issue a warning since it can generate values out of range
    pytest.warns(AmbiScaperWarning, ambiscaper.core._validate_spread,
                 ('normal', 5, 2))

    # truncnorm can't have negative or zero min value
    # truncnorm must be inside value range
    __test_bad_spread_tuple(('truncnorm', 0, 1, -1, 1))
    __test_bad_spread_tuple(('truncnorm', 0, 1, 0, 2))
    __test_bad_spread_tuple(('truncnorm', 0, 1, -3, 3))

def test_validate_snr():

    def __test_bad_snr_tuple(snr_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_snr, snr_tuple)

    # bad consts
    bad_snr_values = [None, 1j, 'yes', [], [5]]
    for bsv in bad_snr_values:
        __test_bad_snr_tuple(('const', bsv))

    # empty list for choose
    __test_bad_snr_tuple(('choose', []))

    # bad consts in list for choose
    for bsv in bad_snr_values:
        __test_bad_snr_tuple(('choose', [bsv]))


def test_validate_pitch_shift():

    def __test_bad_ps_tuple(ps_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_pitch_shift, ps_tuple)

    # bad consts
    bad_ps_values = [None, 1j, 'yes', [], [5]]
    for bv in bad_ps_values:
        __test_bad_ps_tuple(('const', bv))

    # empty list for choose
    __test_bad_ps_tuple(('choose', []))

    # bad consts in list for choose
    for bv in bad_ps_values:
        __test_bad_ps_tuple(('choose', [bv]))


def test_validate_time_stretch():

    def __test_bad_ts_tuple(ts_tuple):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_time_stretch,
                      ts_tuple)

    # bad consts
    bad_ps_values = [None, 1j, 'yes', [], [5], -5, 0]
    for bv in bad_ps_values:
        __test_bad_ts_tuple(('const', bv))

    # empty list for choose
    __test_bad_ts_tuple(('choose', []))

    # bad consts in list for choose
    for bv in bad_ps_values:
        __test_bad_ts_tuple(('choose', [bv]))

    # bad start time in distributions
    __test_bad_ts_tuple(('uniform', 0, 1))
    __test_bad_ts_tuple(('uniform', -5, 1))
    __test_bad_ts_tuple(('truncnorm', 5, 1, 0, 10))
    __test_bad_ts_tuple(('truncnorm', 5, 1, -5, 10))

    # Using normal dist must raise warning since can give neg or 0 values
    pytest.warns(
        AmbiScaperWarning, ambiscaper.core._validate_time_stretch, ('normal', 5, 1))


def test_validate_event():

    # Let's check a valid event
    ambiscaper.core._validate_event(
        source_file=('choose', []),
        source_time=('const', 0),
        event_time=('const', 0),
        event_duration=('const', 1),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 0),
        pitch_shift=None,
        time_stretch=None)

def test_validate_soundscape_duration():

    def __test_bad_soundscape_duration(duration):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_soundscape_duration,
                      duration)

    # bad consts
    bad_duration_values = [None, 1j, 'yes', [], [5], -5, 0]
    for bv in bad_duration_values:
        __test_bad_soundscape_duration(bv)


def test_validate_ambisonics_order():

    def __test_bad_ambisonics_order(order):
        pytest.raises(AmbiScaperError, ambiscaper.core._validate_ambisonics_order,
                      order)

    # bad consts
    bad_order_values = [None, 'yes', [], [5], -5, 0.5]
    for bv in bad_order_values:
        __test_bad_ambisonics_order(bv)


def test_init():
    '''
    Test creation of AmbiScaper object.
    '''

    # bad duration
    sc = pytest.raises(AmbiScaperError, ambiscaper.AmbiScaper, -5, 1,  FG_PATH, BG_PATH)

    # bad ambisonics order
    sc = pytest.raises(AmbiScaperError, ambiscaper.AmbiScaper, 1, -1, FG_PATH, BG_PATH)
    sc = pytest.raises(AmbiScaperError, ambiscaper.AmbiScaper, 1, 1.3, FG_PATH, BG_PATH)

    # bad fg path
    sc = pytest.raises(AmbiScaperError, ambiscaper.AmbiScaper, 10.0, 3,
                       'tests/data/audio/wrong',
                       BG_PATH)

    # bad bg path
    sc = pytest.raises(AmbiScaperError, ambiscaper.AmbiScaper, 10.0, 3,
                       FG_PATH,
                       'tests/data/audio/wrong')

    # all args valid
    sc = ambiscaper.AmbiScaper(10.0, 3, FG_PATH, BG_PATH)
    assert sc.fg_path == FG_PATH
    assert sc.bg_path == BG_PATH

    sc = ambiscaper.AmbiScaper(10.0, 3, FG_PATH, None)
    assert sc.fg_path == FG_PATH
    assert sc.bg_path == None

    # ensure default values have been set
    sc = ambiscaper.AmbiScaper(10.0, 3, FG_PATH, BG_PATH)
    assert sc.sr == 48000
    assert sc.ref_db == -30
    assert sc.fade_in_len == 0.01  # 10 ms
    assert sc.fade_out_len == 0.01  # 10 ms


def test_add_background():
    '''
    Test AmbiScaper.add_background function

    '''
    sc = ambiscaper.AmbiScaper(10.0, 3, FG_PATH, BG_PATH)


    # source_file, source_time
    sc.add_background(("choose", []), ("const", 0))

    # Check that event has been added to the background spec, and that the
    # values that are set automatically by this method (event_time,
    # event_duration, event_azimuth, event_elevation, snr and role) are correctly set to their expected values.
    bg_event_expected = EventSpec(source_file=("choose", []),
                                  event_id=None,
                                  source_time=("const", 0),
                                  event_time=("const", 0),
                                  event_duration=("const", sc.duration),
                                  event_azimuth=('const', 0),
                                  event_elevation=('const', 0),
                                  event_spread=('const', 0),
                                  snr=("const", 0),
                                  role='background',
                                  pitch_shift=None,
                                  time_stretch=None)

    assert sc.bg_spec == [bg_event_expected]


def test_add_event():

    sc = ambiscaper.AmbiScaper(10.0, 3, FG_PATH, BG_PATH)

    # Initially fg_spec should be empty
    assert sc.fg_spec == []

    # Add one event
    sc.add_event(source_file=('choose', []),
                 source_time=('const', 0),
                 event_time=('uniform', 0, 9),
                 event_duration=('truncnorm', 2, 1, 1, 3),
                 event_azimuth=('const', 0),
                 event_elevation=('const', 0),
                 event_spread=('const', 0),
                 snr=('uniform', 10, 20),
                 pitch_shift=('normal', 0, 1),
                 time_stretch=('uniform', 0.8, 1.2))
    # Now should be one event in fg_spec
    assert len(sc.fg_spec) == 1
    fg_event_expected = EventSpec(source_file=('choose', []),
                                  event_id=None,
                                  source_time=('const', 0),
                                  event_time=('uniform', 0, 9),
                                  event_duration=('truncnorm', 2, 1, 1, 3),
                                  event_azimuth=('const', 0),
                                  event_elevation=('const', 0),
                                  event_spread=('const', 0),
                                  snr=('uniform', 10, 20),
                                  role='foreground',
                                  pitch_shift=('normal', 0, 1),
                                  time_stretch=('uniform', 0.8, 1.2))
    assert sc.fg_spec[0] == fg_event_expected


def test_add_simulated_reverb():
    # TODO!
    return 0


def test_add_sofa_reverb():

    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    sofa_path = os.path.abspath('./SOFA')
    sc.set_sofa_reverb_folder_path(sofa_path)
    name_tuple = ('const', 'testpysofa.sofa')
    wrap_tuple = ('const', 'random')

    # Assert correct assignment
    sc.add_sofa_reverb(name=name_tuple,
                       wrap=wrap_tuple)

    assert sc.reverb_spec == SOFAReverbSpec(name_tuple,wrap_tuple)


def test_instantiate_event():


    # BACKGROUND
    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    bg_event = EventSpec(source_file=("const", 'Acoustics_Book/adult_female_speech.wav'),
                         event_id=None,
                         source_time=('const', 0),
                         event_time=('uniform', 0, 9),
                         event_duration=('truncnorm', 2, 1, 1, 3),
                         event_azimuth=('truncnorm', np.pi, 1, 0, 2 * np.pi),
                         event_elevation=('truncnorm', 0, 1, -np.pi/2, np.pi/2),
                         event_spread=('uniform', 0, 1),
                         snr=('uniform', 10, 20),
                         role='background',
                         pitch_shift=('normal', 0, 1),
                         time_stretch=('uniform', 0.8, 1.2))

    instantiated_bg_event = sc._instantiate_event(event=bg_event,
                                                  event_idx=0,
                                                  isbackground=True,
                                                  allow_repeated_source=True,
                                                  used_source_files=[],
                                                  disable_instantiation_warnings=True)

    assert instantiated_bg_event.source_file == os.path.abspath('samples/Acoustics_Book/adult_female_speech.wav')
    assert instantiated_bg_event.event_id == 'bg0'
    assert instantiated_bg_event.source_time == 0
    assert 0 <= instantiated_bg_event.event_time <= 9
    assert 1 <= instantiated_bg_event.event_duration <= 3
    assert 0 <= instantiated_bg_event.event_azimuth <= 2*np.pi
    assert -np.pi/2 <= instantiated_bg_event.event_elevation <= np.pi/2
    assert 0 <= instantiated_bg_event.event_spread <= 1
    assert 10 <= instantiated_bg_event.snr <= 20
    assert instantiated_bg_event.role == 'background'
    assert ambiscaper.util.is_real_number(instantiated_bg_event.pitch_shift)
    assert 0.8 <= instantiated_bg_event.time_stretch <= 1.2


    # FOREGROUND
    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    fg_event = EventSpec(source_file=('const', 'Acoustics_Book/bagpipe_music.wav'),
                         event_id=None,
                         source_time=('const', 0),
                         event_time=('uniform', 0, 9),
                         event_duration=('truncnorm', 2, 1, 1, 3),
                         event_azimuth=('truncnorm', np.pi, 1, 0, 2 * np.pi),
                         event_elevation=('truncnorm', 0, 1, -np.pi/2, np.pi/2),
                         event_spread=('uniform', 0, 1),
                         snr=('uniform', 10, 20),
                         role='foreground',
                         pitch_shift=None,
                         time_stretch=('uniform', 0.8, 1.2))

    # test valid case
    instantiated_event = sc._instantiate_event(event=fg_event,
                                               event_idx=0,
                                               isbackground=False,
                                               allow_repeated_source=True,
                                               used_source_files=[],
                                               disable_instantiation_warnings=True)

    assert instantiated_event.source_file == os.path.abspath('samples/Acoustics_Book/bagpipe_music.wav')
    assert instantiated_event.event_id == 'fg0'
    assert instantiated_event.source_time == 0
    assert 0 <= instantiated_event.event_time <= 9
    assert 1 <= instantiated_event.event_duration <= 3
    assert 0 <= instantiated_event.event_azimuth <= 2*np.pi
    assert -np.pi/2 <= instantiated_event.event_elevation <= np.pi/2
    assert 0 <= instantiated_event.event_spread <= 1
    assert 10 <= instantiated_event.snr <= 20
    assert instantiated_event.role == 'foreground'
    assert instantiated_event.pitch_shift is None
    assert 0.8 <= instantiated_event.time_stretch <= 1.2

    # event duration longer than source duration: warning
    fg_event2 = fg_event._replace(event_duration=('const', 50))
    pytest.warns(AmbiScaperWarning, sc._instantiate_event,
                 event=fg_event2,
                 event_idx=1)

    # event duration longer than soundscape duration: warning
    fg_event3 = fg_event._replace(event_time=('const', 0),
                                  event_duration=('const', 15),
                                  time_stretch=None)
    pytest.warns(AmbiScaperWarning, sc._instantiate_event,
                 event=fg_event3,
                 event_idx=1)

    # stretched event duration longer than soundscape duration: warning
    fg_event4 = fg_event._replace(event_time=('const', 0),
                                  event_duration=('const', 6),
                                  time_stretch=('const', 2))
    pytest.warns(AmbiScaperWarning, sc._instantiate_event,
                 event=fg_event4,
                 event_idx=1)

    # source_time + event_duration > source_duration: warning
    fg_event5 = fg_event._replace(event_time=('const', 0),
                                  event_duration=('const', 8),
                                  source_time=('const', 50))
    pytest.warns(AmbiScaperWarning, sc._instantiate_event,
                 event=fg_event5,
                 event_idx=1)

    # event_time + event_duration > soundscape duration: warning
    fg_event6 = fg_event._replace(event_time=('const', 8),
                                  event_duration=('const', 5),
                                  time_stretch=None)
    pytest.warns(AmbiScaperWarning, sc._instantiate_event,
                 event=fg_event6,
                 event_idx=1)

    # event_time + stretched event_duration > soundscape duration: warning
    fg_event7 = fg_event._replace(event_time=('const', 5),
                                  event_duration=('const', 4),
                                  time_stretch=('const', 2))
    pytest.warns(AmbiScaperWarning, sc._instantiate_event,
                 event=fg_event7,
                 event_idx=1)


    # Test different distribution tuples combinations

    # Choose between all source files, and ensure we choose one of them
    fg_event = EventSpec(source_file=('choose', []),
                         event_id=None,
                         source_time=('const', 0),
                         event_time=('uniform', 0, 9),
                         event_duration=('const', 0.5),
                         event_azimuth=('truncnorm', np.pi, 1, 0, 2 * np.pi),
                         event_elevation=('truncnorm', 0, 1, -np.pi/2, np.pi/2),
                         event_spread=('uniform', 0, 1),
                         snr=('uniform', 10, 20),
                         role='foreground',
                         pitch_shift=('normal', 0, 1),
                         time_stretch=('uniform', 0.8, 1.2))

    instantiated_event = sc._instantiate_event(event=fg_event,
                                               event_idx=0,
                                               isbackground=False)

    available_source_files = _get_sorted_audio_files_recursive(FG_PATH)
    assert instantiated_event.source_file in available_source_files

    # Choose between some of the source files
    fg_event = EventSpec(source_file=('choose', ['Bicycle_Horn/chokedhorn.wav','Bicycle_Horn/classichorn.wav']),
                         event_id=None,
                         source_time=('const', 0),
                         event_time=('uniform', 0, 9),
                         event_duration=('const', 0.5),
                         event_azimuth=('truncnorm', np.pi, 1, 0, 2 * np.pi),
                         event_elevation=('truncnorm', 0, 1, -np.pi / 2, np.pi / 2),
                         event_spread=('uniform', 0, 1),
                         snr=('uniform', 10, 20),
                         role='foreground',
                         pitch_shift=('normal', 0, 1),
                         time_stretch=('uniform', 0.8, 1.2))

    instantiated_event = sc._instantiate_event(event=fg_event,
                                               event_idx=0,
                                               isbackground=False)

    available_source_files =  [os.path.abspath(p) for p in ['samples/Bicycle_Horn/chokedhorn.wav','samples/Bicycle_Horn/classichorn.wav']]
    assert instantiated_event.source_file in available_source_files


    # Error on source file distribution

    fg_event = EventSpec(source_file=('incorrect_distribution', []),
                         event_id=None,
                         source_time=('const', 0),
                         event_time=('uniform', 0, 9),
                         event_duration=('const', 0.5),
                         event_azimuth=('truncnorm', np.pi, 1, 0, 2 * np.pi),
                         event_elevation=('truncnorm', 0, 1, -np.pi / 2, np.pi / 2),
                         event_spread=('uniform', 0, 1),
                         snr=('uniform', 10, 20),
                         role='foreground',
                         pitch_shift=('normal', 0, 1),
                         time_stretch=('uniform', 0.8, 1.2))

    pytest.raises(AmbiScaperError, sc._instantiate_event,
                  event=fg_event,
                  event_idx=1,
                  isbackground=False)


    # Source repetition test
    # There is only one file which is still not used ('paphorn.wav')
    # Let's add it by selecting 'source_file=('choose', []),
    # and iterating until it's selected
    # [NOTE: there are 20 iterations, so it's very unlikely that the missing file won't appear...]


    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path='samples/Bicycle_Horn', bg_path=BG_PATH)
    for i in range(20):
        fg_event = EventSpec(source_file=('choose', []),
                             event_id=None,
                             source_time=('const', 0),
                             event_time=('uniform', 0, 9),
                             event_duration=('const', 0.5),
                             event_azimuth=('truncnorm', np.pi, 1, 0, 2 * np.pi),
                             event_elevation=('truncnorm', 0, 1, -np.pi / 2, np.pi / 2),
                             event_spread=('uniform', 0, 1),
                             snr=('uniform', 10, 20),
                             role='foreground',
                             pitch_shift=('normal', 0, 1),
                             time_stretch=('uniform', 0.8, 1.2))
        try:
            used_source_files = ['samples/Bicycle_Horn/chokedhorn.wav',
                                 'samples/Bicycle_Horn/classichorn.wav',
                                 'samples/Bicycle_Horn/classichorn_double.wav']

            instantiated_event = sc._instantiate_event(event=fg_event,
                                                       event_idx=0,
                                                       isbackground=False,
                                                       allow_repeated_source=False,
                                                       used_source_files=used_source_files)
        except AmbiScaperError:
            pass

    # Now the instanciated event file must be the file missing (paphorn.wav)
    assert instantiated_event.source_file == (
            'samples/Bicycle_Horn/paphorn.wav')

    # Now all files in the folder have been used
    # Therefore, AmbiScaper should return Error
    pytest.raises(AmbiScaperError, sc._instantiate_event,
                  event=fg_event,
                  event_idx=1,
                  isbackground=False,
                  allow_repeated_source=False,
                  used_source_files=used_source_files)




def test_instantiate_reverb():

    # Instantiate SOFA reverb
    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    sc.set_sofa_reverb_folder_path(os.path.abspath('./SOFA'))

    sofa_reverb_spec = SOFAReverbSpec(name=('const', 'testpysofa.sofa'),
                                      wrap=('const', 'random'))
    instantiated_spec = sc._instantiate_reverb(reverb_spec=sofa_reverb_spec)
    assert type(instantiated_spec) == SOFAReverbSpec

    # TODO: SMIR REVERB



def test_instantiate_smir_reverb():
        # TODO:
    return 0

def test_instantiate_sofa_reverb():

    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    sc.set_sofa_reverb_folder_path(os.path.abspath('./SOFA'))

    # Check name
    ## Const value
    sofa_reverb_spec = SOFAReverbSpec(name=('const', 'testpysofa.sofa'),
                                      wrap=('const', 'random'))
    instantiated_spec = sc._instantiate_sofa_reverb(reverb_spec=sofa_reverb_spec)
    assert instantiated_spec.name == 'testpysofa.sofa'
    assert instantiated_spec.wrap == 'random'

    ## Choose among all available files
    sofa_reverb_spec2 = sofa_reverb_spec._replace(name=('choose', []))
    instantiated_spec2 = sc._instantiate_sofa_reverb(reverb_spec=sofa_reverb_spec2)
    assert instantiated_spec2.name in sc.retrieve_available_sofa_reverb_files()

    # Check wrap
    ## Choose among different wraps
    sofa_reverb_spec3 = sofa_reverb_spec._replace(wrap=('choose', []))
    instantiated_spec3 = sc._instantiate_sofa_reverb(reverb_spec=sofa_reverb_spec3)
    assert instantiated_spec3.wrap in SOFAReverb.valid_wrap_values






def test_set_sofa_reverb_folder_path():

    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)

    # Folder does not exist
    sofa_path = 'fake_path'
    pytest.raises(AmbiScaperError,sc.set_sofa_reverb_folder_path, sofa_path)

    # Not a folder
    sofa_path = os.path.abspath('./SOFA/testpysofa.sofa')
    pytest.raises(AmbiScaperError, sc.set_sofa_reverb_folder_path, sofa_path)

    # Correct: no error
    sofa_path = os.path.abspath('./SOFA')
    sc.set_sofa_reverb_folder_path(sofa_path)
    assert sofa_path == sc.sofaReverb.sofa_reverb_folder_path


def test_get_sofa_simulated_reverb():

    # Path not set: None
    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    assert None == sc.get_sofa_reverb_folder_path()

    # Path correctly set
    sofa_path = os.path.abspath('./SOFA')
    sc.set_sofa_reverb_folder_path(sofa_path)
    assert sofa_path == sc.get_sofa_reverb_folder_path()


def test_retrieve_available_sofa_reverb_files():

    sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)

    # Error if path not specified
    pytest.raises(AmbiScaperError,sc.retrieve_available_sofa_reverb_files)

    sofa_path = os.path.abspath('./SOFA')
    sc.set_sofa_reverb_folder_path(sofa_path)

    # At the moment we have only one
    groundtruth = ['testpysofa.sofa']

    # Check with unordered lists
    assert set(sc.retrieve_available_sofa_reverb_files()) == set(groundtruth)




def test_instantiate():


    # TODO: FIX REVERB SPEC STUFF

    # Here we just instantiate a known fixed spec and check if that jams
    # we get back is as expected.
    sc = ambiscaper.AmbiScaper(10.0, 1, fg_path=FG_PATH, bg_path=BG_PATH)
    sc.ref_db = -50

    # background
    sc.add_background(
        source_file=(
            'const',
            'Acoustics_Book/adult_female_speech.wav'),
        source_time=('const', 0))

    # foreground events
    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/chokedhorn.wav'),
        source_time=('const', 5),
        event_time=('const', 2),
        event_duration=('const', 5),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 5),
        pitch_shift=None,
        time_stretch=None)

    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/classichorn.wav'),
        source_time=('const', 0),
        event_time=('const', 5),
        event_duration=('const', 2),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 20),
        pitch_shift=('const', 1),
        time_stretch=None)

    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/paphorn.wav'),
        source_time=('const', 0),
        event_time=('const', 7),
        event_duration=('const', 2),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 10),
        pitch_shift=None,
        time_stretch=('const', 1.2))

    jam = sc._instantiate(disable_instantiation_warnings=True)
    regjam = jams.load(REG_JAM_PATH)
    # print(jam)
    # print(regjam)

    # Note: can't compare directly, since:
    # 1. ambiscaper/and jams library versions may change
    # 2. raw annotation sandbox stores specs as OrderedDict and tuples, whereas
    # loaded ann (regann) simplifies those to dicts and lists
    # assert jam == regression_jam

    # Must compare each part "manually"
    # 1. compare file metadata
    for k, kreg in zip(jam.file_metadata.keys(), regjam.file_metadata.keys()):
        assert k == kreg
        if k != 'jams_version':
            assert jam.file_metadata[k] == regjam.file_metadata[kreg]

    # 2. compare jams sandboxes
    assert jam.sandbox == regjam.sandbox

    # 3. compare annotations
    assert len(jam.annotations) == len(regjam.annotations) == 1
    ann = jam.annotations[0]
    regann = regjam.annotations[0]

    # 3.1 compare annotation metadata
    assert ann.annotation_metadata == regann.annotation_metadata

    # 3.2 compare sandboxes
    # Note: can't compare sandboxes directly, since in raw jam ambiscaper sandbox
    # stores event specs in EventSpec object (named tuple), whereas in loaded
    # jam these will get converted to list of lists.
    # assert ann.sandbox == regann.sandbox
    assert len(ann.sandbox.keys()) == len(regann.sandbox.keys()) == 1
    assert 'ambiscaper' in ann.sandbox.keys()
    assert 'ambiscaper' in regann.sandbox.keys()

    # everything but the specs can be compared directly:
    for k, kreg in zip(sorted(ann.sandbox.ambiscaper.keys()),
                       sorted(regann.sandbox.ambiscaper.keys())):
        assert k == kreg
        if k not in ['bg_spec', 'fg_spec', 'bg_path', 'fg_path']:
            assert ann.sandbox.ambiscaper[k] == regann.sandbox.ambiscaper[kreg]

    # the relative paths might be different, so let's check only the last part
    for path in ['bg_path','fg_path']:
        p1 = str(ann.sandbox.ambiscaper[path])
        p2 = str(regann.sandbox.ambiscaper[path])
        assert os.path.split(p1)[-1] == os.path.split(p2)[-1]

    # to compare specs need to covert raw specs to list of lists
    for spec in ['bg_spec', 'fg_spec']:
        assert (
            [[list(x) if type(x) == tuple else x for x in e] for e in
             ann.sandbox.ambiscaper[spec]] == regann.sandbox.ambiscaper[spec])

    # 3.3. compare namespace, time and duration
    assert ann.namespace == regann.namespace
    assert ann.time == regann.time
    assert ann.duration == regann.duration

    # 3.4 compare data
    (ann.data == regann.data).all().all()


def test_generate_audio():

    # Regression test: same spec, same audio (not this will fail if we update
    # any of the audio processing techniques used (e.g. change time stretching
    # algorithm.
    sc = ambiscaper.AmbiScaper(10.0, 1, fg_path=FG_PATH, bg_path=BG_PATH)
    sc.ref_db = -50

    # background
    sc.add_background(
        source_file=(
            'const',
            'Acoustics_Book/adult_female_speech.wav'),
        source_time=('const', 0))

    # foreground events
    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/chokedhorn.wav'),
        source_time=('const', 5),
        event_time=('const', 2),
        event_duration=('const', 5),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 5),
        pitch_shift=None,
        time_stretch=None)

    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/classichorn.wav'),
        source_time=('const', 0),
        event_time=('const', 5),
        event_duration=('const', 2),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 20),
        pitch_shift=('const', 1),
        time_stretch=None)

    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/paphorn.wav'),
        source_time=('const', 0),
        event_time=('const', 7),
        event_duration=('const', 2),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 10),
        pitch_shift=None,
        time_stretch=('const', 1.2))

    # tmpfiles = []
    # with _close_temp_files(tmpfiles):

    # wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=True)
    # tmpfiles.append(wav_file)

    # Create temmporary folder for the output
    tmp_dir = tempfile.mkdtemp()
    # Output files will have the same name as the folder, so keep it
    tmp_name = os.path.split(tmp_dir)[-1]

    # Following code will raise a warning because the tmpfolder already exists
    # (we have just created it)
    # So, disable warnings temporally
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sc.generate(destination_path=tmp_dir,
                    generate_txt=True,
                    disable_instantiation_warnings=True)


    wav_file_name = os.path.join(tmp_dir, tmp_name + '.wav')

    jam = sc._instantiate(disable_instantiation_warnings=True)
    annotation_array = jam.annotations
    # print(jam.annotations[0])
    # print(jam.annotations[0].search(namespace='ambiscaper_sound_event'))
    # print(jam.annotations[0].search(namespace='ambiscaper_sound_event')[0])
    sc._generate_audio(destination_path=tmp_dir,
                       audio_filename=wav_file_name,
                       annotation_array=annotation_array)

    # validate audio
    wav, sr = soundfile.read(wav_file_name)
    regwav, sr = soundfile.read(REG_WAV_PATH)
    assert np.allclose(wav, regwav, atol=1e-4, rtol=1e-4)

    # TODO!!! continue here

    # # namespace must be ambiscaper_sound_event
    # jam.annotations[0].namespace = 'tag_open'
    #
    # print jam.annotations[0].namespace
    #
    # pytest.raises(AmbiScaperError, sc._generate_audio,
    #               tmp_dir,
    #               wav_file_name,
    #               jam.annotations[0])
    #
    # # unsupported event role must raise error
    # jam.annotations[0].namespace = 'ambiscaper_sound_event'
    # jam.annotations[0].data.loc[3]['value']['role'] = 'ewok'
    # pytest.raises(AmbiScaperError, sc._generate_audio, wav_file_name,
    #               jam.annotations[0])
    #
    # # soundscape with no events will raise warning and won't generate audio
    # sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    # sc.ref_db = -50
    # jam = sc._instantiate(disable_instantiation_warnings=True)
    # pytest.warns(AmbiScaperWarning, sc._generate_audio, wav_file_name,
    #              jam.annotations[0])
    #
    # # soundscape with only one event will use transformer (regression test)
    # sc = ambiscaper.AmbiScaper(10.0, 3, fg_path=FG_PATH, bg_path=BG_PATH)
    # sc.ref_db = -20
    # # background
    # sc.add_background(
    #     source_file=('const',
    #                  'tests/data/audio/background/park/'
    #                  '268903__yonts__city-park-tel-aviv-israel.wav'),
    #     source_time=('const', 0))
    # jam = sc._instantiate(disable_instantiation_warnings=True)
    # sc._generate_audio(wav_file.name, jam.annotations[0], reverb=0.2)
    # # validate audio
    # wav, sr = soundfile.read(wav_file.name)
    # regwav, sr = soundfile.read(REG_BGONLY_WAV_PATH)
    # assert np.allclose(wav, regwav, atol=1e-4, rtol=1e-4)

    # Delete recursively the temp folder
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_generate():

    # Final regression test on all files
    sc = ambiscaper.AmbiScaper(10.0, 1, fg_path=FG_PATH, bg_path=BG_PATH)
    sc.ref_db = -50

    # background
    sc.add_background(
        source_file=(
            'const',
            'Acoustics_Book/adult_female_speech.wav'),
        source_time=('const', 0))

    # foreground events
    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/chokedhorn.wav'),
        source_time=('const', 5),
        event_time=('const', 2),
        event_duration=('const', 5),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 5),
        pitch_shift=None,
        time_stretch=None)

    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/classichorn.wav'),
        source_time=('const', 0),
        event_time=('const', 5),
        event_duration=('const', 2),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 20),
        pitch_shift=('const', 1),
        time_stretch=None)

    sc.add_event(
        source_file=('const',
                     'Bicycle_Horn/paphorn.wav'),
        source_time=('const', 0),
        event_time=('const', 7),
        event_duration=('const', 2),
        event_azimuth=('const', 0),
        event_elevation=('const', 0),
        event_spread=('const', 0),
        snr=('const', 10),
        pitch_shift=None,
        time_stretch=('const', 1.2))


    # Create temmporary folder for the output
    tmp_dir = tempfile.mkdtemp()
    # Output files will have the same name as the folder, so keep it
    tmp_name = os.path.split(tmp_dir)[-1]

    # Following code will raise a warning because the tmpfolder already exists
    # (we have just created it)
    # So, disable warnings temporally
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sc.generate(destination_path = tmp_dir,
                    generate_txt=True,
                    disable_instantiation_warnings=True)

    # validate audio
    wav_file_name = os.path.join(tmp_dir,tmp_name+'.wav')
    wav, sr = soundfile.read(wav_file_name)
    regwav, sr = soundfile.read(REG_WAV_PATH)
    assert np.allclose(wav, regwav, atol=1e-4, rtol=1e-4)

    # validate jams
    jams_file_name = os.path.join(tmp_dir, tmp_name + '.jams')
    jam = jams.load(jams_file_name)
    regjam = jams.load(REG_JAM_PATH)
    assert jam == regjam

    # validate txt
    txt_file_name = os.path.join(tmp_dir, tmp_name + '.txt')
    txt = pd.read_csv(txt_file_name, header=None, sep='\t')
    regtxt = pd.read_csv(REG_TXT_PATH, header=None, sep='\t')
    assert (txt == regtxt).all().all()

    # Delete recursively the temp folder
    shutil.rmtree(tmp_dir, ignore_errors=True)