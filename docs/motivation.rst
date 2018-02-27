.. _motivation:

Motivation
==========

Due to the recent developments on the field of immersive media and virtual reality, there has been a renewed interest into Ambisonics, specially motivated by its potential to capture the spacial qualities of the sound, and the methodologies to dynamically render it to binaural.

Despite the common approach to Ambisonics recordings as "ambiences", some modern Ambisonics microphones feature dozens of capsules. Therefore, it is possible to use such microphones as beamforming devices, with an accurate spatial resolution.

As a consequence, Ambisonics recordings might be useful in the auditory scene analysis field. More specifically, the intrinsic spatial audio representation can be exploited in the Sound Source Localization and Blind Source Separation fields.

However, there is an important lack of Ambisonics recordings databases, specially in the case of Higher Order Ambisonics. Annotation is also needed to design, train and evaluate the algorithms. The related works presented in last years have used custom databases, which hinder experiment reproducibility. A flexible reverberation configuration is as well needed for the state-of-the-art methods. Manual recording and annotation of sound scenes on that scale would imply an excessive amount of work.

We present AmbiScaper, a python library for procedural creation and annotation of reverberant Ambisonics databases.

Acknowledgements
----------------

AmbiScaper is based on `Scaper <http://github.com/justinsalamon/scaper>`_, a related work by Justin Salamon in the context of scene recognition.

The material in the present documentation is as well highly inspired on the original Scaper documentation.

For a more detailed comparison, please refer to the :ref:`differences` section.