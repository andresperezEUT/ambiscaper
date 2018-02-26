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
    * ``source_time`` (the time offset between the soundscape start and the event start) and ``event_time`` (the offset of the given source file itself) are set to ``0``. Furthermore, ``event_duration`` is set equal to the soundscape duration.
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

If everything went good so far, we will have the following structure under *my_first_ambisonics_soundscape*:

    *

Adding a background
~~~~~~~~~~~~~~~~~~~
Next, we can optionally add a background track to our soundscape:

.. code-block:: python


To add a background we have to specify:

* ``label``: the label (category) of background, which has to match the name of one
  of the subfolders in our background folder (in our example "park" or "street").
* ``source_file``: the path to the specific audio file to be used.
* ``source_time``: the time in the source file from which to start the background.

Note how in the example above we do not specify these values directly by providing
strings or floats, but rather we provide each arugment with a tuple. These tuples
are called **distribution tuples** and are used in scaper for specifying all sound
event parameters. Let's explain:

Distribution tuples
~~~~~~~~~~~~~~~~~~~
One of the powerful things about scaper is that it allows you to define a soundscape
in a probabilistic way. That is, rather than specifying constant (hard coded) values for each
sound event, you can specify a distribution of values to sample from. Later on,
when we call ``sc.generate()``, a soundscape will be "instantiated" by sampling a value
for each distribution tuple in each sound event (foreground and background). Every time
we call ``sc.generate()``, a new value will be sampled for each distribution tuple,
resulting in a different soundscape.

The distribution tuples currently supported by scaper are:

* ``('const', value)``: a constant, given by ``value``.
* ``('choose', list)``: uniformly sample from a finite set of values given by ``list``.
* ``('uniform', min, max)``: sample from a uniform distribution between ``min`` and ``max``.
* ``('normal', mean, std)``: sample from a normal distribution with mean ``mean`` and standard deviation ``std``.
* ``('truncnorm', mean, std, min, max)``: sample from a truncated normal distribution with mean ``mean`` and standard deviation ``std``,
  limited to values between ``min`` and ``max``.

Special cases: the ``label`` and ``source_file`` parameters in ``sc.add_background()``
(and as we'll see later ``sc.add_event()`` as well) must be specified using
either the ``const`` or ``choose`` distribution tuples. When using ``choose``, these
two parameters (and only these) can also accept a special version of the ``choose`` tuple
in the form ``('choose', [])``, i.e. with an empty list. In this case, scaper will
use the file structure in the foreground and background folders to automatically populate
the list with all valid labels (in the case of the ``label`` parameter) and all valid
filenames (in the case of the ``source_file`` parameter).

Adding a foreground sound event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Next, we can add foreground sound events. Let's add one to start with:

.. code-block:: python

    sc.add_event(label=('const', 'siren'),
                 source_file=('choose', []),
                 source_time=('const', 0),
                 event_time=('uniform', 0, 9),
                 event_duration=('truncnorm', 3, 1, 0.5, 5),
                 snr=('normal', 10, 3),
                 pitch_shift=('uniform', -2, 2),
                 time_stretch=('uniform', 0.8, 1.2))

A foreground sound event requires several additional parameters compared to a
background event. The full set of parameters is:

* ``label``: the label (category) of foreground event, which has to match the name of one
  of the subfolders in our foreground folder (in our example "siren", "car_honk" or "human_voice").
* ``source_file``: the path to the specific audio file to be used.
* ``source_time``: the time in the source file from which to start the event.
* ``event_time``: the start time of the event in the synthesized soundscape.
* ``event_duration``: the duration of the event in the synthesized soundscape.
* ``snr``: the signal-to-noise ratio (in LUFS) compared to the background. In other words,
  how many dB above or below the background should this sound event be percieved.

Scaper also supports on-the-fly augmentation of sound events, that is, applying audio
transformations to the sound events in order to increase the variability of the resulting soundscape.
Currently, the supported transformations include pitch shifting and time stretching:

* ``pitch_shift``: the number of semitones (can be fractional) by which to shift the sound up or down.
* ``time_stretch``: the factor by which to stretch the sound event. Factors <1
  will make the event shorter, and factors >1 will make it longer.

If you do not wish to apply any transformations, these latter two parameters
(and only these) also accept ``None`` instead of a distribution tuple.

So, going back to the example code above, we're adding a siren sound event,
the specific audio file to use will be chosen randomly from all available siren
audio files in the ``foreground/siren`` subfolder, the event will start at time
0 of the source file, and be "pasted" into the synthesized soundscape anywhere
between times 0 and 9 chosen uniformly. The event duration will be randomly
chosen from a truncated normal distribution with a mean of 3 seconds, standard
deviation of 1 second, and min/max values of 0.5 and 5 seconds respectively.
The loudness with respect to the background will be chosen from a normal
distribution with mean 10 dB and standard deviation of 3 dB. Finally, the pitch
of the sound event will be shifted by a value between -2 and 2 semitones
chosen uniformly within that range, and will be stretched (or condensed) by a
factor chosen uniformly between 0.8 and 1.2.

Let's add a couple more events:

.. code-block:: python

    for _ in range(2):
        sc.add_event(label=('choose', []),
                     source_file=('choose', []),
                     source_time=('const', 0),
                     event_time=('uniform', 0, 9),
                     event_duration=('truncnorm', 3, 1, 0.5, 5),
                     snr=('normal', 10, 3),
                     pitch_shift=None,
                     time_stretch=None)

Here we use a for loop to quickly add two sound events. The specific label and
source file for each event will be determined when we call ``sc.generate()``
(coming up), and will change with each call to this function.

Synthesizing soundscapes
------------------------
Up to this point, we have created a ``Scaper`` object and added a background and
three foreground sound events, whose parameters are specified using distribution
tuples. Internally, this creates an `event specification`, i.e. a
probabilistically-defined list of sound events. To synthesize a soundscape,
we call the ``generate()`` function:

.. code-block:: python

    audiofile = 'soundscape.wav'
    jamsfile = 'soundscape.jams'
    txtfile = 'soundscape.txt'
    sc.generate(audiofile, jamsfile,
                allow_repeated_label=True,
                allow_repeated_source=True,
                reverb=0.1,
                disable_sox_warnings=True,
                no_audio=False,
                txt_path=txtfile)

This will instantiate the event specification by sampling specific parameter
values for every sound event from the distribution tuples stored in the
specification. Once all parameter values have been sampled, they are used by
scaper's audio processing engine to compose the soundscape and save the
resulting audio to ``audiofile``.

But that's not where it ends! Scaper will also generate an annotation file in
`JAMS <https://github.com/marl/jams>`_ format which serves as the reference
annotation (also referred to as "ground truth") for the generated soundscape.
Due to the flexibility of the JAMS
format scaper will store in the JAMS file, in addition to the actual sound
events, the probabilistic event specification (one for background events and one
for foreground events). The ``value`` field of each observation in the JAMS file
will contain a dictionary with all instantiated parameter values. This allows
us to fully reconstruct the audio of a scaper soundscape from its JAMS annotation
using the ``scaper.generate_from_jams()`` function (not discussed in this tutorial).

Finally, we can optionally provide ``generate()`` a path to a text file
with the ``txt_path`` parameter. If provided, scaper will also save a simplified
annotation of the soundscape in a tab-separated text file with three columns
for the start time, end time, and label of every foreground sound event (note that
the background is not stored in the simplified annotation!). The default
separator is a tab, for compatibility with the `Audacity <http://www.audacityteam.org/>`_
label file format. The separator can be changed via ``generate()``'s ``txt_sep``
parameter.

That's it! For a more detailed example of automatically synthesizing 1000
soundscapes using a single ``Scaper`` object, please see the :ref:`examples`.


.. _differences:

Differences from Scaper
-----------------------
TODO
