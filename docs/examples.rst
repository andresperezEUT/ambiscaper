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


Example 2: Fifth order, variable spread Ambisonics soundscape
-------------------------------------------------------------

We will create a 5th order ambisonics soundscape (36 channels),
consisting of 10 sound events, placed at random positions around the sphere,
with a small amount of spread. Furthermore, the parameter ``ambisonics_spread_slope`` is set to ``0.25``,
meaning a softer transition in ambisonics order downgrading (please refer to [Carpentier2017]_ for more information).

Importing *example2.txt* into Audacity might be helpful to understand the cacophony and the possibilities of AmbiScaper.

Also, it might be of interest to have a look into *example2.jams*, in order to understand how the file is organized,
and the possibilities for evaluation and experiment replication that it offers.



.. code-block:: python

    ### EXAMPLE 2

    import ambiscaper
    import numpy as np
    import os

    # AmbiScaper settings
    soundscape_duration = 10.0
    ambisonics_order = 5
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
                        generate_txt=True)




.. [Carpentier2017] Carpentier, T. (2017, May).
    Ambisonic spatial blur.
    In Audio Engineering Society Convention 142. Audio Engineering Society.