import re
import os


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

def remove_non_ascii(name, ignore_extension):
    """Remove all non-ASCII characters from the filename."""
    if ignore_extension:
        new_name = ''.join([char for char in name if ord(char) < 128])
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = ''.join([char for char in base_name if ord(char) < 128])
        new_name = new_base_name + ext
    return new_name

def remove_leading(name, values, ignore_extension):
    """Remove specified leading character(s) from the filename."""
    char = values[0]
    if not char:
        return name  # If no character is provided, return the original name
    
    if ignore_extension:
        return re.sub(f'^{re.escape(char)}+', '', name)

    base_name, ext = os.path.splitext(name)
    new_base_name = re.sub(f'^{re.escape(char)}+', '', base_name)
    
    return new_base_name + ext

def remove_trailing(name, values, ignore_extension):
    """Remove specified trailing character(s) from the filename."""
    char = values[0]
    if not char:
        return name  # If no character is provided, return the original name
    
    if ignore_extension:
        return re.sub(f'{re.escape(char)}+$', '', name)

    base_name, ext = os.path.splitext(name)
    new_base_name = re.sub(f'{re.escape(char)}+$', '', base_name)
    
    return new_base_name + ext

def remove_repeating(name, values, ignore_extension=False):
    """
    Remove all occurrences of a given substring except for the one at the specified index.
    
    :param name: The filename to process.
    :param substring: The substring to de-duplicate.
    :param keep_index: Which occurrence to keep (0-based index).
    :param ignore_extension: Whether to ignore the file extension while modifying the filename.
    :return: The cleaned filename.
    """
    substring = values[0]
    keep_index = int(values[1]) if len(values) > 1 else 0
    if not substring:
        return name  # Return original name if no substring provided

    base_name, ext = os.path.splitext(name)
    
    if ignore_extension:
        part_to_modify = name
    else:
        part_to_modify = base_name  # Only modify the base name

    matches = list(re.finditer(re.escape(substring), part_to_modify))

    if len(matches) <= 1:
        return name  # No need to modify if there's only one or zero occurrences

    keep_index = min(keep_index, len(matches) - 1)

    result = list(name)  # Convert to list to allow modifications
    kept_position = matches[keep_index].start()

    for match in reversed(matches):  
        if match.start() != kept_position:
            del result[match.start():match.end()]

    return "".join(result)

def remove_repeating_connected(name, values, ignore_extension=False):
    """
    Remove consecutive repetitions of a given character(s) except for the first one.
    
    :param name: The filename to process.
    :param values: A list containing the character(s) to de-duplicate and the keep index (optional).
    :param ignore_extension: Whether to ignore the file extension while modifying the filename.
    :return: The cleaned filename.
    """
    char = values[0]
    if not char:
        return name  # Return original name if no character provided

    # If the user provided a keep_index (default is 0)
    keep_index = int(values[1]) if len(values) > 1 else 0

    base_name, ext = os.path.splitext(name)
    
    # Decide whether to ignore the extension while processing
    if ignore_extension:
        part_to_modify = name
    else:
        part_to_modify = base_name  # Only modify the base name

    # Use regex to remove consecutive occurrences of the character(s)
    modified_name = re.sub(rf'{re.escape(char)}+', char, part_to_modify)  # Replace consecutive `char` with a single instance

    # After modifying, we need to reassemble the final name
    if ignore_extension:
        return modified_name  # If ignoring the extension, return the whole modified name
    else:
        return modified_name + ext  # Append the original extension


def remove_numbers(name, ignore_extension):
    """Remove all digits from the filename."""
    if ignore_extension:
        new_name = re.sub(r'\d+', '', name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'\d+', '', base_name)
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
