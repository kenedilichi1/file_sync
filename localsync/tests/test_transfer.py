import pytest
import tempfile
import os
from transfer import FileTransfer
from utils.compression import CompressionMethod

class TestFileTransfer:
    @pytest.fixture
    def transfer(self):
        """Create a FileTransfer instance for testing"""
        return FileTransfer(port=9999)  # Use different port for testing
    
    @pytest.fixture
    def test_file(self):
        """Create a test file"""
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
            f.write("This is a test file content for transfer testing." * 100)
        yield f.name
        os.unlink(f.name)
    
    def test_file_transfer(self, transfer, test_file):
        """Test basic file transfer functionality"""
        # This would require a more complex setup with two instances
        # For now, we'll test the component functions
        assert os.path.exists(test_file)
        
        # Test compression
        with open(test_file, 'rb') as f:
            original_data = f.read()
        
        compressed = transfer._compress_data(original_data, CompressionMethod.ZLIB)
        decompressed = transfer._decompress_data(compressed, CompressionMethod.ZLIB)
        
        assert original_data == decompressed
        assert len(compressed) < len(original_data)  # Should be smaller
        
    def test_checksum_calculation(self, transfer, test_file):
        """Test checksum calculation"""
        with open(test_file, 'rb') as f:
            data = f.read()
        
        checksum1 = transfer._calculate_checksum(data)
        checksum2 = transfer._calculate_checksum(data)
        
        assert checksum1 == checksum2  # Should be deterministic
        
        # Change data slightly and checksum should change
        modified_data = data + b"x"
        checksum3 = transfer._calculate_checksum(modified_data)
        assert checksum1 != checksum3