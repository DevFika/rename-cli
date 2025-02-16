import argparse
from pathlib import Path
import sys
import re
import shlex
import os
import difflib
import shutil

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
END = "\033[0m"
LIGHT_GRAY = "\033[97m"
DARK_GRAY = "\033[90m"
DARKER_GRAY = "\033[38;5;245m"
MAGENTA = "\033[95m"
GREEN46 = f"\033[38;5;46m"
COLOR229 = f"\033[38;5;229m"
# LIGHT_GREEN_GRAY = "\033[38;5;149m"
LIGHT_GREEN_GRAY = "\033[38;5;147m"
LIGHT_YELLOW_GRAY = "\033[38;5;190m"
WARNING_COLOR = RED
NEW_COLOR = GREEN
ORIGINAL_COLOR = DARKER_GRAY
PENDING_COLOR = YELLOW
PENDING_HIGHLIGHT_COLOR = GREEN
END_COLOR = END
INTERACTIVE_MODE_COLOR = MAGENTA
BOLD = "\033[1m"
UNDERLINE = "\033[4m"



class OrderedAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, 'ordered_args'):
            setattr(namespace, 'ordered_args', [])
        
        if values is None:
            namespace.ordered_args.append((self.dest, True))
            setattr(namespace, self.dest, True)
        else:
            namespace.ordered_args.append((self.dest, values))
            setattr(namespace, self.dest, values)

def clear_terminal():
    """Clears the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def highlight_changes(original, new):
    """Highlight differences between original and new name."""
    matcher = difflib.SequenceMatcher(None, original, new)
    highlighted_original = ""
    highlighted_new = ""

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # Keep unchanged text normal in both original and new name
            highlighted_original += f"{DARKER_GRAY}{original[i1:i2]}{END}"
            highlighted_new += f"{LIGHT_GRAY}{new[j1:j2]}{END}"
        elif tag == "replace" or tag == "insert":
            # Highlight new/inserted text in new name
            highlighted_new += f"{PENDING_HIGHLIGHT_COLOR}{new[j1:j2]}{END}"
            # Highlight removed text in original name
            highlighted_original += f"{RED}{original[i1:i2]}{END}"
        elif tag == "delete":
            # Highlight removed text in original name
            highlighted_original += f"{RED}{original[i1:i2]}{END}"

    return highlighted_original, highlighted_new

def extension_type(value):
    """Ensure extensions start with a dot."""
    if not value.startswith('.'):
        raise argparse.ArgumentTypeError(f"Extension must start with a dot (e.g., '.txt').")
    return value.lower()


def clean_filename(name, ignore_extension):
    """Remove unwanted characters (e.g., spaces, extra underscores)."""
    if ignore_extension:
        new_name = re.sub(r'[_\s]+', '_', name)  # Replace multiple spaces or underscores with a single underscore
        new_name = re.sub(r'[^a-zA-Z0-9._-]', '', new_name)  # Remove non-alphanumeric characters
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'[_\s]+', '_', base_name)  # Replace multiple spaces or underscores with a single underscore
        new_base_name = re.sub(r'[^a-zA-Z0-9._-]', '', new_base_name)  # Remove non-alphanumeric characters
        new_name = new_base_name + ext
    return new_name


def remove_duplicate_words(name, ignore_extension):
    """Remove duplicate words or repeated patterns in the filename."""

    # Detect and remove repeated sequences like "testtest" -> "test"
    def remove_repeated_patterns(text):
        return re.sub(r'(\w+)\1', r'\1', text)  # Only remove full repeated sequences

    # Remove separate duplicate words (e.g., "test test test" -> "test", "test_test_test" -> "test")
    def remove_duplicate_whole_words(text):
        words = re.split(r'[_\s]+', text)  # Split by underscores or spaces
        seen = []
        for word in words:
            if word not in seen:
                seen.append(word)
        return '_'.join(seen)  # Join back with underscores

    if ignore_extension:
        name = remove_repeated_patterns(name)  # Fix patterns inside words
        new_name = remove_duplicate_whole_words(name)  # Fix duplicate words
    else:
        base_name, ext = os.path.splitext(name)
        base_name = remove_repeated_patterns(base_name)
        new_base_name = remove_duplicate_whole_words(base_name)
        new_name = new_base_name + ext  # Reattach extension

    return new_name


def limit_word_count(name, max_words, ignore_extension):
    """Limit the number of words in the filename to a specified maximum."""
    if ignore_extension:
        words = name.split()
        new_name = ' '.join(words[:max_words])
    else:
        base_name, ext = os.path.splitext(name)
        words = base_name.split()
        new_base_name = ' '.join(words[:max_words])
        new_name = new_base_name + ext
    return new_name

def insert_text_at_position(name, text, position, ignore_extension):
    """Insert specified text at a given position in the filename."""
    if ignore_extension:
        new_name = name[:position] + text + name[position:]
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = base_name[:position] + text + base_name[position:]
        new_name = new_base_name + ext
    return new_name

def reverse_string(name, ignore_extension):
    """Reverse the entire filename or just the base name."""
    if ignore_extension:
        new_name = name[::-1]
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = base_name[::-1]
        new_name = new_base_name + ext
    return new_name

def hash_filename(name, hash_type='md5', ignore_extension=False):
    """Generate a hash of the filename and append or prepend it."""
    import hashlib
    if ignore_extension:
        hash_obj = hashlib.new(hash_type)
        hash_obj.update(name.encode())
        hash_value = hash_obj.hexdigest()
        new_name = f"{hash_value}_{name}"
    else:
        base_name, ext = os.path.splitext(name)
        hash_obj = hashlib.new(hash_type)
        hash_obj.update(base_name.encode())
        hash_value = hash_obj.hexdigest()
        new_base_name = f"{hash_value}_{base_name}"
        new_name = new_base_name + ext
    return new_name

def camel_case_to_snake_case(name, ignore_extension):
    """Convert CamelCase to snake_case."""
    if ignore_extension:
        new_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', base_name).lower()
        new_name = new_base_name + ext
    return new_name

def pascal_case_to_camel_case(name, ignore_extension):
    """Convert PascalCase to camelCase."""

    def convert(text):
        # Lowercase the first character, keep the rest as is
        return text[0].lower() + text[1:]

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def pascal_case_to_kebab_case(name, ignore_extension):
    """Convert PascalCase to kebab-case."""

    def convert(text):
        # Insert hyphen before each capital letter (except the first) and convert to lowercase
        return re.sub(r'([a-z])([A-Z])', r'\1-\2', text).lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def pascal_case_to_title_case(name, ignore_extension):
    """Convert PascalCase to Title Case."""

    def convert(text):
        # Insert space before each capital letter (except the first)
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def pascal_case_to_snake_case(name, ignore_extension):
    """Convert PascalCase to snake_case."""

    def convert(text):
        # Insert underscore before each capital letter (except the first) and convert to lowercase
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', text).lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def pascal_case_to_spaces(name, ignore_extension):
    """Convert PascalCase to a format with spaces."""

    def convert(text):
        # Insert space before each capital letter (except the first)
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def snake_case_to_pascal_case(name, ignore_extension):
    """Convert snake_case to PascalCase (CamelCase with first letter capitalized)."""
    
    def convert(text):
        return ''.join(word.capitalize() for word in text.split('_'))

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def snake_case_to_camel_case(name, ignore_extension):
    """Convert snake_case to camelCase."""

    def convert(text):
        # Split the text by underscores and capitalize each word except the first one
        words = text.split('_')
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def snake_case_to_kebab_case(name, ignore_extension):
    """Convert snake_case to kebab-case."""

    def convert(text):
        # Replace underscores with hyphens and convert to lowercase
        return text.replace('_', '-').lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def snake_case_to_title_case(name, ignore_extension):
    """Convert snake_case to Title Case."""

    def convert(text):
        # Capitalize each word and join with spaces
        return ' '.join(word.capitalize() for word in text.split('_'))

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def snake_case_to_spaces(name, ignore_extension):
    """Convert snake_case to a format with spaces."""

    def convert(text):
        # Replace underscores with spaces
        return text.replace('_', ' ')

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def camel_case_to_pascal_case(name, ignore_extension):
    """Convert camelCase to PascalCase."""

    def convert(text):
        # Capitalize the first character, keep the rest as is
        return text[0].upper() + text[1:]

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def camel_case_to_snake_case(name, ignore_extension):
    """Convert camelCase to snake_case."""

    def convert(text):
        # Insert underscore before each capital letter and convert to lowercase
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', text).lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def camel_case_to_kebab_case(name, ignore_extension):
    """Convert camelCase to kebab-case."""

    def convert(text):
        # Insert hyphen before each capital letter and convert to lowercase
        return re.sub(r'([a-z])([A-Z])', r'\1-\2', text).lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def camel_case_to_title_case(name, ignore_extension):
    """Convert camelCase to Title Case."""

    def convert(text):
        # Insert space before each capital letter
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def camel_case_to_spaces(name, ignore_extension):
    """Convert camelCase to a format with spaces."""

    def convert(text):
        # Insert space before each capital letter
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def kebab_case_to_snake_case(name, ignore_extension):
    """Convert kebab-case to snake_case."""

    def convert(text):
        # Replace hyphens with underscores
        return text.replace('-', '_')

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def kebab_case_to_pascal_case(name, ignore_extension):
    """Convert kebab-case to PascalCase."""

    def convert(text):
        # Capitalize each word and remove hyphens
        return ''.join(word.capitalize() for word in text.split('-'))

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def kebab_case_to_camel_case(name, ignore_extension):
    """Convert kebab-case to camelCase."""

    def convert(text):
        # Capitalize each word except the first one and remove hyphens
        words = text.split('-')
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def kebab_case_to_title_case(name, ignore_extension):
    """Convert kebab-case to Title Case."""

    def convert(text):
        # Capitalize each word and replace hyphens with spaces
        return ' '.join(word.capitalize() for word in text.split('-'))

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def kebab_case_to_spaces(name, ignore_extension):
    """Convert kebab-case to a format with spaces."""

    def convert(text):
        # Replace hyphens with spaces
        return text.replace('-', ' ')

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def title_case_to_snake_case(name, ignore_extension):
    """Convert Title Case to snake_case."""

    def convert(text):
        # Replace spaces with underscores and convert to lowercase
        return text.replace(' ', '_').lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def title_case_to_pascal_case(name, ignore_extension):
    """Convert Title Case to PascalCase."""

    def convert(text):
        # Capitalize each word and remove spaces
        return ''.join(word.capitalize() for word in text.split())

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def title_case_to_camel_case(name, ignore_extension):
    """Convert Title Case to camelCase."""

    def convert(text):
        # Capitalize each word except the first one and remove spaces
        words = text.split()
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def title_case_to_spaces(name, ignore_extension):
    """Convert Title Case to a format with spaces."""

    def convert(text):
        # Convert to lowercase and replace spaces with spaces (no change needed)
        return text.lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def title_case_to_kebab_case(name, ignore_extension):
    """Convert Title Case to kebab-case."""

    def convert(text):
        # Replace spaces with hyphens and convert to lowercase
        return text.replace(' ', '-').lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def spaces_to_snake_case(name, ignore_extension):
    """Convert spaces to snake_case."""

    def convert(text):
        # Replace spaces with underscores and convert to lowercase
        return text.replace(' ', '_').lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def spaces_to_pascal_case(name, ignore_extension):
    """Convert spaces to PascalCase."""

    def convert(text):
        # Capitalize each word and remove spaces
        return ''.join(word.capitalize() for word in text.split())

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def spaces_to_camel_case(name, ignore_extension):
    """Convert spaces to camelCase."""

    def convert(text):
        # Capitalize each word except the first one and remove spaces
        words = text.split()
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def spaces_to_kebab_case(name, ignore_extension):
    """Convert spaces to kebab-case."""

    def convert(text):
        # Replace spaces with hyphens and convert to lowercase
        return text.replace(' ', '-').lower()

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def spaces_to_title_case(name, ignore_extension):
    """Convert spaces to Title Case."""

    def convert(text):
        # Capitalize each word
        return ' '.join(word.capitalize() for word in text.split())

    if ignore_extension:
        new_name = convert(name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = convert(base_name)
        new_name = new_base_name + ext

    return new_name

def remove_leading_zeros(name, ignore_extension):
    """Remove leading zeros from all numbers in a filename."""
    
    def strip_zeros(match):
        return str(int(match.group()))  # Convert to int and back to remove leading zeros

    if ignore_extension:
        new_name = re.sub(r'\d+', strip_zeros, name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'\d+', strip_zeros, base_name)
        new_name = new_base_name + ext

    return new_name

def add_leading_zeros_to_number(name, total_digits=2, ignore_extension=False):
    """Add leading zeros to numbers in the filename to ensure consistent digit length."""
    if ignore_extension:
        new_name = re.sub(r'(\d+)', lambda match: match.group(0).zfill(total_digits), name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'(\d+)', lambda match: match.group(0).zfill(total_digits), base_name)
        new_name = new_base_name + ext
    return new_name

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

def to_title_case(name, ignore_extension):
    """Convert filename to title case (capitalize each word)."""
    if ignore_extension:
        new_name = ' '.join(word.capitalize() for word in name.split(' '))
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = ' '.join(word.capitalize() for word in base_name.split(' '))
        new_name = new_base_name + ext
    return new_name

def remove_numbers(name, ignore_extension):
    """Remove all digits from the filename."""
    if ignore_extension:
        new_name = re.sub(r'\d+', '', name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'\d+', '', base_name)
        new_name = new_base_name + ext
    return new_name

def standardize_dates(name, ignore_extension):
    """Convert dates like DD-MM-YYYY or MM-DD-YYYY to YYYY-MM-DD."""
    if ignore_extension:
        new_name = re.sub(r'(\b\d{1,2})[-_/](\d{1,2})[-_/](\d{4})', r'\3-\1-\2', name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'(\b\d{1,2})[-_/](\d{1,2})[-_/](\d{4})', r'\3-\1-\2', base_name)
        new_name = new_base_name + ext
    return new_name

def trim_filename(name, ignore_extension):
    """Remove leading and trailing spaces."""
    if ignore_extension:
        new_name = name.strip()
    else:
        base_name, ext = os.path.splitext(name)
        new_name = base_name.strip() + ext
    return new_name

def replace_spaces_with_underscores(name, ignore_extension):
    """Replace spaces with underscores."""
    if ignore_extension:
        new_name = re.sub(r'\s+', '_', name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'\s+', '_', base_name)
        new_name = new_base_name + ext
    return new_name

def replace_word_by_index(name, separator, index, new_text, ignore_extension):
    """Replace the word at the specified index with new text using the specified separator."""
    if ignore_extension:
        parts = name.split(separator)
        if 0 <= index < len(parts):
            parts[index] = new_text
        new_name = separator.join(parts)
    else:
        base_name, ext = os.path.splitext(name)
        parts = base_name.split(separator)
        if 0 <= index < len(parts):
            parts[index] = new_text
        new_base_name = separator.join(parts)
        new_name = new_base_name + ext
    return new_name

def remove_special_characters(name, ignore_extension):
    """Remove all characters except letters, numbers, dots, and underscores."""
    if ignore_extension:
        new_name = re.sub(r'[^a-zA-Z0-9._]', '', name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'[^a-zA-Z0-9._]', '', base_name)
        new_name = new_base_name + ext
    return new_name

def shorten_filename(name, max_length=255, ignore_extension=False):
    """Shorten the filename to fit within the max length, preserving the extension."""
    if ignore_extension:
        if len(name) > max_length:
            name = name[:max_length]
    else:
        base_name, ext = os.path.splitext(name)
        if len(base_name) + len(ext) > max_length:
            base_name = base_name[:max_length - len(ext)]  # Truncate the base name
        name = f"{base_name}{ext}"
    return name

def remove_non_ascii(name, ignore_extension):
    """Remove all non-ASCII characters from the filename."""
    if ignore_extension:
        new_name = ''.join([char for char in name if ord(char) < 128])
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = ''.join([char for char in base_name if ord(char) < 128])
        new_name = new_base_name + ext
    return new_name

from datetime import datetime

def add_timestamp(name, granularity, ignore_extension):
    """Append a timestamp to the filename with specified granularity."""
    if granularity == 'year':
        timestamp = datetime.now().strftime("%Y")
    elif granularity == 'month':
        timestamp = datetime.now().strftime("%Y%m")
    elif granularity == 'day':
        timestamp = datetime.now().strftime("%Y%m%d")
    elif granularity == 'hour':
        timestamp = datetime.now().strftime("%Y%m%d_%H")
    elif granularity == 'minute':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    elif granularity == 'second':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    else:  # 'full' or any other value
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if ignore_extension:
        new_name = f"{name}_{timestamp}"
    else:
        base_name, ext = os.path.splitext(name)
        new_name = f"{base_name}_{timestamp}{ext}"

    return new_name

def regex_replace_in_filenames(name, pattern, replacement, ignore_extension):
    """Use regex to replace a pattern in filenames."""
    if ignore_extension:
        new_name = re.sub(pattern, replacement, name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(pattern, replacement, base_name)
        new_name = new_base_name + ext
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

def add_prefix(name, prefix, ignore_extension):
    """Add a prefix to filenames."""
    if ignore_extension:
        new_name = prefix + name
    else:
        base_name, ext = os.path.splitext(name)
        new_name = prefix + base_name + ext
    return new_name

def add_suffix(name, suffix, ignore_extension):
    """Add a suffix to filenames before the extension."""
    if ignore_extension:
        new_name = name + suffix
    else:
        base_name, ext = os.path.splitext(name)
        new_name = base_name + suffix + ext
    return new_name

def handle_case(name, values, ignore_extension):
    from_case = values[0]
    to_case = values[1]
    ignore_caps = (len(values) > 2 and values[2] == "-ignore-caps")
    if from_case == "snake":
        if to_case == "pascal":
            new_name = snake_case_to_pascal_case(name, ignore_extension)
        elif to_case == "camel":
            new_name = snake_case_to_camel_case(name, ignore_extension)
        elif to_case == "kebab":
            new_name = snake_case_to_kebab_case(name, ignore_extension)
        elif to_case == "title":
            new_name = snake_case_to_title_case(name, ignore_extension)
        elif to_case == "space":
            new_name = snake_case_to_spaces(name, ignore_extension)
    elif from_case == "pascal":
        if to_case == "snake":
            new_name = pascal_case_to_snake_case(name, ignore_extension)
        elif to_case == "camel":
            new_name = pascal_case_to_camel_case(name, ignore_extension)
        elif to_case == "kebab":
            new_name = pascal_case_to_kebab_case(name, ignore_extension)
        elif to_case == "title":
            new_name = pascal_case_to_title_case(name, ignore_extension)
        elif to_case == "space":
            new_name = pascal_case_to_spaces(name, ignore_extension)
    elif from_case == "camel":
        if to_case == "snake":
            new_name = camel_case_to_snake_case(name, ignore_extension)
        elif to_case == "pascal":
            new_name = camel_case_to_pascal_case(name, ignore_extension)
        elif to_case == "kebab":
            new_name = camel_case_to_kebab_case(name, ignore_extension)
        elif to_case == "title":
            new_name = camel_case_to_title_case(name, ignore_extension)
        elif to_case == "space":
            new_name = camel_case_to_spaces(name, ignore_extension)
    elif from_case == "kebab":
        if to_case == "snake":
            new_name = kebab_case_to_snake_case(name, ignore_extension)
        elif to_case == "pascal":
            new_name = kebab_case_to_pascal_case(name, ignore_extension)
        elif to_case == "camel":
            new_name = kebab_case_to_camel_case(name, ignore_extension)
        elif to_case == "title":
            new_name = kebab_case_to_title_case(name, ignore_extension)
        elif to_case == "space":
            new_name = kebab_case_to_spaces(name, ignore_extension)
    elif from_case == "title":
        if to_case == "snake":
            new_name = title_case_to_snake_case(name, ignore_extension)
        elif to_case == "pascal":
            new_name = title_case_to_pascal_case(name, ignore_extension)
        elif to_case == "camel":
            new_name = title_case_to_camel_case(name, ignore_extension)
        elif to_case == "kebab":
            new_name = title_case_to_kebab_case(name, ignore_extension)
        elif to_case == "space":
            new_name = title_case_to_spaces(name, ignore_extension)
    elif from_case == "space":
        if to_case == "snake":
            new_name = spaces_to_snake_case(name, ignore_extension)
        elif to_case == "pascal":
            new_name = spaces_to_pascal_case(name, ignore_extension)
        elif to_case == "camel":
            new_name = spaces_to_camel_case(name, ignore_extension)
        elif to_case == "kebab":
            new_name = spaces_to_kebab_case(name, ignore_extension)
        elif to_case == "title":
            new_name = spaces_to_title_case(name, ignore_extension)
    return new_name
    
def process_filename(name, arg, values, args):
    ignore_extension = args.ignore_extension
    """Apply selected transformations."""
    if arg == "camel_to_snake":
        name = camel_case_to_snake_case(name, ignore_extension)
    elif arg == "snake_to_pascal":
        name = snake_case_to_pascal_case(name, ignore_extension)
    elif arg == "remove_zeros":
        name = remove_leading_zeros(name, ignore_extension)
    elif arg == "add_zeros":
        name = add_leading_zeros_to_number(name, values[0], ignore_extension)
    elif arg == "uppercase":
        name = to_uppercase(name, ignore_extension)
    elif arg == "lowercase":
        name = to_lowercase(name, ignore_extension)
    elif arg == "remove_numbers":
        name = remove_numbers(name, ignore_extension)
    elif arg == "standardize_dates":
        name = standardize_dates(name, ignore_extension)
    elif arg == "trim":
        name = trim_filename(name, ignore_extension)
    elif arg == "replace_spaces":
        name = replace_spaces_with_underscores(name, ignore_extension)
    elif arg == "remove_special":
        name = remove_special_characters(name, ignore_extension)
    elif arg == "remove_non_ascii":
        name = remove_non_ascii(name, ignore_extension)
    elif arg == "add_timestamp":
        name = add_timestamp(name, values[0], ignore_extension)
    elif arg == "title_case":
        name = to_title_case(name, ignore_extension)
    elif arg == "clean":
        name = clean_filename(name, ignore_extension)
    elif arg == "replace":
        name = replace_in_filename(name, values[0], values[1], ignore_extension)
    elif arg == "replace_ext":
        name = regex_replace_in_filenames(name, r'\.' + re.escape(values[0]) + '$', '.' + values[1], ignore_extension)
    elif arg == "replace_regex":
        name = regex_replace_in_filenames(name, values[0], values[1], ignore_extension)
    elif arg == "replace_index":
        name = replace_word_by_index(name, values[0], int(values[1]), values[2], ignore_extension)
    elif arg == "prefix":
        name = add_prefix(name, values, ignore_extension)
    elif arg == "suffix":
        name = add_suffix(name, values, ignore_extension)
    elif arg == "remove_duplicates":
        name = remove_duplicate_words(name, ignore_extension)
    elif arg == "limit_words":
        name = limit_word_count(name, values, ignore_extension)
    elif arg == "insert_text":
        name = insert_text_at_position(name, values[0], int(values[1]), ignore_extension)
    elif arg == "reverse":
        name = reverse_string(name, ignore_extension)
    elif arg == "case":
        name = handle_case(name, values, ignore_extension)
    # elif arg == "hash":
    #     name = hash_filename(name, values[0], ignore_extension)

    return name

class ReplaceAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Handle replacement logic
        if len(values) == 1:
            old = values[0]
            values.append("")
            new = ""
        else:
            old, new = values[0], values[1]
        
        # Add the replacement to the appropriate list
        replacements = getattr(namespace, self.dest, None)
        if replacements is None:
            replacements = []
            setattr(namespace, self.dest, replacements)
        replacements.append((old, new))
        
        # Track the order of the arguments
        if not hasattr(namespace, 'ordered_args'):
            setattr(namespace, 'ordered_args', [])
        
        # Add this action to the ordered arguments list
        namespace.ordered_args.append((self.dest, values))


def confirm_rename(old_name, new_name):
    """Interactive confirmation for renaming."""
    confirm = input(f"Rename {old_name} to {new_name}? (y/n): ")
    if confirm.lower() != 'y':
        print(f"{WARNING_COLOR}Skipping renaming of {old_name}{END_COLOR}")
        return False
    return True


def rename_file(path, args, target_path):
    """Renames a single file based on user-defined rules."""
    if not path.is_file():
        print(f"❌ Error: {path} is not a valid file.", file=sys.stderr)
        return
    
    preview = args.preview
    verbose = args.verbose
    confirm = args.confirm
    
    new_name = path.name
    actions = args.ordered_args if hasattr(args, 'ordered_args') else []

    log = True

    for arg, values in actions:
        new_name = process_filename(new_name, arg, values, args)

    if new_name == path.name:
        if verbose:
            print(f"ℹ️ No changes needed: {path}")
        return

    new_path = path.with_name(new_name)

    # TODO: Add check for overwriting existing files
    # Prevent overwriting existing files
    # if any(f.lower() == new_path.name.lower() for f in os.listdir(new_path.parent)):
    # if new_path.name.lower() == new_path.name.lower() and path.name != new_path.name:
    # if new_path.exists():
    #     print(f"⚠️  Skipping (target exists): {path} -> {new_path}")
    #     return

    relative_path = path.relative_to(target_path)
    relative_new_name = new_path.relative_to(target_path)

    rename_text = "Renaming" if not preview else "Preview"

    highlighted_original, highlighted_new = highlight_changes(relative_path.name, relative_new_name.name)
    print(f"{rename_text}: {highlighted_original} -> {highlighted_new}")

    if not preview:
        try:
            if confirm:
                if confirm_rename(path.name, new_name):  # Confirm before renaming
                    path.rename(new_path)
                    if verbose:
                        print(f"{NEW_COLOR}File renamed successfully!{END_COLOR}")
            else:
                path.rename(new_path)
                if verbose:
                    print(f"{NEW_COLOR}File renamed successfully!{END_COLOR}")
        except FileExistsError:
            print(f"⚠️ Error: {new_path} already exists.", file=sys.stderr)
        except PermissionError:
            print(f"⚠️ Permission denied to rename {path}.", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error renaming {path}: {e}", file=sys.stderr)


def rename_files(directory, args, extensions, target_path):
    """Renames multiple files in a directory based on user-defined rules and filters."""
    directory = Path(directory).resolve()

    if not directory.is_dir():
        print(f"❌ Error: {directory} is not a valid directory.", file=sys.stderr)
        return
    
    preview = args.preview
    verbose = args.verbose
    confirm = args.confirm
    recursive = args.recursive

    files = directory.rglob("*") if recursive else directory.glob("*")

    for path in files:
        if path.is_file():
            # Filter by extension if specified
            if extensions and path.suffix.lower() not in extensions:
                if verbose:
                    print(f"⚠️ Skipping: {path} (does not match specified extensions: {extensions})", file=sys.stderr)
                continue  # Skip files that don"t match the given extensions
            
            rename_file(path, args, target_path)

def pretty_print_preview(files_to_process):
    # Print a header with a fancy border
    print(f"{BOLD}{UNDERLINE}File Renaming Preview{END_COLOR}")
    terminal_width = shutil.get_terminal_size().columns
    print("━" * terminal_width)

    # Iterate through the files to process
    for i, (file, names) in enumerate(files_to_process.items()):
        original_name = f"{names['original_name']}"
        new_name = f"{names['new_name']}"
        highlighted_original, highlighted_new = highlight_changes(original_name, new_name)
        max_length = max(len(highlighted_original), len(highlighted_new))
        
        # Print original and new names with colors
        print(f"{WARNING_COLOR}■{END_COLOR} {highlighted_original:<{max_length}}")
        print(f"{NEW_COLOR}■{END_COLOR} {highlighted_new:<{max_length}}")
        
        # Check if this is the last item and skip the blank line after it
        if i != len(files_to_process) - 1:
            print()  # Adds a blank line for better readability between entries
    
    # Print options as a single-line bar
    # print("━" * terminal_width)
    options_bar = (
        f"Options: {NEW_COLOR}--apply{END_COLOR} | "
        f"{WARNING_COLOR}--exit{END_COLOR} | "
        f"{PENDING_COLOR}--confirm{END_COLOR} | "
        f"{CYAN}--undo{END_COLOR}"
    )

    # Add a box around the options bar┏┃┓
    padding = " " * 2
    options_bar_with_box = f"{'━' * (terminal_width)}\n"  # Top border

    # Add the options bar inside the box
    options_bar_with_box += f"{padding}{options_bar}{padding}\n"

    # Add the bottom border┗┛
    options_bar_with_box += f"{'━' * (terminal_width)}"

    print(options_bar_with_box)  # Print the boxed options


def interactive_rename(path, args, target_path, extensions):
    """Interactive renaming of files in a directory."""
    # Get the list of files to process
    files_to_process = {}
    verbose = args.verbose
    history = []

    # If the target is a file, add it to the dictionary
    if path.is_file():
        if extensions and path.suffix.lower() not in extensions:
            return
        files_to_process[path] = {'original_name': path.name, 'new_name': path.name}
    # If the target is a directory, get all files in the directory
    elif path.is_dir():
        files = target_path.rglob("*") if args.recursive else target_path.glob("*")
        for file in files:
            if file.is_file():
                if extensions and file.suffix.lower() not in extensions:
                    continue
                files_to_process[file] = {'original_name': file.name, 'new_name': file.name}

    # Loop until the user confirms the rename or exits for all files
    while True:
        try:
            # clear_terminal()

            pretty_print_preview(files_to_process)
            user_input = input(f"{INTERACTIVE_MODE_COLOR}Interactive Mode{END_COLOR}: ").strip()

            parser = create_parser(interactive_mode=True)

            args = parser.parse_args(shlex.split(user_input))

            extensions = {ext.lower() for ext in args.ext} if args.ext else None

            preview = args.preview
            
            if args.undo:
                if history:
                    last_snapshot = history.pop()
                    for file, old_name in last_snapshot.items():
                        files_to_process[file]['new_name'] = old_name
                else:
                    print("No changes to undo.")
                continue

            if args.apply or args.confirm:
                # User confirmed the rename for all files
                for file, names in files_to_process.items():
                    if names['new_name'] == names['original_name']:
                        if verbose:
                            print(f"ℹ️ No changes needed: {path}")
                        continue
                    if args.confirm:
                        if confirm_rename(file.name, names['new_name']):  # Confirm before renaming
                                file.rename(file.with_name(names['new_name']))
                                if verbose:
                                    print(f"{NEW_COLOR}File renamed successfully!{END_COLOR}")
                    else:
                        file.rename(file.with_name(names['new_name']))  # Apply the name change
                        if verbose:
                            print(f"{NEW_COLOR}File renamed successfully!{END_COLOR}")
                break

            elif args.exit:
                print("Exiting interactive mode.")
                break

            else:
                current_snapshot: dict = {file: names['new_name'] for file, names in files_to_process.items()}
                history.append(current_snapshot)

                actions = args.ordered_args if hasattr(args, 'ordered_args') else []
                for arg, values in actions:
                    for file, names in files_to_process.items():
                        names['new_name'] = process_filename(names['new_name'], arg, values, args)

        except SystemExit:  # Catch argparse exiting due to invalid input
            print("\033[91mInvalid input. Please try again.\033[0m")  # Red error message
        except KeyboardInterrupt:  # Handle Ctrl+C gracefully
            print("\nExiting interactive mode.")
            break

def create_parser(interactive_mode: bool = False):
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(description="Batch rename files.")
    # Add command-line arguments
    if not interactive_mode:
        parser.add_argument("target", type=str, help="File or directory to rename. Use '.' for the current directory.")

    renaming_group = parser.add_argument_group('Renaming Options', 'Options for renaming files')
    renaming_group.add_argument("-p", "--prefix", type=str, action=OrderedAction, help="Add this prefix to filenames.")
    renaming_group.add_argument("-s", "--suffix", type=str, action=OrderedAction, help="Add this suffix to filenames before the extension.")
    renaming_group.add_argument("-r", "--replace", action=ReplaceAction, nargs='+', help="Replace old text with new text in filenames.")
    renaming_group.add_argument("-e", "--replace-ext", nargs='+', action=ReplaceAction, help="Replace file extensions (e.g., .txt .md).")
    renaming_group.add_argument("-x", "--replace-regex", action=ReplaceAction, nargs='+', help="Use regex to replace a pattern in filenames.")
    renaming_group.add_argument("-ri", "--replace-index", nargs=3, action=ReplaceAction, metavar=('SEPARATOR', 'INDEX', 'NEW_TEXT'), help="Replace the word at INDEX with NEW_TEXT using SEPARATOR.")
    
    renaming_group.add_argument("-I", "--insert-text", action=OrderedAction, nargs=3, metavar=('TEXT', 'POSITION', 'INDEX'), help="Insert TEXT at POSITION in the filename.")
    # renaming_group.add_argument("-H", "--hash", action=OrderedAction, nargs='?', const='md5', type=str, choices=['md5', 'sha256'], help="Generate a hash of the filename and append or prepend it.")

    selection_group = parser.add_argument_group('File Selection Options', 'Options for selecting which files to rename')
    selection_group.add_argument("-t", "--ext", action="append", type=extension_type, help="Only rename files with these extensions (e.g., --ext .txt --ext .jpg).")
    if not interactive_mode:
        selection_group.add_argument("-R", "--recursive", action="store_true", help="Recursively rename files in subdirectories (if target is a directory).")
    # if not interactive_mode:
    preview_group = parser.add_argument_group('Preview and Confirmation Options', 'Options for previewing and confirming changes')
    preview_group.add_argument("--preview", action="store_true", help="Preview changes without renaming files.")
    preview_group.add_argument("--verbose", action="store_true", help="Display detailed renaming information.")
    preview_group.add_argument("--confirm", action="store_true", help="Prompt for confirmation before renaming each file.")
    
    
    interactive_group = parser.add_argument_group('Interactive Mode Options', 'Options for interactive renaming mode')
    if not interactive_mode:
        interactive_group.add_argument("-i", "--interactive", action="store_true", help="Enable interactive renaming mode.")
    if interactive_mode:
        interactive_group.add_argument("-q", "--exit", action="store_true", help="Exit interactive mode.")
        interactive_group.add_argument("-a", "--apply", action="store_true", help="Apply changes in interactive mode.")
        interactive_group.add_argument("-u", "--undo", action="store_true", help="Undo the last change in interactive mode.")
    
    formatting_group = parser.add_argument_group('Formatting Options', 'Options for formatting filenames')
    formatting_group.add_argument("--case", nargs="+", action=OrderedAction, choices=['pascal', 'snake', 'camel', 'title', 'kebab', 'space', '--ignore-caps', ''], help="Convert case. Specify the source and target case, e.g., 'snake camel', 'pascal snake'.")
    # formatting_group.add_argument("--camel-to-snake", nargs=0, action=OrderedAction, help="Convert CamelCase to snake_case")
    # formatting_group.add_argument("--snake-to-camel", nargs=0, action=OrderedAction, help="Convert snake_case to PascalCase")
    # formatting_group.add_argument("--snake-to-pascal", nargs=0, action=OrderedAction, help="Convert snake_case to camelCase")
    formatting_group.add_argument("--remove-zeros", nargs=0, action=OrderedAction, help="Remove leading zeros from numbers")
    formatting_group.add_argument("--add-zeros", nargs=1, type=int, action=OrderedAction, help="Add leading zeros to numbers")
    formatting_group.add_argument("--uppercase", nargs=0, action=OrderedAction, help="Convert filename to uppercase")
    formatting_group.add_argument("--lowercase", nargs=0, action=OrderedAction, help="Convert filename to lowercase")
    formatting_group.add_argument("--title-case", nargs=0, action=OrderedAction, help="Convert filename to Titlecase")
    formatting_group.add_argument("--remove-numbers", nargs=0, action=OrderedAction, help="Remove all digits from the filename")
    formatting_group.add_argument("--standardize-dates", nargs=0, action=OrderedAction, help="Convert dates like DD-MM-YYYY to YYYY-MM-DD")
    formatting_group.add_argument("--trim", nargs=0, action=OrderedAction, help="Trim leading and trailing spaces")
    formatting_group.add_argument("--replace-spaces", nargs=0, action=OrderedAction, help="Replace spaces with underscores")
    formatting_group.add_argument("--remove-special", nargs=0, action=OrderedAction, help="Remove special characters except letters, numbers, dots, and underscores")
    formatting_group.add_argument("--clean", nargs=0, action=OrderedAction, help="Remove unwanted characters (e.g., spaces, extra underscores).")
    formatting_group.add_argument("--remove-non-ascii", nargs=0, action=OrderedAction, help="Remove all non-ASCII characters from the filename")
    formatting_group.add_argument("--add-timestamp", nargs='+', action=OrderedAction, choices=['year', 'month', 'day', 'hour', 'minute', 'second', 'full'], help="Append a timestamp to the filename with specified granularity")
    # formatting_group.add_argument("--shorten", type=int, action=OrderedAction, help="Shorten the filename to fit within the max length, preserving the extension")
    formatting_group.add_argument("--remove-duplicates", action=OrderedAction, nargs=0, help="Remove duplicate words in the filename.")
    # formatting_group.add_argument("--limit-words", type=int, action=OrderedAction, help="Limit the number of words in the filename to a specified maximum.")
    formatting_group.add_argument("--reverse", action=OrderedAction, nargs=0, help="Reverse the entire filename or just the base name.")
    
    formatting_group.add_argument("--ignore-extension", action="store_true", help="Apply formatting to the entire filename, including the extension.")
    return parser



def main():
    parser = create_parser()

    args = parser.parse_args()
    extensions = {ext.lower() for ext in args.ext} if args.ext else None

    target_path = Path(args.target).resolve()

    if args.interactive:
        interactive_rename(target_path, args, target_path, extensions)
        #     sys.exit(1)
    else:
        if target_path.is_file():
            # Single file mode
            if extensions and target_path.suffix.lower() not in extensions:
                print(f"⚠️ Skipping {target_path} (does not match specified extensions: {extensions})")
                return
            
            rename_file(target_path, args, target_path)
        elif target_path.is_dir():
            # Directory mode
            rename_files(target_path, args, extensions, target_path)
        else:
            print(f"❌ Error: {args.target} is not a valid file or directory.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()