"""Source adapters. Each module exposes a fetch(config, http) -> List[PropertyRecord]."""
from .base import BaseAdapter
from .gsa_realestatesales import GSARealEstateSalesAdapter
from .fdic_ore import FDICOREAdapter
from .bid4assets_county import Bid4AssetsCountyAdapter
from .sba_oreo import SBAOREOAdapter
from .la_pais import LAPAISAdapter

__all__ = [
    "BaseAdapter",
    "GSARealEstateSalesAdapter",
    "FDICOREAdapter",
    "Bid4AssetsCountyAdapter",
    "SBAOREOAdapter",
    "LAPAISAdapter",
]
