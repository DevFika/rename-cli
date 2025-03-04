from typing import List
from textual.suggester import Suggester
from .command_pipeline_handler import commands, flags

class CommandSuggester(Suggester):
    """Suggester for command-line commands with argument and flag suggestions."""
    
    def __init__(self, ) -> None:
        """
        Initialize the CommandSuggester with a dictionary of commands and flags.

        Args:
            commands: A dictionary where each key is a command and its value is 
                      the argument list (with required and optional args).
            flags: A dictionary where each key is a flag and its value is its argument list.
        """
        super().__init__(use_cache=True, case_sensitive=True)
        self.commands = commands
        self.flags = flags  # Add flags to the class

    async def get_suggestion(self, value: str) -> List[str] | None:
        autocomplete_suggestions = []

        # Split the value by spaces to separate commands and arguments
        parts = value.strip().split()
        print(f"Input Parts: {parts}")  # Debug: Check how input is split

        if not parts:
            # If there's no input, show all commands and flags
            autocomplete_suggestions = [f"-{command}" for command in self.commands] + [f"--{flag}" for flag in self.flags]
            print(f"No input, showing all commands and flags: {autocomplete_suggestions}")  # Debug
        else:
            # Check for the last part in the input to see if it's a command, flag, or argument
            last_part = parts[-1]
            print(f"Last Part: {last_part}")  # Debug: Show the last part of the input

            # If input starts with '-', it's for command or flag matching
            if last_part.startswith("-"):
                last_part_without_dash = last_part.lstrip('-')
                print(f"Last Part Without Dash: {last_part_without_dash}")  # Debug: Show last part without dash

                if last_part.startswith("--"):  # For flags
                    # Match flags that start with the input (i.e., partial match)
                    matching_flags = [
                        flag for flag in self.flags if flag.startswith(last_part_without_dash)
                    ]
                    print(f"Matching Flags: {matching_flags}")  # Debug: Show matching flags
                    
                    if matching_flags:
                        for flag in matching_flags:
                            # Suggest the flag and its arguments (if any)
                            flag_name = flag  # Keep the full flag name
                            args = self.flags[flag_name]["args"] if flag_name in self.flags else []
                            suggestion = f"--{flag_name}"

                            # Add all arguments (required and optional)
                            for arg in args:
                                if arg["required"]:
                                    suggestion += f" <!:{arg['name']}>"
                                else:
                                    suggestion += f" <{arg['name']}>"
                            
                            # Append the suggestion directly to the current input
                            if len(parts) > 1:  # If more than one part, add the suggestion to the whole input
                                autocomplete_suggestions.append(f"{' '.join(parts[:-1])} {suggestion}")
                            else:
                                autocomplete_suggestions.append(suggestion)
                    else:
                        # If no matching flag, return None or leave suggestions empty
                        autocomplete_suggestions = []
                        print(f"No match found for flags, no suggestions.")  # Debug: No match found
                else:  # For commands
                    # Match commands that start with the input (i.e., partial match)
                    matching_commands = [
                        command for command in self.commands if command.startswith(last_part_without_dash)
                    ]
                    print(f"Matching Commands: {matching_commands}")  # Debug: Show matching commands
                    
                    if matching_commands:
                        # If there are matching commands, suggest them
                        for command in matching_commands:
                            # Suggest the command and its arguments (if any)
                            command_name = command  # Keep the full command
                            args = self.commands[command_name]["args"]
                            suggestion = f"-{command_name}"

                            # Add all arguments (required and optional)
                            for arg in args:
                                if arg["required"]:
                                    suggestion += f" <!:{arg['name']}>"
                                else:
                                    suggestion += f" <{arg['name']}>"
                            
                            # Append the suggestion directly to the current input
                            if len(parts) > 1:  # If more than one part, add the suggestion to the whole input
                                autocomplete_suggestions.append(f"{' '.join(parts[:-1])} {suggestion}")
                            else:
                                autocomplete_suggestions.append(suggestion)
                    else:
                        # If no matching command, return None or leave suggestions empty
                        autocomplete_suggestions = []
                        print(f"No match found for commands, no suggestions.")  # Debug: No match found
            else:
                # If the last part does not start with '-', it might be an argument or text
                # For now, do not show any command or flag suggestions when typing arguments
                autocomplete_suggestions = []
                print(f"Argument or text detected, no command or flag suggestions.")  # Debug

        # For debugging purposes, show the autocomplete suggestions
        print(f"Autocomplete Suggestions: {autocomplete_suggestions}")  # Debug
        
        # Return only the first suggestion or empty if no suggestions found
        return autocomplete_suggestions[0] if autocomplete_suggestions else None
