from .parser import create_parser
from argparse import ArgumentError, ArgumentParser
from ..data_manager import DataManager
from .rename_functions import *
import shlex


def process_names(input_command, data_manager: DataManager):
    try:
        pipeline_callable = _build_process_pipeline(input_command)
    except (ArgumentError, SystemExit) as e:
        # Handle invalid input (e.g., show an error message, log to console, etc.)
        print(f"Invalid command: {input_command}\nError: {e}")
        return  # Exit gracefully, don't run file processing if parsing failed

    data_manager.process_file_names(pipeline_callable)

def _build_process_pipeline(input_command) -> callable:
    parser = create_parser(interactive_mode=True)

    args_list = shlex.split(input_command)
    args = parser.parse_args(args_list)

    # Capture all the processing steps into a list
    process_steps = []

    actions = args.ordered_args if hasattr(args, 'ordered_args') else []

    for arg, values in actions:
        step = _create_process_step(arg, values, args)
        process_steps.append(step)

    # Return a single callable that applies all steps
    def process_pipeline(new_name, abs_path):
        for step in process_steps:
            new_name = step(new_name, abs_path)
        return new_name

    return process_pipeline

def _create_process_step(arg, values, args):
    """
    Returns a callable function that applies a single rename step.
    Example: step(new_name, abs_path) -> new_new_name
    """
    def step(new_name, abs_path):
        # process_filename is your existing logic that applies one command
        return _process_filename(new_name, arg, values, args, abs_path)

    return step


def _process_filename(name, arg, values, args, path=None):
    ignore_extension = args.ignore_extension
    """Apply selected transformations."""
    # if arg == "camel_to_snake":
    #     name = camel_case_to_snake_case(name, ignore_extension)
    # elif arg == "snake_to_pascal":
    #     name = snake_case_to_pascal_case(name, ignore_extension)
    # elif arg == "remove_zeros":
    #     name = remove_leading_zeros(name, ignore_extension)
    # elif arg == "add_zeros":
    #     name = add_leading_zeros_to_number(name, values[0], ignore_extension)
    if arg == "uppercase":
        name = to_uppercase(name, ignore_extension)
    elif arg == "lowercase":
        name = to_lowercase(name, ignore_extension)
    # elif arg == "remove_numbers":
    #     name = remove_numbers(name, ignore_extension)
    # elif arg == "standardize_dates":
    #     name = standardize_dates(name, ignore_extension)
    # elif arg == "trim":
    #     name = trim_filename(name, ignore_extension)
    # elif arg == "replace_spaces":
    #     name = replace_spaces_with_underscores(name, ignore_extension)
    # elif arg == "remove_special":
    #     name = remove_special_characters(name, ignore_extension)
    # elif arg == "remove_non_ascii":
    #     name = remove_non_ascii(name, ignore_extension)
    # elif arg == "add_timestamp":
    #     name = add_timestamp(name, values[0], ignore_extension)
    # elif arg == "title_case":
    #     name = to_title_case(name, ignore_extension)
    # elif arg == "clean":
    #     name = clean_filename(name, ignore_extension)
    # elif arg == "replace":
    #     name = replace_in_filename(name, values[0], values[1], ignore_extension)
    # elif arg == "replace_ext":
    #     name = regex_replace_in_filenames(name, r'\.' + re.escape(values[0]) + '$', '.' + values[1], ignore_extension)
    # elif arg == "replace_regex":
    #     name = regex_replace_in_filenames(name, values[0], values[1], ignore_extension)
    # elif arg == "replace_index":
    #     name = replace_word_by_index(name, values[0], int(values[1]), values[2], ignore_extension)
    # elif arg == "prefix":
    #     name = add_prefix(name, values, ignore_extension)
    # elif arg == "suffix":
    #     name = add_suffix(name, values, ignore_extension)
    # elif arg == "remove_duplicates":
    #     name = remove_duplicate_words(name, ignore_extension)
    # elif arg == "limit_words":
    #     name = limit_word_count(name, values, ignore_extension)
    # elif arg == "insert_text":
    #     name = insert_text_at_position(name, values[0], int(values[1]), ignore_extension)
    # elif arg == "reverse":
    #     name = reverse_string(name, ignore_extension)
    # elif arg == "case":
    #     name = convert_to_case(name, values[0], ignore_extension)
    #     # name = handle_case(name, values, ignore_extension)
    # elif arg == "add_resolution":
    #     name = add_resolution(name, values, ignore_extension, path)
    # elif arg == "remove_resolution":
    #     name = remove_resolution(name, values, ignore_extension)
    # elif arg == "remove_leading":
    #     name = remove_leading(name, values, ignore_extension)
    # elif arg == "remove_trailing":
    #     name = remove_trailing(name, values, ignore_extension)
    # elif arg == "remove_repeating":
    #     name = remove_repeating(name, values, ignore_extension)
    # elif arg == "remove_repeating_connected":
    #     name = remove_repeating_connected(name, values, ignore_extension)
    # elif arg == "add_image_info":
    #     name = add_image_info(name, values, ignore_extension, path)
    # elif arg == "case_flip":
    #     name = flip_case(name, ignore_extension)

    # elif arg == "hash":
    #     name = hash_filename(name, values[0], ignore_extension)

    return name