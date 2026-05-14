import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
PICOGL_SHADER_SRC_DIRECTORY = Path(PROJECT_ROOT) / "picogl" / "shaders" / "src"
SHADER_SRC_DIRECTORY = Path(PROJECT_ROOT) / "picogl" / "shaders" / "src"