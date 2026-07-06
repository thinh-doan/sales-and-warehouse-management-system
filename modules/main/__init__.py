"""Main module package."""

import sys

from . import main as _main_module
from .main import MainController

# Backward compatibility for main.py importing modules.main.main_controller.
sys.modules[__name__ + ".main_controller"] = _main_module

__all__ = ["MainController"]
