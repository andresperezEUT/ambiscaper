.. _examples:

Examples
========

Example 1: Foreground and background
------------------------------------

In this example, we are instanciating one sound event on the front position (azimuth and elevation are ``0``),
and adding a background sound.

Background sources are implemented as completely diffused sources: internally, spread is set to ``1``.
Although this implementation is not accurate in physical terms, and therefore not rigorous
(for instance, not valid for Intensity Vector Statistics or parametric spatial audio analysis),
it is still a common approach in the scope of spatial audio reproduction and diffuse soundscape creation.

Also notice that most of the event specifications are not available (and relevant) for the background spec.
For example, ``azimuth`` and ``elevation`` are not relevant on this context, since a fully spread source should
come from *all* positions.

Lastly, please notice the ``ref_db`` and ``snr`` parameters.
Ambiscaper's instance ``ref_db`` refers to the "noise floor" of the scene.
The backgound event's reference level will be set to that value. By default it is set to ``-30`` dBs.
Accordingly, event's ``snr`` indicates the dBs above ``ref_db`` of the given event.
Loudness computation is performed in a psychoacoustic way through the `LKFS scale <https://en.wikipedia.org/wiki/LKFS>`_.

.. code-block:: python

    ### EXAMPLE 1

    import ambiscaper
    import os

    # AmbiScaper settings
    soundscape_duration = 5.0
    ambisonics_order = 1

    # We want to use the full samples folder as potential events
    samples_folder = os.path.abspath('./samples/Handel_Trumpet')

    ### Create an ambiscaper instance
    ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                       ambisonics_order=ambisonics_order,
                                       fg_path=samples_folder,
                                       bg_path=samples_folder)

    # Configure reference noise floor level
    ambiscaper.ref_db = -30

    ### Add a background event

    # Background events, by definition, have maximum spread
    # That means that they will only contain energy in the W channel (the first one)
    ambiscaper.add_background(source_file=('const','tr-1788d-piece4-sl.wav'),
                              source_time=('const', 5.))

    ### Add an event
    ambiscaper.add_event(source_file=('const','tr-1888d-high.wav'),
                         source_time=('const', 0),
                         event_time=('const', 0),
                         event_duration=('const', soundscape_duration),
                         event_azimuth=('const', 0 ),
                         event_elevation=('const', 0),
                         event_spread=('const', 0),
                         snr=('const', 10),
                         pitch_shift=('const', 1),
                         time_stretch=('const', 1)
                         )

    ### Genereate the audio and the annotation
    outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
    destination_path = os.path.join(outfolder, "example1")

    ambiscaper.generate(destination_path=destination_path,
                        generate_txt=True)


Example 2: 15th order, variable spread Ambisonics soundscape
-------------------------------------------------------------

We will create a **15th** (yes, fifteenth!) order ambisonics soundscape (256 channels),
consisting of 10 sound events, placed at random positions around the sphere,
with a small amount of spread. Furthermore, the parameter ``ambisonics_spread_slope`` is set to ``0.25``,
meaning a softer transition in ambisonics order downgrading (please refer to [Carpentier2017]_ for more information).

Importing *example2.txt* into Audacity might be helpful to understand the cacophony and the possibilities of AmbiScaper.

Also, it might be of interest to have a look into *example2.jams*, in order to understand how the file is organized,
and the possibilities for evaluation and experiment replication that it offers.

Finally, notice the ``allow_repeated_source=True`` argument in ``generate()``.
As its name implies, during event instanciation, it will not take into account that a given source has been already chosen.
Setting it to ``False`` might be useful in many cases, but then there is the risk of not having enough sources in the used database.


.. code-block:: python

    ### EXAMPLE 2

    import ambiscaper
    import numpy as np
    import os

    # AmbiScaper settings
    soundscape_duration = 10.0
    ambisonics_order = 15
    ambisonics_spread_slope = 0.25 # soft curve

    # We want to use the full samples folder as potential events
    samples_folder = os.path.abspath('./samples/')

    ### Create an ambiscaper instance
    ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                       ambisonics_order=ambisonics_order,
                                       fg_path=samples_folder,
                                       ambisonics_spread_slope=ambisonics_spread_slope)

    # Make everything a little bit softer to avoid clipping
    ambiscaper.ref_db = -40

    # add 10 events!
    num_events = 10
    for event_idx in range(num_events):
        ### Add an event
        ambiscaper.add_event(source_file=('choose',[]),
                             source_time=('uniform', 0, soundscape_duration),
                             event_time=('uniform', 0, soundscape_duration),
                             event_duration=('const', soundscape_duration),
                             event_azimuth=('uniform', 0, 2 * np.pi),
                             event_elevation=('uniform', -np.pi / 2, np.pi / 2),
                             event_spread=('truncnorm', 0.1, 0.2, 0.0, 0.5),
                             snr=('uniform', 0, 10),
                             pitch_shift=('uniform', -2, 2),
                             time_stretch=('uniform', 0.8, 1.2))

    ### Genereate the audio and the annotation
    outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
    destination_path = os.path.join(outfolder, "example2")

    ambiscaper.generate(destination_path=destination_path,
                        generate_txt=True,
                        allow_repeated_source=True)


Example 3: Reverberant soundscape from IR measurement
-----------------------------------------------------

So far we have been considering the anechoic case, which is great, but unfortunately not realistic.
Reverberation is present in almost all acoustic environments, and most state-of-the-art algorithms
for Blind Source Separation and Source Localization consider the reverberant case.
Apart from the more scientifical approach, reverberant soundscapes sound very nice!

In this example we will use the default reverbs shipped with AmbiScaper - they can be found under the */IRs/* folder.
Currently, there are five sets of measurements available, corresponding to 5 different rooms with diverse reverberation
characteristics, ranging from studio to church. All these reverbs come from the great research at Surrey,
Salford and Southampton Universities, and from BBC.
Please refer to [Coleman2015]_ for more information.

Reverberation is captured through `Impulse Responses (IRs) <https://en.wikipedia.org/wiki/Impulse_response>`_.
In this particular case, we are using *Ambisonics IRs*, wich are IRs recorded with an Ambisonics microphone,
thus capturing the spatial cues of the reverberation. It should be noticed that reverberation is variable along a room,
in the sense that it depends on both the position of the emitter and the receiver.
Since it would be impossible to record every possible pair of emitter/receiver positions, a spatial sampling strategie must be designed.

Therefore, the given IRs are the recordings at different emitter positions, while the receiver remains fix (usually at the room center).
The different speaker positions are specified in the ``LsPos.txt`` file.

.. note::

    We are working on a more compact, reliable and scalable way to store Ambisonics IRs,
    by means of the development of an ad-hoc `SOFA <https://www.sofaconventions.org>`_ convention.
    That means that the *IRs* folder structure might change in next releases.

The implication for the soundscape generation is that we can only provide IRs from the actual measured emitter points,
and with a limited spatial resolution (the Ambisonics order of the microphone used).

In the following example, we define ``ambisonics_order = 2``.
However, since we are defining a recorded reverb spec of order 1, ``'MainChurch'``, the system will automatically
downgrade the Ambisonics order to match the minimum.

Furthermore, the source positions will be limited to the ones provided by the ``'MainChurch'`` measurements.
How AmbiScaper select the final source positions due to this constrain is selected through the ``wrap`` argument
inside ``add_recorded_reverb()`` method. There are different options:

    *  ``wrap_azimuth``: source position assigned to the closest speaker position in azimuth
    *  ``wrap_elevation``: source position assigned to the closest speaker position in azimuth
    *  ``wrap_surface``: source position assigned to the closest speaker position around the spherical surface
    *  ``random``: source position assigned randomly to one of the available speaker positions


.. code-block:: python

    ### EXAMPLE 3

    import ambiscaper
    import numpy as np
    import os

    # AmbiScaper settings
    soundscape_duration = 5.0
    ambisonics_order = 2
    samples_folder = os.path.abspath('./samples/Bicycle_Horn')

    ### Create an ambiscaper instance
    ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                       ambisonics_order=ambisonics_order,
                                       fg_path=samples_folder)

    num_events = 2
    for event_idx in range(num_events):
        ### Add an event
        ambiscaper.add_event(source_file=('choose',[]),
                             source_time=('uniform', 0, soundscape_duration),
                             event_time=('uniform', 0, soundscape_duration),
                             event_duration=('const', soundscape_duration),
                             event_azimuth=('uniform', 0, 2 * np.pi),
                             event_elevation=('uniform', -np.pi / 2, np.pi / 2),
                             event_spread=('uniform',0 ,1),
                             snr=('uniform', 0, 10),
                             pitch_shift=('const', 1),
                             time_stretch=('const', 1))

    # Add reverb
    ambiscaper.add_recorded_reverb(name=('const','MainChurch'),
                                   wrap=('const','wrap_azimuth'))

    ### Genereate the audio and the annotation
    outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
    destination_path = os.path.join(outfolder, "example3")

    ambiscaper.generate(destination_path=destination_path,
                        generate_txt=True,
                        allow_repeated_source=True)

Please notice the warning message:

    ``AmbiScaperWarning: User-defined Ambisonics order L=2 is higher than the maximum order allowed by the reverb spec. Downgrading to 1 AmbiScaperWarning)``.


.. [Carpentier2017] Carpentier, T. (2017, May).
    Ambisonic spatial blur.
    In Audio Engineering Society Convention 142. Audio Engineering Society.

.. [Coleman2015]
 Coleman, P., Remaggi, L., and Jackson, PJB. (2015)
  "S3A Room Impulse Responses", http://dx.doi.org/10.15126/surreydata.00808465