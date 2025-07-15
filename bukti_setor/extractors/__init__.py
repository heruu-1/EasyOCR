# bukti_setor/extractors/__init__.py

from .kode_setor import extract_kode_setor
from .tanggal import extract_tanggal_setor
from .jumlah import extract_jumlah_setor
from .ntpn import extract_ntpn

__all__ = [
    "extract_kode_setor",
    "extract_tanggal_setor", 
    "extract_jumlah_setor",
    "extract_ntpn"
]
