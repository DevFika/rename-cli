import Imath
import imageio.v3 as iio
import OpenEXR
import os
import re
from PIL import Image

RESOLUTION_TAGS = {
    2: "2",
    4: "4",
    8: "8",
    16: "16",
    32: "32",
    64: "64",
    128: "128",
    256: "256",
    512: "512",
    1024: "1K",
    2048: "2K",
    4096: "4K",
    8192: "8K"
}

def _get_texture_resolution(path):
    image_path = path.resolve()
    ext = os.path.splitext(image_path)[-1].lower()
    # print(image_path)
    try:
        if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            with Image.open(image_path) as img:
                return img.width, img.height

        elif ext in [".tga", ".dds"]:
            img = iio.imread(image_path)
            return img.shape[1], img.shape[0]  # (width, height)
        
        elif ext == ".exr":  # Special handling for .exr
            # print("EXT FILE")
            # file = OpenEXR.InputFile(image_path)
            file = OpenEXR.InputFile(path.as_posix())
            # print("opening file")
            header = file.header()
            # print(header)
            width = header['displayWindow'].max.x - header['displayWindow'].min.x + 1
            height = header['displayWindow'].max.y - header['displayWindow'].min.y + 1
            # print(width)
            # print(height)
            return width, height
        
        else:
            return "Unsupported format", None

    except Exception as e:
        return None, None
        # return "Error", str(e)
    
def _get_resolution_tag(width, height):
    """Convert resolution to tag format (_512, _1K, _2K, etc.)."""
    if width == height and width in RESOLUTION_TAGS:
        return RESOLUTION_TAGS[width]
    return f"{width}x{height}"  # Fallback to exact resolution

def _get_image_info(path):
    image_path = path.resolve()
    ext = os.path.splitext(image_path)[-1].lower()

    try:
        if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            with Image.open(image_path) as img:
                bit_depth = img.info.get("bits", 8)  # Default to 8 if not found
                # print(f"{ext}: bit depth: {bit_depth}")
                # print(f"{img.mode}")

                mode_to_info = {
                    "1": ("L", 1),    # 1-bit Black & White
                    "L": ("L", bit_depth),    # 8-bit Grayscale
                    "P": ("P", 8),    # 8-bit Palette
                    "RGB": ("RGB", bit_depth), # 24-bit RGB (8 per channel)
                    "RGBA": ("RGBA", bit_depth), # 32-bit RGBA (8 per channel)
                    "I": ("I", 32),  # 32-bit Integer
                    "F": ("F", 32),  # 32-bit Float
                    "I;16": ("L", 16)
                }
                img_type, bits_per_channel = mode_to_info.get(img.mode, (None, None))
                return img_type, bits_per_channel

        elif ext in [".tga", ".dds"]:
            img = iio.imread(image_path)
            
            # Check the number of channels to determine if it's RGBA or RGB
            num_channels = img.shape[-1] if len(img.shape) > 2 else 1

            dtype_to_info = {
                "uint8": (8, "RGB"),
                "uint16": (16, "RGB"),
                "float16": (16, "F16"),
                "float32": (32, "F32"),
            }

            # Determine bit depth and type from dtype
            bit_depth, img_type = dtype_to_info.get(str(img.dtype), (None, None))

            # If it's more than 3 channels, we assume it's RGBA
            if num_channels == 4:
                img_type = "RGBA"

            return img_type, bit_depth
        
        elif ext == ".exr":
            file = OpenEXR.InputFile(path.as_posix())
            header = file.header()
            channels = header['channels']
            # print(header)
            # print(channels)
            
            # Extract image data type (based on channels and type)
            channel_types = set()
            # print("hello")
            channel_info = {}
            overall_bit_depth = 0
            prefix = ""
            for channel_name, channel_data in channels.items():
                # print(f"Channel: {channel_name}, Data: {channel_data}")  # Check the channel data type
                # print(channel_data.type)
                
                pixel_type = channel_data.type
                # print(pixel_type)
                # print(Imath.PixelType.FLOAT)
                # print(Imath.PixelType(Imath.PixelType.HALF))
                if pixel_type == Imath.PixelType(Imath.PixelType.HALF):
                    # print(f"Channel '{channel_name}' is of type HALF.")
                    prefix = "F"
                    bit_depth = 16
                    # numpy_type = np.float16
                elif pixel_type == Imath.PixelType(Imath.PixelType.FLOAT):
                    # print(f"Channel '{channel_name}' is of type FLOAT.")
                    prefix = "F"
                    bit_depth = 32
                    # numpy_type = np.float32
                elif pixel_type == Imath.PixelType(Imath.PixelType.UINT):
                    # print(f"Channel '{channel_name}' is of type UINT.")
                    bit_depth = 32
                    prefix = "I"
                    # numpy_type = np.uint32
                else:
                    bit_depth = ""
                    # print(f"Channel '{channel_name}' has an unknown type.")
                    # numpy_type = None
                overall_bit_depth = bit_depth

                channel_info[channel_name] = {
                "bit_depth": bit_depth,
                # "numpy_type": numpy_type,
                "pixel_type": pixel_type,
            }

            # print(channel_info)
            # print("CHANNEL INFO")
            # for channel_name, channel_details in channel_info.items():
                # print(f"Channel: {channel_name}, Data: {channel_details}")  # Check the channel data type
                # Now check the data_type
                # if data_type_str == "FLOAT":
                #     channel_types.add('float32')
                # elif data_type_str == "HALF":
                #     channel_types.add('float16')
                # elif data_type_str == "UINT":
                #     channel_types.add('uint8')
                # else:
                #     print(f"Unknown data type for {channel_name}: {data_type_str}")
            
            # print("hello")
            # print(channel_types)  # Print out the collected types
            # colorChannels = ['R', 'G', 'B', 'A'] if 'A' in header['channels'] else ['R', 'G', 'B']
            img_type = 'RGBA' if len(channels) == 4 else 'RGB'
            bit_depth = overall_bit_depth
            # If only one type exists, set the img_type and bit depth
            # if len(channel_types) == 1:
            #     img_type = 'RGBA' if len(channels) == 4 else 'RGB'
            #     bit_depth = channel_types.pop()  # Get the data type of the channels
            # else:
            #     img_type = "Unknown"
            #     bit_depth = "Unknown"

            # If you have only 1 channel, it can be grayscale
            if len(channels) == 1:
                img_type = "L"
                # bit_depth = overall_bit_depth

            bit_depth = f"{prefix}{bit_depth}"

            return img_type, bit_depth
        else:
            return None, None

    except Exception as e:
        return "Error", str(e)

def add_resolution(name, values, ignore_extension, path):
    """Add a suffix to filenames before the extension."""
    file_path = path.resolve()
    # print(file_path)
    width, height = _get_texture_resolution(path)
    type = values[0]

    # print(width)
    if width is None or height is None:
        print(f"Skipping {name}: Unsupported format or error.")
        return name
    
    resolution_suffix = _get_resolution_tag(width, height) if type == "tag" else f"{width}x{height}"

    if ignore_extension:
        new_name = f"{name}_{resolution_suffix}"
    else:
        base_name, ext = os.path.splitext(name)
        new_name = f"{base_name}_{resolution_suffix}{ext}"
    return new_name

def add_image_info(name, values, ignore_extension, path):
    """Add a suffix to filenames before the extension."""
    file_path = path.resolve()
    # print(file_path)
    img_type, bits_per_channel = _get_image_info(path)
    if img_type is None or bits_per_channel is None:
        print(f"Skipping {name}: Unsupported format or error.")
        return name
    
    image_info_suffix = f"{img_type}_{bits_per_channel}"

    if ignore_extension:
        new_name = f"{name}_{image_info_suffix}"
    else:
        base_name, ext = os.path.splitext(name)
        new_name = f"{base_name}_{image_info_suffix}{ext}"
    return new_name

def remove_resolution(file_name, type, ignore_extension):
    TAG_RESOLUTION_REGEX = r'(^|[\s_.-])(2|4|8|16|32|64|128|256|512|1024|2048|4096|8192)(K|k)?(?=[\s_.-]|$)'

    EXACT_RESOLUTION_REGEX = r'_(\d{3,4}x\d{3,4})'  # 2048x2048, 1024x512
    file_path, file_extension = os.path.splitext(file_name)

    if ignore_extension:
        file_name_with_extension = f"{file_path}{file_extension}"  # Treat full name (including extension)
    else:
        file_name_with_extension = file_path  # Separate name and extension handling

    # print(file_name)
    type = type[0]
    # print(type)

    if type == "tag":
        file_name_with_extension = re.sub(TAG_RESOLUTION_REGEX, '', file_name_with_extension)

    if type == "exact":
        file_name_with_extension = re.sub(EXACT_RESOLUTION_REGEX, '', file_name_with_extension)

    if ignore_extension:
        return file_name_with_extension  # Whole name including extension
    else:
        # Rebuild the new filename, keeping the extension intact
        new_file_name = f"{file_name_with_extension}{file_extension}"
        return new_file_name
