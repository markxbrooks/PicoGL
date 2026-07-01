"""
RGB Color 
"""
from dataclasses import dataclass

@dataclass
class RGB:
    """RGB color"""
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0
    

@dataclass
class RGBA(RGB):
    """RGBA color"""
    a: float = 1.0
