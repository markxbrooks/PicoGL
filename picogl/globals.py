"""
PicoGL Globals
"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
PICOGL_PROJECT_ROOT = PROJECT_ROOT
PICOGL_EXAMPLES_DIR = Path(PROJECT_ROOT) / "picogl" / "examples"
PICOGL_SHADER_SRC_DIRECTORY = Path(PROJECT_ROOT) / "picogl" / "shaders" / "src"
SHADER_SRC_DIRECTORY = Path(PROJECT_ROOT) / "picogl" / "shaders" / "src"
