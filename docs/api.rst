.. _api:

.. module:: ambiscaper

API Reference
------------------

.. automodule:: ambiscaper.core
    :members: generate_from_jams, trim

.. autoclass:: ambiscaper.core.AmbiScaper
    :members:

.. automodule:: ambiscaper.reverb_ambisonics
    :members: get_max_ambi_order_from_reverb_config, retrieve_available_recorded_IRs, generate_RIR_path, retrieve_RIR_positions_spherical

.. autodata:: ambiscaper.reverb_ambisonics.SMIR_SUPPORTED_VIRTUAL_MICS
    :annotation:

.. autodata:: ambiscaper.reverb_ambisonics.SMIR_ALLOWED_SOURCE_TYPES
    :annotation:

.. automodule:: ambiscaper.util
    :members: cartesian_to_spherical, spherical_to_cartesian