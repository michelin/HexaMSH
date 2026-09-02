# coding: utf-8
"""Main module of HexaMSH."""

try:
    from .version import __version__, __version_date__
except ImportError:
    __version__ = None
    __version_date__ = ""


def main(*args, **kwargs):
    """Lazy CLI entrypoint to avoid import-time side effects during packaging."""
    from .hexamsh import main as _main

    return _main(*args, **kwargs)
