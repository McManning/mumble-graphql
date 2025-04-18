
import base64
from io import BytesIO
from PIL import Image

# Mapping between a [server_id:user_id] -> Data URI
texture_cache: dict[str, str] = {}


def texture_to_data_uri(texture) -> str:
    """Convert a Murmur Texture to a data uri encoded PNG"""

    if len(texture) < 1:
        return None

    # Murmur gives us the *original* image data, so we want
    # to try to decode that, crush it to an avatar size, and encode
    image = Image.open(BytesIO(texture))
    image.thumbnail((128, 128), Image.ANTIALIAS)

    # Convert image to PNG string
    buffered = BytesIO()
    image.save(buffered, format='PNG')

    encoded = base64.b64encode(buffered.getvalue())
    return 'data:image/png;base64,' + encoded.decode('utf-8')


def get_cache_key(server_id: str, user_id: str) -> str:
    return f"{server_id}:{user_id}"


def get_texture_cache(server_id: str, user_id: str) -> str | None:
    """Get the cached texture, if present"""
    key = get_cache_key(server_id, user_id)
    if not key in texture_cache:
        return None

    return texture_cache[key]


def set_texture_cache(server_id: str, user_id: str, texture: bytes | None) -> str:
    """Cache the raw texture as a PNG data URI and return that URI"""
    if not texture:
        data_uri = None
    else:
        data_uri = texture_to_data_uri(texture)

    key = get_cache_key(server_id, user_id)
    texture_cache[key] = data_uri
    return data_uri
