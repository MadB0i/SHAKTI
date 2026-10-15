"""Compatibility entry point for the current delivery edit."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("prepare-launch-media.py")),run_name="__main__")
