.. _api:

.. module:: ambiscaper

API Reference
------------------

.. automodule:: ambiscaper.core
    :members: generate_from_jams, trim

.. autoclass:: ambiscaper.core.AmbiScaper
    :members:

.. automodule:: ambiscaper.reverb_ambisonics
    :members: get_maximum_ambisonics_order_from_spec, retrieve_available_recorded_IRs, generate_sofa_file_full_path, retrieve_emitter_positions_spherical

.. autodata:: ambiscaper.reverb_ambisonics.SMIR_SUPPORTED_VIRTUAL_MICS
    :annotation:

.. autodata:: ambiscaper.reverb_ambisonics.SMIR_ALLOWED_SOURCE_TYPES
    :annotation:

.. automodule:: ambiscaper.util
    :members: cartesian_to_spherical, spherical_to_cartesian