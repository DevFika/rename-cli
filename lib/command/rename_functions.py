import os

def to_uppercase(name, ignore_extension):
    """Convert filename to uppercase."""
    if ignore_extension:
        new_name = name.upper()
    else:
        base_name, ext = os.path.splitext(name)
        new_name = base_name.upper() + ext
    return new_name

def to_lowercase(name, ignore_extension):
    """Convert filename to lowercase."""
    if ignore_extension:
        new_name = name.lower()
    else:
        base_name, ext = os.path.splitext(name)
        new_name = base_name.lower() + ext
    return new_name