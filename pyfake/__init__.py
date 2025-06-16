from .__version import __version__

# from .core.engine import Pyfake
# from .generators import number

# from pyfake.core.engine import Pyfake
# from pyfake.generators import number

from .core.engine import Pyfake
from .generators import number

__all__ = ["Pyfake", "__version__", "number"]
