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

    # Example 1: Foreground and background
    # ------------------------------------

    from ambiscaper import *
    import os

    # AmbiScaper settings
    soundscape_duration = 5.0
    ambisonics_order = 1

    # We want to use the full samples folder as potential events
    samples_folder = '../../samples/Handel_Trumpet'

    ### Create an ambiscaper instance
    ambiscaper = AmbiScaper(duration=soundscape_duration,
                            ambisonics_order=ambisonics_order,
                            fg_path=samples_folder,
                            bg_path=samples_folder)

    # Configure reference noise floor level
    ambiscaper.ref_db = -30

    ### Add a background event

    # Background events, by definition, have maximum spread
    # That means that they will only contain energy in the W channel (the first one)
    ambiscaper.add_background(source_file=('const', 'tr-1788d-piece4-sl.wav'),
                              source_time=('const', 5.))

    ### Add an event
    ambiscaper.add_event(source_file=('const', 'tr-1888d-high.wav'),
                         source_time=('const', 0),
                         event_time=('const', 0),
                         event_duration=('const', soundscape_duration),
                         event_azimuth=('const', 0),
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

    # Example 2: 15th order, variable spread Ambisonics soundscape
    # -------------------------------------------------------------

    from ambiscaper import *
    import numpy as np
    import os

    # AmbiScaper settings
    soundscape_duration = 10.0
    ambisonics_order = 15
    ambisonics_spread_slope = 0.25 # soft curve

    # We want to use the full samples folder as potential events
    samples_folder = os.path.abspath('../../samples/')

    ### Create an ambiscaper instance
    ambiscaper = AmbiScaper(duration=soundscape_duration,
                            ambisonics_order=ambisonics_order,
                            fg_path=samples_folder)

    # Make everything a little bit softer to avoid clipping
    ambiscaper.ref_db = -40
    ambiscaper.ambisonics_spread_slope = ambisonics_spread_slope

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


Example 3: Reverberant soundscape from recorded SOFA Ambisonics IRs
-------------------------------------------------------------------

So far we have been considering the anechoic case, which is great, but unfortunately not very realistic.
Reverberation is present in almost all acoustic environments, and most state-of-the-art algorithms
for Blind Source Separation and Source Localization consider the reverberant case.
Apart from the more scientifical approach, reverberant soundscapes sound very nice!

In this example we will use `sala1.sofa`, which is a nice reverb shipped with AmbiScaper.
It corresponds to an acoustic measurement of an exhibition room in the Fundacio Miro, Barcelona.
This file is part of the `Ambisonics Room Impulse Responses dataset <https://zenodo.org/record/1417727#.W5uO2pMzZ24>`_.

Reverberation is captured through `Impulse Responses (IRs) <https://en.wikipedia.org/wiki/Impulse_response>`_.
In this particular case, we are using *Ambisonics IRs*, wich are IRs recorded with an Ambisonics microphone,
thus capturing the spatial cues of the reverberation. It should be noticed that reverberation is variable along a room,
in the sense that it depends on both the position of the emitter and the receiver.
Since it would be impossible to record every possible pair of emitter/receiver positions, a spatial sampling strategie must be designed.
The implication for the soundscape generation is that we can only provide IRs from the actual measured emitter points,
and with a limited spatial resolution (the Ambisonics order of the microphone used).

The `SOFA conventions <www.sofaconventions.org>`_ conform a file description standard, intended for storing Impulse Responses
from different measurement setups. The author has participated in the design of a SOFA convention for Ambisonics IRs,
the *AmbisonicsDRIRconvention* (please refer to [Perez2018]_ for more information).
AmbiScaper uses SOFA files through the `pysofaconventions <https://andresperezlopez.github.io/pysofaconventions/>`_ library,
which is automatically installed with pip as a dependence.
Therefore, all specific SOFA details remain hidden to the user.


In the following example, we define ``ambisonics_order = 2``.
However, since we are using a recorded reverb spec of order 1, the system will automatically
downgrade the Ambisonics order to match the common minimum.

Furthermore, the source positions will be limited to the ones provided by the ``'Foyer'`` measurements.
How AmbiScaper select the final source positions due to this constrain is selected through the ``wrap`` argument
inside ``add_sofa_reverb()`` method. There are different options:

    *  ``wrap_azimuth``: source position assigned to the closest speaker position in azimuth
    *  ``wrap_elevation``: source position assigned to the closest speaker position in azimuth
    *  ``wrap_surface``: source position assigned to the closest speaker position around the spherical surface
    *  ``random``: source position assigned randomly to one of the available speaker positions

Please note that the reverb is as well specified in terms of distribution tuples, reusing the logic for the sound events,
and allowing for a very flexible dataset creation. Only one reverb type might be specified per soundscape, *i.e.*,
per each time the ``generate()`` method is called.


.. code-block:: python

    # Example 3: Reverberant soundscape from recorded SOFA Ambisonics IRs
    # -------------------------------------------------------------------

    from ambiscaper import *
    import numpy as np
    import os

    # AmbiScaper settings
    soundscape_duration = 5.0
    ambisonics_order = 2
    samples_folder = '../../samples/Bicycle_Horn'

    ### Create an ambiscaper instance
    ambiscaper = AmbiScaper(duration=soundscape_duration,
                            ambisonics_order=ambisonics_order,
                            fg_path=samples_folder)

    num_events = 2
    for event_idx in range(num_events):
        ### Add an event
        ambiscaper.add_event(source_file=('choose', []),
                             source_time=('uniform', 0, soundscape_duration),
                             event_time=('uniform', 0, soundscape_duration),
                             event_duration=('const', soundscape_duration),
                             event_azimuth=('uniform', 0, 2 * np.pi),
                             event_elevation=('uniform', -np.pi / 2, np.pi / 2),
                             event_spread=('uniform', 0, 1),
                             snr=('uniform', 0, 10),
                             pitch_shift=('const', 1),
                             time_stretch=('const', 1))

    # Set the path to the SOFA reverbs
    ambiscaper.set_sofa_reverb_folder_path('../../SOFA')

    # Add a recorded reverb
    ambiscaper.add_sofa_reverb(name=('const', 'sala1.sofa'),
                               wrap=('const', 'wrap_azimuth'))

    ### Genereate the audio and the annotation
    outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
    destination_path = os.path.join(outfolder, "example3")

    ambiscaper.generate(destination_path=destination_path,
                        generate_txt=True,
                        allow_repeated_source=True)

Please notice the warning message:

    ``AmbiScaperWarning: User-defined Ambisonics order L=2 is higher than the maximum order allowed by the reverb spec. Downgrading to 1 AmbiScaperWarning)``.

The last remark is about the IRs. In order to be useful to dereverberation/reverb estimation applications,
the actual IRs used are copied into the output */source/* folder, together with the source files.
The name of the file corresponds to the ``event_id`` parameter for each source: for example, source 0,
which is named ``fg0.wav``, will have a corresponding ``h0.wav`` file, and so on.


Example 4: Reverberant soundscape from simulated Ambisonics IRs
---------------------------------------------------------------

.. note::

    SIMULATED REVERBS ARE STILL IN DEVELOPMENT!!


AmbiScaper provides the option to use simulated IRs to create synthetic reverberant sound scapes.
This option might be useful in the cases in which it is not possible to record IRs, due to
limitations on equipment, permissions or whaterver other reason.
It is as well indicated for parametric analysis (for example, how is the performance of my BSS algorithm
as a function on t60?).

The simulated reverbs are computed through the wonderful
`SMIR Generator <https://www.audiolabs-erlangen.de/fau/professor/habets/software/smir-generator>`_,
a Matlab library intended for simulation of IRs on a spherical surface (as for example an Ambisonics Microphone),
inside a *shoebox* room model.
For a more detailed explanation, please refer to [Jarrett2012]_.

.. note::

    Please, notice that SMIR Generator is implemented in Matlab, and therefore a valid Matlab installation
    is needed in order to run the program.

When the simulated reverb is specified, AmbiScaper will internally launch a background Matlab sesssion,
which will execute the required computation. When finished, the resulting data will be transferred back to
AmbiScaper, and the Matlab session will be automatically closed. All this process remains hidden for the user.

Please, take into account that IR simulation is a computationally expensive process, and the computation time
will increase exponentially with the Ambisonics order.

As a result of AmbiScaper's ``generate()`` method, the computed IRs will be available at the */source/* folder.
AmbiScaper provides thus a way to create databases of Ambisonics IRs, defined in statistical terms.

SMIR Generator is a very flexible tool and, consequently, many parameters might be tuned for the IR computation.
AmbiScaper exposes a subset of the most relevant ones, described as distribution tuples,
in the ``add_simulated_reverb()`` method:

    * ``IRlength``: length in samples of the desired IRs
    * ``room_dimensions``: specified in meters, in the format *[x,y,z]*
    * ``t60``: reverberation time at 1 kHz, in seconds
    * ``source_type``: source directionality, can be choosen between:
        * 'o': omnidirectional
        * 'c': cardioid
        * 's': subcardioid
        * 'h': hypercardioid
        * 'b': bidirectional
    * ``microphone_type``: AmbiScaper features some predefined virtual microphone geometries:
        * 'soundfield'
        * 'tetramic'
        * 'em32'

.. note::

    It is possible, as well, to define the wall ``reflectivity``, specified for each one of the walls.
    However, it is not possible to define both ``t60`` and ``reflectivity`` at the same time, for obvious reasons.
    In that case, ``t60`` will be preferent.

By default, the virtual microphone will be placed at the center of the room, and thus the source
position is defined with respect to that center.


In Example 4, we will create a file consisting of a trumpet recording in a synthetic reverberant environment,
virtually captured with a Soundfield microphone.

.. code-block:: python

    ### EXAMPLE 4

    import ambiscaper
    import numpy as np
    import os

    # AmbiScaper settings
    soundscape_duration = 5.0
    ambisonics_order = 1
    samples_folder = os.path.abspath('./samples/Handel_Trumpet')

    ### Create an ambiscaper instance
    ambiscaper = ambiscaper.AmbiScaper(duration=soundscape_duration,
                                       ambisonics_order=ambisonics_order,
                                       fg_path=samples_folder)


    ### Add an event
    ambiscaper.add_event(source_file=('choose',[]),
                         source_time=('uniform', 0, soundscape_duration),
                         event_time=('uniform', 0, soundscape_duration),
                         event_duration=('const', soundscape_duration),
                         event_azimuth=('const',0),
                         event_elevation=('const',0),
                         event_spread=('const',0.5),
                         snr=('uniform', 0, 10),
                         pitch_shift=('const', 1),
                         time_stretch=('const', 1))

    # Add Simulated Reverb
    ambiscaper.add_simulated_reverb(IRlength=('const', 2048),                  # in samples
                                    room_dimensions=('const', [3,3,2]),         # [x,y,z]
                                    t60=('const', 0.2),                         # in seconds
                                    source_type=('const', 'o'),                 # omnidirectional
                                    microphone_type=('const', 'soundfield'))    # order 1


    ### Genereate the audio and the annotation
    outfolder = '/Volumes/Dinge/ambiscaper/testing/'  # watch out! outfolder must exist
    destination_path = os.path.join(outfolder, "example4")

    ambiscaper.generate(destination_path=destination_path,
                        generate_txt=True,
                        allow_repeated_source=True)

.. [Carpentier2017] Carpentier, T. (2017, May).
    Ambisonic spatial blur.
    In Audio Engineering Society Convention 142. Audio Engineering Society.

.. [Perez2018]
    Perez-Lopez, A. and de Muynke, J, (2018)
    "Ambisonics Directional Room Impulse Response as a New Convention of the Spatially Oriented Format for Acoustics",http://www.aes.org/e-lib/browse.cfm?elib=19560

.. [Jarrett2012]
    D. P. Jarrett, E. A. P. Habets, M. R. P. Thomas and P. A. Naylor,
    "Rigid sphere room impulse response simulation: algorithm and applications,"
    Journal of the Acoustical Society of America, Volume 132, Issue 3, pp. 1462-1472, 2012.