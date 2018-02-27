.. _tutorial:

AmbiScaper tutorial
===================

Welcome to the AmbiScaper tutorial!

Introduction
------------

AmbiScaper is a fantastic tool to create Ambisonics sound files (and corresponding annotations) in a procedural way.

Through this tutorial you will learn the basic features, and you will be ready to create amazing Ambisonics datasets.

Ambisonics?
~~~~~~~~~~~
`Ambisonics <https://en.wikipedia.org/wiki/Ambisonics>`_ is a spatial sound theory developed by Michael Gerzon in the 1970s, based on the acoustics and psychoacoustics fields.

On its most basic form, Ambisonics can be thought as a way to preserve the spatial characteristics of a soundfield.
This is based on the plane-wave decomposition of the sound by means of the `Spherical Harmonics Transform <https://en.wikipedia.org/wiki/Spherical_harmonics>`_ (aka the *Spatial Fourier Transform*).
Indeed, there are many parallels between the *spectral* Fourier transform and the *spacial* Fourier transform,
but for the moment it's enough to imagine the transform as a set of virtual microphones, each one pointing to one spatial direction.
This transformation, which is usually referred to as *Ambisonics Encoding*, produces a multichannel audio track which implicitly contains
the information about the source position(s). This kind of multichannel file is usually called *B-Format*.

Ambisonics audio cannot be played just as it is, but it neeeds to be *decoded*. The great thing about it is that it does not requiere
any specific speaker layout: it will adapt to any given speaker layout, provided a corresponding decoder. Furthermore, it is very easy
to render binaural audio from a *B-Format* recording, and this is one of the reasons why it is becoming so popular.

AmbiScaper produces *B-Format* synthetic recordings from a library of mono/stereo tracks. If you want to listen to them,
you will need some extra software, as for example the great `ambiX plugins suite <http://www.matthiaskronlachner.com/?p=2015>`_.

Ambisonics can be very useful as well in some research areas, such as Blind Source Separation and Sound Source Localization.
However, it is not easy to create an annotated dataset of Ambisonics audios, and specially with the separated tracks for the BSS evaluation.
This is the main motivation behind the development of AmbiScaper.
Of course, usages for other purposes, such as generative soundscape creation, are welcomed too.

Source Material
~~~~~~~~~~~~~~~

As we already mentioned, the raw material for the Ambisonics soundscape creation are individual audio clips, both mono or stereo.
These clips, ideally (semi)anechoic, must be present in your system.
You can use any sounds you like but, just in case, AmbiScaper features a selection of clips from the great `openAIRlib <http://www.openairlib.net>`_.
You can find them in the `AmbiScaper repository <http://andresperezlopez.com/ambiscaper>`_, under the *samples* folder.



Creating our first Ambisonics soundscape
----------------------------------------

AmbiScaper Instanciation
~~~~~~~~~~~~~~~~~~~~~~~~

The ``AmbiScaper`` class is the main object from the library.
Let's start by instanciating it:

.. code-block:: python

    import ambiscaper
    import numpy as np
    import os

    # AmbiScaper settings
    soundscape_duration = 5.0
    ambisonics_order = 1
    foreground_folder = os.path.abspath('./samples/Acoustics_Book')

    ### Create an ambiscaper instance
    ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                       ambisonics_order=ambisonics_order,
                                       fg_path=foreground_folder)

We are specifying three arguments to the AmbiScaper instance creation.

1. The desired soundscape duration.
2. The Ambisonics order to be used.
3. The path to the sound event folder (in this case, the *Acoustics_Book* samples shipped with the code).


Adding sound events
~~~~~~~~~~~~~~~~~~~

Once we have an instance of AmbiScaper, we can add audio clips (events) to be rendered.

One of the main features of AmbiScaper is that event parameters might be specified in terms of statistical distributions,
and not only as fixed values. For example:

.. code-block:: python

    ### Add an event
    ambiscaper.add_event(source_file=('choose', ['adult_female_speech.wav','bagpipe_music.wav']),
                         source_time=('const', 0),
                         event_time=('const', 0),
                         event_duration=('const', soundscape_duration),
                         event_azimuth=('uniform', 0, 2*np.pi),
                         event_elevation=('uniform', -np.pi/2, np.pi/2),
                         event_spread=('const', 0),
                         snr=('const', 0),
                         pitch_shift=('const', 1),
                         time_stretch=('const', 1)
                         )

As you can see, every parameter is defined in terms of a *distribution tuple*, i.e., a definition of the possible values
that the given parameter might take. The actual values, sampled from the distribution tuples, will be assigned at the
soundscape rendering stage (the ``generate()`` method).

The distribution tuples currently supported are:

    * ``('const', value)``: a constant, given by ``value``.
    * ``('choose', list)``: uniformly sample from a finite set of values given by ``list``.
    * ``('uniform', min, max)``: sample from a uniform distribution between ``min`` and ``max``.
    * ``('normal', mean, std)``: sample from a normal distribution with mean ``mean`` and standard deviation ``std``.
    * ``('truncnorm', mean, std, min, max)``: sample from a truncated normal distribution with mean ``mean`` and standard deviation ``std``,
      limited to values between ``min`` and ``max``.

Therefore, our ``add_event`` method is actually specifying the following:

    * ``source_file`` can take one of the two provided values: ``adult_female_speech.wav`` or ``bagpipe_music.wav``.
    * ``source_time`` (the time in the source file from which to start the event) and ``event_time`` (the start time of the event in the synthesized soundscape) are set to ``0``.
        Furthermore, ``event_duration`` is set equal to the soundscape duration.
    * ``event_azimuth`` and ``event_elevation``, the angles defining the event position, are set to take a random value, uniformly distributed in their value domain.
        Remember that *azimuth* is the angle in the horizontal plane starting from the X axis in counter-clockwise direction,
        and *elevation* is the angle perpendicular to the horizontal plane, being ``0`` the horizontal plane, ``pi/2`` above and ``-pi/2`` below.
    * ``event_spread`` is set to 0. The spread parameter can be thought as the apparent sound source width, with a value between ``0`` (no spread) and ``1`` (fully spread)
    * ``snr`` ``pitch_shift`` ``time_stretch`` are set with a constant value.

To summarize up, the ``add_event()`` method allows to tell AmbiScaper about an *event specification* with statistical
distribution values.

Soundscape generation
~~~~~~~~~~~~~~~~~~~~~

Once the sound events are described, we can proceed to actually generate the Ambisonics soundscape.

This is provided by the ``generate()`` method:

.. code-block:: python

    ### Genereate the audio and the annotation
    outfolder = '/Volumes/Dinge/ambiscaper/testing/' # watch out! outfolder must exist
    destination_path = os.path.join(outfolder,"my_first_ambisonics_soundscape")

    ambiscaper.generate(destination_path=destination_path,
                        generate_txt=True)

This piece of code will actually sample all values from the event specifications, in a process called *instanciation*,
and as a result will provide the rendered audio and the associated annotations.

If everything went good so far, we will have the following output structure:

    * /my_first_ambisonics_soundscape/
        * *my_first_ambisonics_soundscape.wav*
        * *my_first_ambisonics_soundscape.jams*
        * *my_first_ambisonics_soundscape.txt*
        * /Source/
            * *fg0.wav*

Let's exlain them briefly:

``my_first_ambisonics_soundscape.wav`` is the main audio output: an Ambisonics multichanel audio file
(in this case 4 channels, since we specified 1st Order Ambisonics), which contains the spatially encoded
representation of the audio source.
If you try to open the file with an audio editor
(we can recommend `Audacity <https://www.audacityteam.org/>`_ and `Ardour <https://ardour.org//>`_, which are open source, multichannel-friendly and cool),
you will appreciate that the different channels have the same audio content with different gains -
that's hos Ambisonics looks like. The duration of the audio file is 5 seconds, just as we specified.

.. note::
    Ambisonics Audios generated by AmbiScaper follow the conventions:

    *   Normalization: *SN3D*
    *   Channel ordering: *ACN*

``my_first_ambisonics_soundscape.jams`` is the annotation file, in the `JAMS <https://github.com/marl/jams>`_ format
(a JSON-based specification intended for Music Information Retrieval). It basically contains a bunch of information
related to the generated audio file: not only the actual instanciated values, but also the distribution tuples from the
event specification. This is great, since we can use this file not only for validation, but also for exact setup reproduction.

Try to open the file with any text editor or python IDE, and inspect a little bit the contents.
The instanciated values are under the ``data`` field, and you can check that they are consistent with the provided AmbiScaper arguments.
Another interesting part is located under the field ``fg_spec``, containing the given distribution tuples.

``my_first_ambisonics_soundscape.txt`` is a small plain text file, which contains some information about the generated soundscape.
More precisely, it includes one row for each sound event, and features three columns (separated by tabs): *start time*, *end time* and *event_id*.
Please notice that *event_id* is ``fg0``, which corresponds to the first foreground event.
A very handy usage of this text file is event duration visualization through Audacity (*File/Import/Labels..*).

.. note::
   ``event_id`` is the unique identifier for each sound event,
   assigned by AmbiScaperin the order given by the successive calls to ``add_event()``.

   *event_ids* are composed of the string ``fg`` and an index.
   The correspondence of each *event_id* with the actual source file name is defined in the ``data`` field of the JAMS file.

Inside the *source* folder, there will be just one file, ``fg0.wav``.
This is a copy of the original source file, which includes the modifications performed by AmbiScaper (time offset, gain correction, pitch shift, etc).
To put it in other words, it contains just the exact audio content before the Ambisonics encoding.
This file is very useful if you want to perform Source Separation evaluation tasks.



If you want to explore a litte bit more the capabilities of AmbiScaper, please refer to the :ref:`examples` section.


.. _differences:

Differences from Scaper
-----------------------

As already mentioned, AmbiScaper is (obviously) based on the great  `Scaper <http://github.com/justinsalamon/scaper>`_, by Justin Salamon.
More precisely, it was forked at 17th October 2017 from `commit e0cc1c9 <https://github.com/justinsalamon/scaper/commit/e0cc1c9701bb4bcd96a02cd1737c723d765dcd16>`_.

Scaper is a piece of software intended for automatic generation and annotation of monophonic soundscapes, in the context of
Auditory Scene Analysis, sound event recognition, etc. The parallelism with the Blind Source Separation problem is clear:
we need big datasets of annotated events, specially when dealing with Deep Neural Network architectures.

Forking such a project is a great idea, since all the nice features (event specification vs instanciation, jams file, etc)
are preserver. However, obviously, some changes must be performed in order to adapt the code to the Ambisonics domain.

In that sense, Scaper and AmbiScaper are not mutually compatible. That means that, in general, copying pieces of code from
one to the another won't work. The number of arguments to the methods, the default values, the namespaces, and many other
aspects have been changed and adapted to the new situation.

However, don't panic! The code structure is very similar and, if you already know how Scaper works, it will be very fast
to catch up with AmbiScaper.

