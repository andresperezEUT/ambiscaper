#!/usr/bin/env python
"""Top-level module for ambiscaper"""

from .core import AmbiScaper
from .core import generate_from_jams
from .core import trim
import jams
from pkg_resources import resource_filename
from .version import version as __version__

# Add sound_event namesapce
namespace_file = resource_filename(__name__, 'namespaces/ambiscaper_sound_event.json')
jams.schema.add_namespace(namespace_file)

# Add smir_reverb namesapce
smir_reverb_namespace_file = resource_filename(__name__, 'namespaces/ambiscaper_smir_reverb.json')
jams.schema.add_namespace(smir_reverb_namespace_file)

# Add sofa reverb namespace
recorded_reverb_namespace_file = resource_filename(__name__, 'namespaces/ambiscaper_sofa_reverb.json')
jams.schema.add_namespace(recorded_reverb_namespace_file)
