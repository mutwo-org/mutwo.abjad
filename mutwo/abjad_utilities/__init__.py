from .tests import *

from . import tests
from . import tools  # core patch

__all__ = tests.__all__

del tests, tools
