import shlex
from .rename_functions import *
import datetime

commands = {
    "replace": {
        "args": [
            {"name": "old_text", "required": True},
            {"name": "new_text", "required": False, "default": ""}
        ]
    },
    "case": {
        "args": [
            {"name": "style", "required": True}  # e.g., upper, lower, snake, camel
        ]
    },
    "add_zeros": {"args": []},
    "remove_zeros": {"args": []},
}

flags = {
    "ext": {
        "args": [
            {"name": "type", "required": True},  # Only work on the file with this extension
        ]
    },
    "regex": {
        "args": [
            {"name": "pattern", "required": True}  # Regex pattern to match file name
        ]
    },
    "prefix": {
        "args": [
            {"name": "prefix", "required": True}  # Only work on files with this prefix
        ]
    },
    "size": {
        "args": [
            {"name": "min_size", "required": False},  # Minimum file size
            {"name": "max_size", "required": False}   # Maximum file size
        ]
    },
    "date": {
        "args": [
            {"name": "min_date", "required": False},  # Minimum modification date
            {"name": "max_date", "required": False}   # Maximum modification date
        ]
    },
    "ignore-extension": {
        "args": []  # Simple flag with no args
    },
    "preserve-caps": {
        "args": []  # Simple flag with no args
    },
}



class CommandPipelineHandler:
    def __init__(self, input_command, data_manager):
        self.input_command = input_command
        self.data_manager = data_manager
        self.flags = set()
        self.process_steps = []

    def parse_and_prepare_pipeline(self):
        parts = shlex.split(self.input_command)
        print(parts)
        self.flags, cleaned_parts = self._preprocess_flags(parts)
        print(self.flags)
        print(self.flags)
        print(self.flags)
        print(self.flags)
        print(self.flags)
        print(cleaned_parts)
        commands_args = self._parse_commands(cleaned_parts)

        for command, args in commands_args:
            command_name = command.lstrip('-')
            if command_name not in commands:
                print(f"Unknown command: {command_name}")
                continue

            expected_args = commands[command_name]["args"]
            filled_args = self._fill_arguments(args, expected_args)

            step = self._create_process_step(command_name, filled_args)
            self.process_steps.append(step)

    def _preprocess_flags(self, parts):
        flags = {}
        cleaned_parts = []
        i = 0

        while i < len(parts):
            part = parts[i]

            if part.startswith("--"):
                flag_name = part.lstrip("-")
                if flag_name not in flags:
                    flags[flag_name] = []

                flag_spec = self._get_flag_spec(flag_name)

                if flag_spec:
                    for arg_spec in flag_spec.get("args", []):
                        i += 1
                        if i < len(parts):
                            flags[flag_name].append(parts[i])
                        elif arg_spec["required"]:
                            raise ValueError(f"Missing required argument for flag: --{flag_name}")

                elif flag_name in flags:  # Simple flag with no args
                    flags[flag_name] = True  # Set simple flags to True for presence
                else:
                    flags[flag_name] = True  # If it's not defined, assume simple flag

            else:
                cleaned_parts.append(part)

            i += 1

        return flags, cleaned_parts

    def _get_flag_spec(self, flag_name):
        return flags.get(flag_name, None)

    def _parse_commands(self, parts):
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

    def _fill_arguments(self, provided_args, expected_args):
        filled_args = []
        for index, arg_info in enumerate(expected_args):
            if index < len(provided_args):
                filled_args.append(provided_args[index])
            elif not arg_info["required"]:
                filled_args.append(arg_info.get("default", ""))
            else:
                raise ValueError(f"Missing required argument: {arg_info['name']}")

        return filled_args

    def _create_process_step(self, command_name, args):
        def step(filename, path):
            return self._process_filename(filename, command_name, args, path)
        return step

    def _process_filename(self, name, command_name, values, path=None):
        ignore_extension = "ignore-extension" in self.flags
        preserve_caps = "preserve-caps" in self.flags
        # ignore_extension = "ext" in self.flags


        if command_name == "case":
            style = values[0].lower()
            if style == "upper":
                return to_uppercase(name, ignore_extension)
            elif style == "lower":
                return to_lowercase(name, ignore_extension)
            elif style == "snake":
                return to_snake_case(name, ignore_extension, preserve_caps)
            elif style == "camel":
                return to_camel_case(name, ignore_extension, preserve_caps)
            elif style == "pascal":
                return to_pascal_case(name, ignore_extension, preserve_caps)
            elif style == "kebab":
                return to_kebab_case(name, ignore_extension, preserve_caps)
            elif style == "title":
                return to_title_case(name, ignore_extension, preserve_caps)
            # else:
            #     raise ValueError(f"Unknown case style: {style}")
        # elif command_name == "uppercase":
        #     return to_uppercase(name, ignore_extension)
        # elif command_name == "lowercase":
        #     return to_lowercase(name, ignore_extension)
        elif command_name == "replace":
            old_text, new_text = values
            return replace_in_filename(name, old_text, new_text, ignore_extension)
        # elif command_name == "add_zeros":
        #     return add_leading_zeros(name, ignore_extension)
        # elif command_name == "remove_zeros":
        #     return remove_leading_zeros(name, ignore_extension)

        return name  # Default to no-op if unknown command

    def process_file_names(self):
        filters = self._extract_filters_from_flags()
        self.data_manager.process_file_names(self._pipeline_callable, filters)

    def _pipeline_callable(self, new_name, abs_path):
        for step in self.process_steps:
            new_name = step(new_name, abs_path)
        return new_name
    
    def _extract_filters_from_flags(self):
        filters = {}

        # Check for the "ext" flag (can support multiple extensions)
        if "ext" in self.flags:
            extensions = self.flags["ext"]
            filters["ext"] = extensions  # List of extensions

        # Check for the "regex" flag (supporting regex filtering if provided)
        if "regex" in self.flags:
            regex_pattern = self.flags["regex"][0]
            filters["regex"] = regex_pattern

        # Check for the "prefix" flag (can support prefix filtering)
        if "prefix" in self.flags:
            prefix_value = self.flags["prefix"][0]
            filters["prefix"] = prefix_value

        # Check for the "size" flag (supports size filtering as a tuple of (min_size, max_size))
        if "size" in self.flags:
            size_values = self.flags["size"]
            min_size = int(size_values[0]) if size_values[0] else None
            max_size = int(size_values[1]) if size_values[1] else None
            filters["size"] = (min_size, max_size)

        # Check for the "date" flag (supports date filtering)
        if "date" in self.flags:
            date_values = self.flags["date"]
            min_date = datetime.strptime(date_values[0], "%Y-%m-%d") if date_values[0] else None
            max_date = datetime.strptime(date_values[1], "%Y-%m-%d") if date_values[1] else None
            filters["date"] = (min_date, max_date)

        # Add other flag-based filters as needed (e.g., file name patterns, date filters, etc.)
        if "ignore-extension" in self.flags:
            filters["ignore_extension"] = True

        return filters



