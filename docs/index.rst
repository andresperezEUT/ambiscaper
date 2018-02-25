.. ambiscaper documentation master file, created by
   sphinx-quickstart on Sun Feb 25 17:42:51 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ambiscaper's documentation!
======================================

Ambiscaper: a tool for automatic dataset generation and annotation of reverberant Ambisonics audio.

Originally forked from http://github.com/justinsalamon/scaper

Motivation
----------

Due to the recent developments on the field of immersive media and virtual reality, there has been a renewed interest into Ambisonics, specially motivated by its potential to capture the spacial qualities of the sound, and the methodologies to dynamically render it to binaural.

Despite the common approach to Ambisonics recordings as "ambiences", some modern Ambisonics microphones feature dozens of capsules. Therefore, it is possible to use such microphones as beamforming devices, with an accurate spatial resolution.

As a consequence, Ambisonics recordings might be useful in the auditory scene analysis field. More specifically, the intrinsic spatial audio representation can be exploited in the Sound Source Localization and Blind Source Separation fields.

However, there is an important lack of Ambisonics recordings databases, specially in the case of Higher Order Ambisonics. Annotation is also needed to design, train and evaluate the algorithms. The related works presented in last years have used custom databases, which hinder experiment reproducibility. A flexible reverberation configuration is as well needed for the state-of-the-art methods. Manual recording and annotation of sound scenes on that scale would imply an excessive amount of work.

We present AmbiScaper, a python library for procedural creation and annotation of reverberant Ambisonics databases. The software is based on a related work by Justin Salamon (http://github.com/justinsalamon/scaper) in the context of scene recognition.


Contents
-------------
.. toctree::
   :maxdepth: 2
   :caption: Contents:


Installation
-------------
.. toctree::
   :maxdepth: 1

   installation


Getting started
---------------
.. toctree::
   :maxdepth: 1

   tutorial


Examples
--------
.. toctree::
   :maxdepth: 3

   examples

API Reference
-------------
.. toctree::
  :maxdepth: 3

  api

* :ref:`genindex`


Changes
-------
.. toctree::
 :maxdepth: 1

 changes

Contribute
----------
- `Issue tracker <http://github.com/andresperezlopez/ambiscaper/issues>`_
- `Source code <http://github.com/andresperezlopez/ambiscaper>`_
