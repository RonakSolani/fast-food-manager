# imghdr.py - Simple implementation to replace the removed module in Python 3.13.1
# This provides basic functionality needed by Streamlit

def what(file, h=None):
    """Determine the type of image contained in a file or memory buffer.
    
    This is a simplified version of the removed imghdr module to support Streamlit in Python 3.13.1
    
    Args:
        file: A filename (string) or a file object open for reading in binary mode
        h: The first few bytes of the file, if already read
        
    Returns:
        A string describing the image type if recognized, or None if not recognized
    """
    if h is None:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
    
    # Check for PNG
    if h.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    
    # Check for JPEG
    if h[0:2] == b'\xff\xd8':
        return 'jpeg'
    
    # Check for GIF
    if h[0:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    
    # Check for BMP
    if h[0:2] == b'BM':
        return 'bmp'
    
    # Check for WEBP
    if h[0:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'
    
    # Add more image formats as needed
    
    return None