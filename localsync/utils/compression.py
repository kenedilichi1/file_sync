import zlib
import gzip
import lzma
import bz2
from enum import Enum

class CompressionMethod(Enum):
    NONE = 0
    ZLIB = 1
    GZIP = 2
    LZMA = 3
    BZ2 = 4

class CompressionManager:
    @staticmethod
    def compress_data(data: bytes, method: CompressionMethod = CompressionMethod.ZLIB) -> bytes:
        """Compress data using specified method"""
        if method == CompressionMethod.NONE:
            return data
        elif method == CompressionMethod.ZLIB:
            return zlib.compress(data)
        elif method == CompressionMethod.GZIP:
            return gzip.compress(data)
        elif method == CompressionMethod.LZMA:
            return lzma.compress(data)
        elif method == CompressionMethod.BZ2:
            return bz2.compress(data)
        else:
            raise ValueError(f"Unknown compression method: {method}")
    
    @staticmethod
    def decompress_data(compressed_data: bytes, method: CompressionMethod = CompressionMethod.ZLIB) -> bytes:
        """Decompress data using specified method"""
        if method == CompressionMethod.NONE:
            return compressed_data
        elif method == CompressionMethod.ZLIB:
            return zlib.decompress(compressed_data)
        elif method == CompressionMethod.GZIP:
            return gzip.decompress(compressed_data)
        elif method == CompressionMethod.LZMA:
            return lzma.decompress(compressed_data)
        elif method == CompressionMethod.BZ2:
            return bz2.decompress(compressed_data)
        else:
            raise ValueError(f"Unknown compression method: {method}")
    
    @staticmethod
    def get_recommended_method(data_size: int) -> CompressionMethod:
        """Get recommended compression method based on data size"""
        if data_size < 1024 * 1024:  # < 1MB
            return CompressionMethod.ZLIB
        else:
            return CompressionMethod.LZMA