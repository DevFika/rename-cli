import argparse
from.rename_functions import *

commands = {
    "replace": {
        "args": [
            {"name": "old_text", "required": True},  # Required argument
            {"name": "new_text", "required": False, "default": ""}  # Optional argument with default value
        ]
    },
    "uppercase": {
        "args": []  # No arguments needed
    },
    "lowercase": {
        "args": []  # No arguments needed
    },
    "add_zeros": {
        "args": []  # No arguments needed
    },
    "remove_zeros": {
        "args": []  # No arguments needed
    }
}

flags = ["ext"]

class CommandHandler:
    def __init__(self, input_command):
        self.input_field = input_command

    def handle_input(self) -> None:
        command_str = self.input_field.strip()
        parts = command_str.split()

        if not parts:
            return

        self.flags, cleaned_parts = self.preprocess_flags(parts)
        print(f"flags {self.flags}")
        print(f"cleaned_parts {cleaned_parts}")

        commands_args = self.parse_commands(cleaned_parts)

        for command, args in commands_args:
            command_name = command.lstrip('-')  # Strip leading dash
            if command_name not in commands:
                print(f"Unknown command: {command_name}")
                continue

            command_info = commands[command_name]
            expected_args = command_info["args"]

            # Fill in missing optional arguments with their default values
            filled_args = self.fill_arguments(args, expected_args)

            # Execute the command with the filled arguments
            self.execute_command(command_name, filled_args, self.flags)

    def preprocess_flags(self, parts):
        flags = []
        cleaned_parts = []

        for part in parts:
            if part.startswith("--"):
                flags.append(part.lstrip("-"))
            else:
                cleaned_parts.append(part)

        return flags, cleaned_parts

    def parse_commands(self, parts):
        commands_args = []
        current_command = None
        current_args = []

        for part in parts:
            if part.startswith("-"):
                if current_command:
                    commands_args.append((current_command, current_args))
                current_command = part
                current_args = []
            else:
                current_args.append(part)

        if current_command:
            commands_args.append((current_command, current_args))

        return commands_args

    def fill_arguments(self, provided_args, expected_args):
        """Fill provided arguments with defaults for optional arguments."""
        filled_args = []

        for index, arg_info in enumerate(expected_args):
            if index < len(provided_args):
                filled_args.append(provided_args[index])
            elif not arg_info["required"]:
                filled_args.append(arg_info.get("default", ""))
            else:
                print(f"Missing required argument: {arg_info['name']}")
                filled_args.append(None)  # You could also raise an error here

        return filled_args

    def execute_command(self, command_name, args, flags):
        if command_name == "replace":
            self.replace(args[0], args[1])
        elif command_name == "uppercase":
            to_uppercase()
        elif command_name == "lowercase":
            self.lowercase()
        elif command_name == "add_zeros":
            self.add_zeros()
        elif command_name == "remove_zeros":
            self.remove_zeros()

    def replace(self, old_text, new_text):
        print(f"Replacing '{old_text}' with '{new_text}'")

    def uppercase(self):
        print("Uppercasing text")

    def lowercase(self):
        print("Lowercasing text")

    def add_zeros(self):
        print("Adding zeros")

    def remove_zeros(self):
        print("Removing zeros")

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

def extension_type(value):
    """Ensure extensions start with a dot."""
    if not value.startswith('.'):
        raise argparse.ArgumentTypeError(f"Extension must start with a dot (e.g., '.txt').")
    return value.lower()

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
    formatting_group.add_argument("--case-flip", nargs=0, action=OrderedAction, help="")
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
    formatting_group.add_argument("--add-resolution", nargs=1, action=OrderedAction, choices=['exact', 'tag'], help="Append a resolution or tag to the filename")
    formatting_group.add_argument("--remove-resolution", nargs=1, action=OrderedAction, choices=['exact', 'tag'], help="Append a resolution or tag to the filename")
    formatting_group.add_argument("--remove-leading", nargs=1, action=OrderedAction, help="")
    formatting_group.add_argument("--remove-repeating", nargs="+", action=OrderedAction, help="")
    formatting_group.add_argument("--remove-repeating-connected", nargs=1, action=OrderedAction, help="")
    formatting_group.add_argument("--remove-trailing", nargs=1, action=OrderedAction, help="")
    
    formatting_group.add_argument("--add-image-info", nargs="+", action=OrderedAction, choices=['type', 'bits', ""], help="Append a resolution or tag to the filename")
    formatting_group.add_argument("--ignore-extension", action="store_true", help="Apply formatting to the entire filename, including the extension.")
    return parser