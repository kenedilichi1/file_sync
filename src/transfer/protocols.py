import json
import socket


class TransferProtocol:
    def __init__(self):
        pass

    def receive_request_metadata(self, ssock):
        """Receive request metadata"""
        request_data = b''
        while True:
            chunk = ssock.recv(1024)
            request_data += chunk
            if b'<REQUEST_END>' in request_data:
                break
            if len(request_data) > 65536:
                ssock.send("ERROR: Request too large".encode())
                return None
        
        request_str = request_data.split(b'<REQUEST_END>')[0].decode()
        return json.loads(request_str)

    def receive_file_metadata(self, ssock):
        """Receive file metadata"""
        metadata = b''
        while True:
            chunk = ssock.recv(1024)
            metadata += chunk
            if b'<METADATA_END>' in metadata:
                break
            if len(metadata) > 65536:
                ssock.send("ERROR: Metadata too large".encode())
                return None
        
        metadata_str = metadata.split(b'<METADATA_END>')[0].decode()
        return json.loads(metadata_str)