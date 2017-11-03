'''
ambisonics.py

SN3D coefs
ACN ordering
up to 3rd order

from D. Malham, 'Higher order Ambisonic systems'
https://www.york.ac.uk/inst/mustech/3d_audio/higher_order_ambisonics.pdf
notice that phi and theta are switched from standard...

'''
import numpy as np
from math import sin, cos, sqrt
from scaper.scaper_exceptions import ScaperError
from numbers import Number

def _validate_ambisonics_order(order):

    if (order<0):
        raise ScaperError(
            'Ambisonics order must be bigger than 0')
    if (not isinstance(order,int)):
        raise ScaperError(
            'Ambisonics order must be an integer')


def get_number_of_ambisonics_channels(order):
    _validate_ambisonics_order(order)
    return pow(order+1,2)


def _validate_angle(angle):
    if (not isinstance(angle,Number)):
            raise ScaperError(
                'Ambisonics order must be bigger than 0')

def get_ambisonics_coefs(azimuth,elevation,order):

    _validate_angle(azimuth)
    _validate_angle(elevation)
    _validate_ambisonics_order(order)

    # azimuth and elevation values are fine as long as they are real numbers...

    coefs = np.zeros(get_number_of_ambisonics_channels(order))

    a = azimuth     # usually phi
    e = elevation   # usually theta

    if (order >= 0):
        coefs[0] = 1. # W

    if (order >= 1):
        coefs[1] = sin(a) * cos(e)    # Y
        coefs[2] = sin(e)             # Z
        coefs[3] = cos(a) * cos(e)    # X

    if (order >= 2):
        coefs[4] = (sqrt(3)/2.) * sin(2*a) * pow(cos(e),2)    # V
        coefs[5] = (sqrt(3)/2.) * sin(a) * sin(2*e)           # T
        coefs[6] = 0.5 * ( 3*pow(sin(e),2)-1 )                # R
        coefs[7] = (sqrt(3)/2.) * cos(a) * sin(2*e)           # S
        coefs[8] = (sqrt(3)/2.) * cos(2*a) * pow(cos(e),2)    # U

    if (order >= 3):
        coefs[9] = (sqrt(5./8.)) * sin(3*a) * pow(cos(e),3)                    # Q
        coefs[10] = (sqrt(15)/2.) * sin(2*a) * sin(e) * pow(cos(e),2)         # O
        coefs[11] = (sqrt(3./8.)) * sin(a) * cos(e) * (5*(pow(sin(e),2))-1)    # M
        coefs[12] = 0.5 * ( sin(e) * (5*(pow(sin(e),2))-3) )                  # K
        coefs[13] = (sqrt(3./8.)) * cos(a) * cos(e) * ((5*pow(sin(e),2))-1)    # L
        coefs[14] = (sqrt(15)/2.) * cos(2*a) * sin(e) * pow(cos(e),2)         # N
        coefs[15] = (sqrt(5./8.)) * cos(3*a) * pow(cos(e),3)                   # P

    return coefs