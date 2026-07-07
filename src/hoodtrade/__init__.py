"""Hood Trade — a pre-trade safety scanner for Robinhood Chain.

Read-only. It never signs, never holds funds, never trades. It inspects a proposed
swap and returns a GO / CAUTION / NO-GO verdict with the evidence behind it.
"""

from .models import ScanReport, TradeRequest, Verdict

__version__ = "0.4.1"
__all__ = ["ScanReport", "TradeRequest", "Verdict", "__version__"]
