import os
import re

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

def replace_in_filename(name, old, new, ignore_extension):
    """Replace old text with new text in filenames."""
    if ignore_extension:
        new_name = name.replace(old, new)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = base_name.replace(old, new)
        new_name = new_base_name + ext
    return new_name

def to_snake_case(name, ignore_extension, preserve_caps=False):
    name, ext = _split_extension(name) if ignore_extension else (name, "")
    words = _split_into_words(name)
    
    if preserve_caps:
        # Keep fully uppercase words as they are, others transformed to lowercase
        words = [word if word.isupper() else word.lower() for word in words]
    
    return '_'.join(words) + ext

def to_camel_case(name, ignore_extension, preserve_caps=False):
    name, ext = _split_extension(name) if ignore_extension else (name, "")
    words = _split_into_words(name)
    
    if preserve_caps:
        # Keep fully uppercase words as they are, others transformed to lowercase
        words = [word if word.isupper() else word.lower() for word in words]
    
    camel = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    return camel + ext

def to_pascal_case(name, ignore_extension, preserve_caps=False):
    name, ext = _split_extension(name) if ignore_extension else (name, "")
    words = _split_into_words(name)
    
    if preserve_caps:
        # Keep fully uppercase words as they are, others transformed to lowercase
        words = [word if word.isupper() else word.lower() for word in words]
    
    return ''.join(word.capitalize() for word in words) + ext

def to_kebab_case(name, ignore_extension, preserve_caps=False):
    name, ext = _split_extension(name) if ignore_extension else (name, "")
    words = _split_into_words(name)
    
    if preserve_caps:
        # Keep fully uppercase words as they are, others transformed to lowercase
        words = [word if word.isupper() else word.lower() for word in words]
    
    return '-'.join(words) + ext

def to_title_case(name, ignore_extension, preserve_caps=False):
    name, ext = _split_extension(name) if ignore_extension else (name, "")
    words = _split_into_words(name)
    
    if preserve_caps:
        # Keep fully uppercase words as they are, others capitalized
        words = [word if word.isupper() else word.capitalize() for word in words]
    else:
        # Capitalize all words if preserve_caps is not set
        words = [word.capitalize() for word in words]
    
    return ' '.join(words) + ext

## Helper Functions
def _split_extension(filename):
    """Splits filename into (name, extension), where extension includes the dot."""
    name, ext = os.path.splitext(filename)
    return name, ext

def _split_into_words(name):
    # Replace separators with spaces
    name = name.replace('_', ' ').replace('-', ' ')

    # Split camel case (myFileName -> my File Name)
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)

    # Normalize all spacing and split into words
    words = re.split(r'\s+', name.strip())
    return [word.lower() for word in words if word]

