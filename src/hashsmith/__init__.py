"""
HashSmith: A modern, compositional password pattern engine and hashcat orchestrator.
"""

__version__ = "0.2.1"
__author__ = "Baksi Li"
__email__ = "myself@baksili.codes"

from . import attacks, core, patterns

__all__ = ["attacks", "core", "patterns"]
