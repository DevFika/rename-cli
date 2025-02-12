import argparse
from pathlib import Path
import sys
import re
import shlex
import os
import difflib

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
END = "\033[0m"
LIGHT_GRAY = "\033[97m"
MAGENTA = "\033[95m"
WARNING_COLOR = RED
NEW_COLOR = GREEN
ORIGINAL_COLOR = LIGHT_GRAY
PENDING_COLOR = YELLOW
PENDING_HIGHLIGHT_COLOR = GREEN
END_COLOR = END
INTERACTIVE_MODE_COLOR = MAGENTA


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
            highlighted_original += original[i1:i2]
            highlighted_new += new[j1:j2]
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


def clean_filename(name):
    """Remove unwanted characters (e.g., spaces, extra underscores)."""
    new_name = re.sub(r'[_\s]+', '_', name)  # Replace multiple spaces or underscores with a single underscore
    new_name = re.sub(r'[^a-zA-Z0-9._-]', '', new_name)  # Remove non-alphanumeric characters
    if new_name != name:
        # print(f"Renaming {path.name} to {new_name}")
        return new_name
    return name


def regex_replace_in_filenames(path, pattern, replacement):
    new_name = re.sub(pattern, replacement, path.name)
    if new_name != path.name:
        new_path = path.with_name(new_name)
        print(f"Renaming {path.name} to {new_name}")
        return new_path
    return path

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
        if arg == "clean":
            if log: print("Doing clean")
            new_name = clean_filename(new_name)
        elif arg == "replace":
            if log: print("Doing Replace")
            new_name = new_name.replace(values[0], values[1])
        elif arg == "ext_replace":
            if log: print("Doing extension Replace")
            if new_name.endswith(values[0]):
                new_name = new_name.replace(values[0], values[1])
        elif arg == "prefix":
            if log: print("Doing prefix")
            new_name = values + new_name
        elif arg == "suffix":
            if log: print("Doing suffix")
            new_name = f"{Path(new_name).stem}{values}{Path(new_name).suffix}"

    if new_name == path.name:
        if verbose:
            print(f"ℹ️ No changes needed: {path}")
        return

    new_path = path.with_name(new_name)

    # Prevent overwriting existing files
    if new_path.exists():
        print(f"⚠️  Skipping (target exists): {path} -> {new_path}")
        return

    relative_path = path.relative_to(target_path)
    relative_new_name = new_path.relative_to(target_path)

    rename_text = "Renaming" if not preview else "Preview"
    print(f"{rename_text}: {ORIGINAL_COLOR}{relative_path}{END_COLOR} -> {PENDING_COLOR}{relative_new_name}{END_COLOR}")

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
            clear_terminal()
            # Show the current preview of the filenames
            for file, names in files_to_process.items():
                original_name = f"{names['original_name']}"
                new_name = f"{names['new_name']}"
                highlighted_original, highlighted_new = highlight_changes(original_name, new_name)
                print(f"Preview: {highlighted_original} -> {highlighted_new}")

            print(f"{NEW_COLOR}--apply{END_COLOR}: Apply all changes, "
                f"{WARNING_COLOR}--exit{END_COLOR}: Quit, "
                f"{PENDING_COLOR}--confirm{END_COLOR}: Review & apply individually, "
                f"{CYAN}--undo{END_COLOR}: Revert last change.")


            user_input = input(f"{INTERACTIVE_MODE_COLOR}Interactive Mode{END_COLOR}: ").strip()

            parser = create_parser(interactive_mode=True)

            args = parser.parse_args(shlex.split(user_input))

            extensions = {ext.lower() for ext in args.ext} if args.ext else None

            preview = args.preview
            
            if args.undo:
                if history:
                    print(history)
                    last_snapshot = history.pop()
                    print(last_snapshot)
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
                log = True
                for arg, values in actions:
                    if arg == "clean":
                        if log: print("Doing clean")
                        for file, names in files_to_process.items():
                            names['new_name'] = clean_filename(names['new_name'])
                    elif arg == "replace":
                        if log: print("Doing Replace")
                        old, new = values[0], values[1]
                        for file, names in files_to_process.items():
                            names['new_name'] = names['new_name'].replace(old, new)
                    elif arg == "ext_replace":
                        if log: print("Doing extension Replace")
                        old_ext, new_ext = values[0], values[1]
                        for file, names in files_to_process.items():
                            if names['new_name'].endswith(old_ext):
                                names['new_name'] = names['new_name'].replace(old_ext, new_ext)
                    elif arg == "prefix":
                        if log: print("Doing prefix")
                        for file, names in files_to_process.items():
                            names['new_name'] = values + names['new_name']
                    elif arg == "suffix":
                        if log: print("Doing suffix")
                        for file, names in files_to_process.items():
                            names['new_name'] = f"{Path(names['new_name']).stem}{values}{Path(names['new_name']).suffix}"
                        
            # Show the updated previews after each command
            print("\nUpdated Previews:")
            for file, names in files_to_process.items():
                print(f"{PENDING_COLOR}{names['new_name']}{END_COLOR}")
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
        parser.add_argument("-T", "--target", type=str, required=True, help="File or directory to rename. Use '.' for the current directory.")
    parser.add_argument("--replace", action=ReplaceAction, nargs='+', help="Replace old text with new text in filenames.")
    parser.add_argument("--prefix", type=str, action=OrderedAction, help="Add this prefix to filenames.")
    parser.add_argument("--suffix", type=str, action=OrderedAction, help="Add this suffix to filenames before the extension.")
    if not interactive_mode:
        parser.add_argument("-R", "--recursive", action="store_true", help="Recursively rename files in subdirectories (if target is a directory).")
    
    parser.add_argument("--ext", action="append", type=extension_type, help="Only rename files with these extensions (e.g., --ext .txt --ext .jpg).")
    parser.add_argument("--ext-replace", nargs='+', action=ReplaceAction, help="Replace file extensions (e.g., .txt .md).")
    # if not interactive_mode:
    parser.add_argument("--preview", action="store_true", help="Preview changes without renaming files.")
    parser.add_argument("--verbose", action="store_true", help="Display detailed renaming information.")
    parser.add_argument("--confirm", action="store_true", help="Prompt for confirmation before renaming each file.")
    parser.add_argument("--regex-replace", nargs=2, metavar=("pattern", "replacement"), help="Use regex to replace a pattern in filenames.")
    parser.add_argument("--clean", nargs=0, action=OrderedAction, help="Remove unwanted characters (e.g., spaces, extra underscores).")
    if not interactive_mode:
        parser.add_argument("--interactive", action="store_true", help="Enable interactive renaming mode.")
    if interactive_mode:
        parser.add_argument("--exit", action="store_true", help="Exit interactive mode.")
        parser.add_argument("--apply", action="store_true", help="Apply changes in interactive mode.")
        parser.add_argument("--undo", action="store_true", help="Undo the last change in interactive mode.")
    return parser

def main():
    parser = create_parser()

    args = parser.parse_args()
    if hasattr(args, 'ordered_args'):
        for arg, values in args.ordered_args:
            print(arg, values)
            # print(values)
    replacements = getattr(args, 'replace', [])
    replacements = [] if replacements is None else replacements
    ext_replace = getattr(args, 'ext_replace', [])
    ext_replace = [] if ext_replace is None else ext_replace
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