# CREATED: 10/14/16 12:35 PM by Justin Salamon <justin.salamon@nyu.edu>
'''
Utility functions
=================
'''

from contextlib import contextmanager
import logging
import os
import glob

from .ambiscaper_exceptions import AmbiScaperError
import scipy
import numpy as np
from numbers import Number
import random
import fnmatch


event_foreground_id_string = 'fg'
event_background_id_string = 'bg'


@contextmanager
def _close_temp_files(tmpfiles):
    '''
    Utility function for creating a context and closing all temporary files
    once the context is exited. For correct functionality, all temporary file
    handles created inside the context must be appended to the ```tmpfiles```
    list.

    Parameters
    ----------
    tmpfiles : list
        List of temporary file handles

    '''

    yield
    for t in tmpfiles:
        try:
            t.close()
            os.unlink(t.name)
        except:
            pass


@contextmanager
def _set_temp_logging_level(level):
    '''
    Utility function for temporarily changing the logging level using contexts.

    Parameters
    ----------
    level : str or int
        The desired temporary logging level. For allowed values see:
        https://docs.python.org/2/library/logging.html#logging-levels

    '''
    logger = logging.getLogger()
    current_level = logger.level
    logger.setLevel(level)
    yield
    logger.setLevel(current_level)


def _get_sorted_files(folder_path):
    '''
    Return a list of absolute paths to all valid files contained within the
    folder specified by ```folder_path```.

    Parameters
    ----------
    folder_path : str
        Path to the folder to scan for files.

    Returns
    -------
    files : list
        List of absolute paths to all valid files contained within
        ```folder_path```.

    '''

    # Ensure path points to valid folder
    _validate_folder_path(folder_path)

    # Get folder contents and filter for valid files
    # Note, we sort the list to ensure consistent behavior across operating
    # systems.
    files = sorted(glob.glob(os.path.join(folder_path, "*")))
    files = [f for f in files if os.path.isfile(f)]

    return files

def _get_sorted_audio_files_recursive(folder_path):
    '''
    Recursive implementation of _get_sorted_files()
    Also filters only .wav files
    :param folder_path:
    :return:
    '''
    # Ensure path points to valid folder
    _validate_folder_path(folder_path)

    # Get folder contents and filter for valid files
    # Note, we sort the list to ensure consistent behavior across operating
    # systems.

    files = []
    for dirpath, dirnames, dirfiles in os.walk(folder_path):
        for f in fnmatch.filter(dirfiles, '*.wav'):
            files.append(os.path.join(dirpath,f))

    files = sorted(files)
    return files


def _validate_folder_path(folder_path):
    '''
    Validate that a provided path points to a valid folder.

    Parameters
    ----------
    folder_path : str
        Path to a folder.

    Raises
    ------
    AmbiScaperError
        If ```folder_path``` does not point to a valid folder.

    '''

    if not os.path.isdir(folder_path):
        raise AmbiScaperError(
            'Folder path "{:s}" does not point to a valid folder'.format(
                str(folder_path)))



def _trunc_norm(mu, sigma, trunc_min, trunc_max):
    '''
    Return a random value sampled from a truncated normal distribution with
    mean ```mu``` and standard deviation ```sigma``` whose values are limited
    between ```trunc_min``` and ```trunc_max```.

    Parameters
    ----------
    mu : float
        The mean of the truncated normal distribution
    sig : float
        The standard deviation of the truncated normal distribution
    trunc_min : float
        The minimum value allowed for the distribution (lower boundary)
    trunc_max : float
        The maximum value allowed for the distribution (upper boundary)

    Returns
    -------
    value : float
        A random value sampled from the truncated normal distribution defined
        by ```mu```, ```sigma```, ```trunc_min``` and ```trunc_max```.

    '''

    # By default truncnorm expects a (lower boundary) and b (upper boundary)
    # values for a standard normal distribution (mu=0, sigma=1), so we need
    # to recompute a and b given the user specified parameters.
    a, b = (trunc_min - mu) / float(sigma), (trunc_max - mu) / float(sigma)
    return scipy.stats.truncnorm.rvs(a, b, mu, sigma)


def max_polyphony(ann):
    '''
    Given an annotation of sound events, compute the maximum polyphony, i.e.
    the maximum number of simultaneous events at any given point in time. Only
    foreground events are taken into consideration for computing the polyphony.

    Parameters
    ----------
    ann : JAMS.Annotation

    Returns
    -------
    polyphony : int
        Maximum number of simultaneous events at any point in the annotation.
    '''

    # If there are no foreground events the polyphony is 0
    roles = [v['role'] for v in ann.data['value']]
    if 'foreground' not in roles:
        return 0
    else:
        # Keep only foreground events
        int_time, int_val = ann.data.to_interval_values()
        int_time_clean = []
        for t, v in zip(int_time, int_val):
            if v['role'] == 'foreground':
                int_time_clean.append(t)
        int_time_clean = np.asarray(int_time_clean)

        # Sort and reshape
        arrivals = np.sort(int_time_clean[:, 0]).reshape(-1, 1)
        departures = np.sort(int_time_clean[:, 1]).reshape(-1, 1)

        # Onsets are +1, offsets are -1
        arrivals = np.concatenate(
            (arrivals, np.ones(arrivals.shape)), axis=1)
        departures = np.concatenate(
            (departures, -np.ones(departures.shape)), axis=1)

        # Merge arrivals and departures and sort
        entry_log = np.concatenate((arrivals, departures), axis=0)
        entry_log_sorted = entry_log[entry_log[:, 0].argsort()]

        # Get maximum number of simultaneously occurring events
        polyphony = np.max(np.cumsum(entry_log_sorted[:, 1]))

        return int(polyphony)


def polyphony_gini(ann, hop_size=0.01):
    '''
    Compute the gini coefficient of the annotation's polyphony time series.

    Useful as an estimate of the polyphony "flatness" or entropy. The
    coefficient is in the range [0,1] and roughly inverse to entropy: a
    distribution that's close to uniform will have a low gini coefficient
    (high entropy), vice versa.
    https://en.wikipedia.org/wiki/Gini_coefficient

    Parameters
    ----------
    ann : jams.Annotation
        Annotation for which to compute the normalized polyphony entropy. Must
        be of the sound_event namespace.
    hop_size : float
        The hop size for sampling the polyphony time series.

    Returns
    -------
    polyphony_gini: float
        Gini coefficient computed from the annotation's polyphony time series.

    Raises
    ------
    AmbiScaperError
        If the annotation does not have a duration value or if its namespace is
        not sound_event.

    '''

    if not ann.duration:
        raise AmbiScaperError('Annotation does not have a duration value set.')

    if ann.namespace != 'ambiscaper_sound_event':
        raise AmbiScaperError(
            'Annotation namespace must be ambiscaper_sound_event, found {:s}.'.format(
                ann.namespace))

    # If there are no foreground events the gini coefficient is 0
    roles = [v['role'] for v in ann.data['value']]
    if 'foreground' not in roles:
        return 0

    # Sample the polyphony using the specified hop size
    n_samples = int(np.floor(ann.duration / float(hop_size)) + 1)
    times = np.linspace(0, (n_samples-1) * hop_size, n_samples)
    values = np.zeros_like(times)

    for idx in ann.data.index:
        if ann.data.loc[idx, 'value']['role'] == 'foreground':
            start_time = ann.data.loc[idx, 'time'].total_seconds()
            end_time = (
                start_time + ann.data.loc[idx, 'duration'].total_seconds())
            start_idx = np.argmin(np.abs(times - start_time))
            end_idx = np.argmin(np.abs(times - end_time)) - 1
            values[start_idx:end_idx + 1] += 1
    values = values[:-1]

    # DEBUG
    # vstring = ('{:d} ' * len(values)).format(*tuple([int(v) for v in values]))
    # print(vstring)
    # print(' ')

    # Compute gini as per:
    # http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    values += 1e-6  # all values must be positive
    values = np.sort(values)  # sort values
    n = len(values)
    i = np.arange(n) + 1
    gini = np.sum((2*i - n - 1) * values) / (n * np.sum(values))
    return (1 - gini)


def is_real_number(num):
    '''
    Check if a value is a real scalar by aggregating several numpy checks.

    Parameters
    ----------
    num : any type
        The parameter to check

    Returns
    ------
    check : bool
        True if ```num``` is a real scalar, False otherwise.

    '''

    if (not np.isreal(num) or
            not np.isrealobj(num) or
            not np.isscalar(num)):
        return False
    else:
        return True


def is_real_array(array):
    '''
    Check if a value is a list or array of real scalars by aggregating several
    numpy checks.

    Parameters
    ----------
    array: any type
        The parameter to check

    Returns
    ------
    check : bool
        True if ```array``` is a list or array of a real scalars, False
        otherwise.

    '''

    if not (type(array) is list or type(array) is np.ndarray):
        return False
    else:
        if (not np.all([np.isreal(x) for x in array]) or
                not np.isrealobj(array) or
                not np.asarray(list(map(np.isscalar, array))).all()):
            return False
        else:
            return True



def wrap_number(x, x_min, x_max):
    '''
    Return the resulting value of wrapping the number in the range [x_min, x_max)

    Parameters
    ----------
    x: Number
        The nunber to wrap
    x_min: Number
        The minimum value of the range (included)
    x_max: Number
        The maximum value of the range (not included)

    Returns
    -------
    wrap: Number
        The wrapped number

    Raises
    ------
    AmbiScaperError
        If the arguments are not valid numbers, or if min is greater than max

    '''
    if (not isinstance(x, Number)
        or not isinstance(x_min, Number)
        or not isinstance(x_max, Number)):
        raise AmbiScaperError(
            'Error wrapping number: not a number, got ' + str(type(x)))
    if (x_min > x_max):
        raise AmbiScaperError(
            'Error wrapping number: min greater than max'
        )

    return (((x - x_min) % (x_max - x_min)) + (x_max - x_min)) % (x_max - x_min) + x_min



def delta_kronecker(q1,q2):
    '''
    Return 1 if q1==q2, 0 otherwise
    see https://en.wikipedia.org/wiki/Kronecker_delta

    Parameters
    ----------
    q1: int
        First number
    q2: int
        Second number

    Returns
    -------
    delta: int
        The Kronecker delta evaluated on the arguments

    Raises
    ------
    AmbiScaperError
        If the arguments are not valid numbers

    '''
    if (not isinstance(q1, int)
        or not isinstance(q2, int)):
        raise AmbiScaperError(
            'Error on Kronecker delta: argument not int')

    if (q1==q2): return 1
    else:        return 0


def cartesian_to_spherical(cartesian_list):
    '''
    Performs conversion from cartesian to spherical coordinates (in radians), with the following reference system:

        - azimuth 0: +x axis
        - elevation 0: horizontal plane ()
        - +y axis: azimuth pi/2
        - +x axis: elevation pi/2

    :param cartesian_list: List of 3 floats or ndarray(3), in the form ``[x,y,z]``.

    :returns: List of 3 floats, in the form ``[azimuth, elevation, radius]``. (in radians)

    :raises: AmbiScaperError. If the input argument does not match the required type
    '''

    def _validate_args(list_arg):
        if not isinstance(list_arg,list) and not isinstance(list_arg,np.ndarray):
            raise AmbiScaperError(
                'Error on Cartesian to Spherical conversion: argument not a list, given ' + str(type(list_arg)) + str(list_arg))
        if len(list_arg) is not 3:
            raise AmbiScaperError(
                'Error on Cartesian to Spherical conversion: argument should have lenght of 3, given' + str(list_arg))
        if not any([isinstance(f,float) for f in list_arg]):
            raise AmbiScaperError(
                'Error on Cartesian to Spherical conversion: argument should contain floats, given' + str(list_arg))

    _validate_args(cartesian_list)

    # Perform actual conversion
    x = cartesian_list[0]
    y = cartesian_list[1]
    z = cartesian_list[2]

    r = np.sqrt((x*x)+(y*y)+(z*z))
    azimuth = np.arctan2(y,x)
    elevation = np.arcsin((z/r))

    return [azimuth,elevation,r]

def cartesian_to_spherical_degree(cartesian_list):
    '''
    Performs conversion from cartesian to spherical coordinates (in degrees), with the following reference system:

        - azimuth 0: +x axis
        - elevation 0: horizontal plane ()
        - +y axis: azimuth 90
        - +x axis: elevation 90

    :param cartesian_list: List of 3 floats or ndarray(3), in the form ``[x,y,z]``.

    :returns: List of 3 floats, in the form ``[azimuth, elevation, radius]``. (in degrees)

    :raises: AmbiScaperError. If the input argument does not match the required type
    '''

    spherical = cartesian_to_spherical(cartesian_list)
    spherical[0] = radian_to_degree(spherical[0])
    spherical[1] = radian_to_degree(spherical[1])
    return spherical

def spherical_degree_to_cartesian(spherical_list):
    '''
    Performs conversion from spherical (degrees) to cartesian coordinates, with the following reference system:

        - azimuth 0: +x axis
        - elevation 0: horizontal plane ()
        - +y axis: azimuth pi/2
        - +x axis: elevation pi/2

    :param spherical_list: List of 3 floats, in the form ``[azimuth, elevation, radius]``. (in degrees)

    :returns: List of 3 floats or ndarray(3), in the form ``[x,y,z]``.

    :raises: AmbiScaperError. If the input argument does not match the required type
    '''

    spherical_list[0] = degree_to_radian(spherical_list[0])
    spherical_list[1] = degree_to_radian(spherical_list[1])

    cartesian = spherical_to_cartesian(spherical_list)
    return cartesian

def spherical_to_cartesian(spherical_list):
    '''
    Performs conversion from spherical (radians) to cartesian coordinates, with the following reference system:

        - azimuth 0: +x axis
        - elevation 0: horizontal plane ()
        - +y axis: azimuth pi/2
        - +x axis: elevation pi/2

    :param spherical_list: List of 3 floats, in the form ``[azimuth, elevation, radius]``. (in radians)

    :returns: List of 3 floats or ndarray(3), in the form ``[x,y,z]``.

    :raises: AmbiScaperError. If the input argument does not match the required type
    '''

    # Both arguments should be lists of 3 floats
    def _validate_args(list_arg):
        if not isinstance(list_arg, list) and not isinstance(list_arg, np.ndarray):
            raise AmbiScaperError(
                'Error on Spherical to Cartesian conversion: argument not a list, given ' + str(type(list_arg)) + str(list_arg))
        if len(list_arg) is not 3:
            raise AmbiScaperError(
                'Error on Spherical to Cartesian conversion: argument should have lenght of 3, given ' + str(list_arg))
        if not any([isinstance(f,float) for f in list_arg]):
            raise AmbiScaperError(
                'Error on Spherical to Cartesian conversion: argument should contain floats, given ' + str(list_arg))

    _validate_args(spherical_list)

    # Perform actual conversion
    azi = spherical_list[0]
    ele = spherical_list[1]
    r = spherical_list[2]

    x = r * np.cos(ele) * np.cos(azi)
    y = r * np.cos(ele) * np.sin(azi)
    z = r * np.sin(ele)

    return [x,y,z]


def degree_to_radian(degree):
    """

    :param degree:
    :return:
    """
    return degree * 2 * np.pi / 360.


def radian_to_degree(rad):
    """

    :param degree:
    :return:
    """
    return rad * 360 / (2 * np.pi)


def find_element_in_list(element, list_arg):
    '''
    Check if a given element is found in a given list.
    Returns the first occurrence of the object in the list, or None if not found.
    Very similar to list.index(), but does not return Error if not found
    (kinda more convenient sometimes)

    Parameters
    ----------
    element: any type
        The element to find
    list_arg: list type
        The list where to search the element

    Returns
    ------
    value : int or None
        Index of the first occurrence of the element in the list,
        or None if not found

    '''

    # element might have any kind of type,
    # but list_element must be a list
    if not isinstance(list_arg,list):
        raise AmbiScaperError(
            'Error on find(): second argument not a list, given' + str(list_arg))

    try:
        index_element = list_arg.index(element)
        return index_element
    except ValueError:
        return None


# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def find_closest_spherical_point(point,list_of_points,criterium='azimuth'):

    '''
    :param point:
    :param list_of_points:
    :return:
    '''

    if not isinstance(point,list):
        raise AmbiScaperError(
            'Error on find_closest_spherical_point(): fist argument not a list, given' + str(point))
    elif len(point) != 2:
        raise AmbiScaperError(
            'Error on find_closest_spherical_point(): fist argument size != 2, given' + str(point))

    if not isinstance(list_of_points,np.ndarray):
        raise AmbiScaperError(
            'Error on find_closest_spherical_point(): second argument not an array, given' + str(list_of_points))
    elif not all(isinstance(v,np.ndarray) for v in list_of_points):
        raise AmbiScaperError(
            'Error on find_closest_spherical_point(): second argument not an array of arrays, given' + str(list_of_points))
    elif not all(len(v) == 3 for v in list_of_points):
        raise AmbiScaperError(
            'Error on find_closest_spherical_point(): second argument not an array of arrays of len 3, given' + str(list_of_points))

    if criterium not in ['azimuth','elevation','surface']:
        raise AmbiScaperError(
            'Error on find_closest_spherical_point(): criterium not known, given' + criterium)


    # Let's define the geometry with azi between 0 and 2pi

    azi = float(wrap_number(point[0],0,2*np.pi))
    ele = float(wrap_number(point[1],-1*np.pi/2,np.pi/2))

    list_of_distances = []
    for p in list_of_points:

        # TODO: this will probably fail if M != 1
        p_azi = p[0][0]
        p_ele = p[1][0]
        target_azi = float(wrap_number(p_azi,0,2*np.pi))
        target_ele = float(wrap_number(p_ele,-1*np.pi/2,np.pi/2))

        # Closer in azimuth
        if criterium is 'azimuth':
            dist = np.abs(azi - target_azi)
            dist = min(dist, (2 * np.pi) - dist) # Because azimuth is periodic every 2pi

        elif criterium is 'elevation':
            dist = np.abs(ele - target_ele)

        elif criterium is 'surface': # both angles
            dist_azi = np.abs(azi - target_azi)
            dist_azi = min(dist_azi, (2 * np.pi) - dist_azi)  # Because azimuth is periodic every 2pi
            dist_ele = np.abs(ele - target_ele)
            # kinda euclidean distance from angles
            dist = np.sqrt(pow(dist_azi,2)+pow(dist_ele,2))

        list_of_distances.append(dist)

    index_of_min_distance = list_of_distances.index(min(list_of_distances))
    return (index_of_min_distance)


# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: REWRITE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



def _generate_event_id_from_idx(event_idx,role):
    '''
    Given an event_idx (an integer),
    generate the event identifier string (event_id)
    by appending the corresponding role label

    Parameters
    ----------
    :param event_idx: integer
    :param role: 'foreground' or 'background'

    Returns
    ------
    The correctly formed event_id string

    Raises
    ------
    AmbiScaperError
        If the input arguments does not match the required types

    '''

    if role is 'foreground':
        substring = event_foreground_id_string
    elif role is 'background':
        substring = event_background_id_string
    else:
        raise AmbiScaperError(
            'event role not known'+role
        )

    if not isinstance(event_idx,int):
        raise AmbiScaperError(
            'event_idx not an integer: ' + str(type(event_idx))
        )
    elif event_idx < 0:
        raise AmbiScaperError(
            'event_idx must be positive: ' + str(event_idx)
        )

    return substring+str(event_idx)


def _get_event_idx_from_id(event_id,role):
    '''
    Given an event_id (a string),
    generate the event index (event_id)
    by appending the corresponding role label

    Parameters
    ----------
    :param event_id: string
    :param role: 'foreground' or 'background'

    Returns
    ------
    The associated event index (event_idx)

    Raises
    ------
    AmbiScaperError
        If the input arguments does not match the required types and formats

    '''

    if role is 'foreground':
        substring = event_foreground_id_string
    elif role is 'background':
        substring = event_background_id_string
    else:
        raise AmbiScaperError(
            'event role not known'+role
        )

    if not isinstance(event_id,str):
        raise AmbiScaperError(
            'event_id not a string: ' + str(type(event_id))
        )

    # Remove role substring and get the integer number
    idx = event_id.replace(substring,"")

    # If didn't found (incorrect id), then idx will be equal to event_id
    if idx == event_id:
        raise AmbiScaperError(
            'Malformed event_id: ' + event_id
        )

    try:
        return int(idx)
    except ValueError:
        raise AmbiScaperError(
            'Malformed event_id: ' + event_id
        )



## TODO: COPYED FROM CORE TO AVOID CIRCULAR DEPENDENCIES

SUPPORTED_DIST = {"const": lambda x: x,
                  "choose": lambda x: scipy.random.choice(x),
                  "uniform": random.uniform,
                  "normal": random.normalvariate,
                  "truncnorm": _trunc_norm}

def _validate_distribution(dist_tuple):
    '''
    Check whether a tuple specifying a parameter distribution has a valid
    format, if not raise an error.

    Parameters
    ----------
    dist_tuple : tuple
        Tuple specifying a distribution to sample from. See AmbiScaper.add_event
        for details about the expected format of the tuple and allowed values.

    Raises
    ------
    AmbiScaperError
        If the tuple does not have a valid format.

    See Also
    --------
    AmbiScaper.add_event : Add a foreground sound event to the foreground
    specification.
    '''
    # Make sure it's a tuple
    if not isinstance(dist_tuple, tuple):
        raise AmbiScaperError('Distribution tuple must be of type tuple.')

    # Make sure the tuple contains at least 2 items
    if len(dist_tuple) < 2:
        raise AmbiScaperError('Distribution tuple must be at least of length 2.')

    # Make sure the first item is one of the supported distribution names
    if dist_tuple[0] not in SUPPORTED_DIST.keys():
        raise AmbiScaperError(
            "Unsupported distribution name: {:s}".format(dist_tuple[0]))

    # If it's a constant distribution, tuple must be of length 2
    if dist_tuple[0] == 'const':
        if len(dist_tuple) != 2:
            raise AmbiScaperError('"const" distribution tuple must be of length 2')
    # If it's a choose, tuple must be of length 2 and second item of type list
    elif dist_tuple[0] == 'choose':
        if len(dist_tuple) != 2 or not isinstance(dist_tuple[1], list):
            raise AmbiScaperError(
                'The "choose" distribution tuple must be of length 2 where '
                'the second item is a list.')
    # If it's a uniform distribution, tuple must be of length 3, 2nd item must
    # be a real number and 3rd item must be real and greater/equal to the 2nd.
    elif dist_tuple[0] == 'uniform':
        if (len(dist_tuple) != 3 or
                not is_real_number(dist_tuple[1]) or
                not is_real_number(dist_tuple[2]) or
                    dist_tuple[1] > dist_tuple[2]):
            raise AmbiScaperError(
                'The "uniform" distribution tuple be of length 2, where the '
                '2nd item is a real number and the 3rd item is a real number '
                'and greater/equal to the 2nd item.')
    # If it's a normal distribution, tuple must be of length 3, 2nd item must
    # be a real number and 3rd item must be a non-negative real
    elif dist_tuple[0] == 'normal':
        if (len(dist_tuple) != 3 or
                not is_real_number(dist_tuple[1]) or
                not is_real_number(dist_tuple[2]) or
                    dist_tuple[2] < 0):
            raise AmbiScaperError(
                'The "normal" distribution tuple must be of length 3, where '
                'the 2nd item (mean) is a real number and the 3rd item (std '
                'dev) is real and non-negative.')
    elif dist_tuple[0] == 'truncnorm':
        if (len(dist_tuple) != 5 or
                not is_real_number(dist_tuple[1]) or
                not is_real_number(dist_tuple[2]) or
                not is_real_number(dist_tuple[3]) or
                not is_real_number(dist_tuple[4]) or
                    dist_tuple[2] < 0 or
                    dist_tuple[4] < dist_tuple[3]):
            raise AmbiScaperError(
                'The "truncnorm" distribution tuple must be of length 5, '
                'where the 2nd item (mean) is a real number, the 3rd item '
                '(std dev) is real and non-negative, the 4th item (trunc_min) '
                'is a real number and the 5th item (trun_max) is a real '
                'number that is equal to or greater than trunc_min.')



def find_onset(ndarray,th=1e-4):
    '''
    Find the onset in samples of a given signal

    :param ndarray: 1d array
    :param th: level threshold
    :return: the onset's sample index, or None if no onset found
    :raises: AmbiScaper error if args not correct
    '''
    if not isinstance(ndarray,np.ndarray):
        raise AmbiScaperError('find_onset: arg not a ndarray')
    elif ndarray.ndim != 1:
        raise AmbiScaperError('find_onset: arg not a 1d-ndarray')
    elif not isinstance(th,float):
        raise AmbiScaperError('find_onset: th not a float')

    onset = None
    for i in range(ndarray.size):
        if ndarray[i] >= th:
            onset = i
            break

    return onset

def find_offset(ndarray,th=1e-4):
    '''
    Find the offset in samples of a given signal

    :param th: level threshold
    :return: the offset's sample index, or None if no onset found
    :raises: AmbiScaper error if args not correct
    '''

    if not isinstance(ndarray,np.ndarray):
        raise AmbiScaperError('find_onset: arg not a ndarray')
    elif ndarray.ndim != 1:
        raise AmbiScaperError('find_onset: arg not a 1d-ndarray')
    elif not isinstance(th,float):
        raise AmbiScaperError('find_onset: th not a float')

    offset = None
    # Decreasing range
    for i in range(ndarray.size-1,-1,-1):
        if ndarray[i] >= th:
            offset = i
            break

    return offset


def normalize_ir(ndarray, max=1):
    """
    :param ndarray:
    :param max:
    :return:
    """
    peak_value = np.amax(np.absolute(ndarray))
    k = max / peak_value
    return ndarray*k