# hullbreach_server
# frob:invariant INV-007
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hullbreach_server")
except PackageNotFoundError:  # running from a bare checkout
    __version__ = "0.0.0"
