import argparse
from pathlib import Path
import sys
import re


RED = "\033[91m"
GREEN = "\033[92m"
END = "\033[0m"


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
        if len(values) == 1:
            old = values[0]
            new = ""
        else:
            old, new = values[0], values[1]
        replacements = getattr(namespace, self.dest, None)
        if replacements is None:
            replacements = []
            setattr(namespace, self.dest, replacements)
        replacements.append((old, new))


def confirm_rename(old_name, new_name):
    """Interactive confirmation for renaming."""
    confirm = input(f"Rename {old_name} to {new_name}? (y/n): ")
    if confirm.lower() != 'y':
        print(f"{RED}Skipping renaming of {old_name}{END}")
        return False
    return True


def rename_file(path, replacements, args, target_path, ext_replace):
    """Renames a single file based on user-defined rules."""
    if not path.is_file():
        print(f"❌ Error: {path} is not a valid file.", file=sys.stderr)
        return
    
    prefix = args.prefix
    suffix = args.suffix
    preview = args.preview
    verbose = args.verbose
    confirm = args.confirm
    clean = args.clean
    
    new_name = path.name
    replacements_copy = replacements.copy()
    ext_replace_copy = ext_replace.copy()

    log = False
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--clean":
            if log: print("Doing clean")
            new_name = clean_filename(new_name)
        elif arg == "--replace" and replacements_copy:
            if log: print("Doing Replace")
            old, new = replacements_copy.pop(0)
            new_name = new_name.replace(old, new)
        elif arg == "--ext-replace":
            if log: print("Doing extension Replace")
            old_ext, new_ext = ext_replace_copy
            if new_name.endswith(old_ext):
                new_name = new_name.replace(old_ext, new_ext)
        elif arg == "--prefix":
            if log: print("Doing prefix")
            new_name = prefix + new_name
        elif arg == "--suffix":
            if log: print("Doing suffix")
            new_name = f"{Path(new_name).stem}{suffix}{path.suffix}"

    # if clean:
    #     new_name = clean_filename(path)

    # Apply text replacements
    # if replacements:
    #     for old, new in replacements:
    #         new_name = new_name.replace(old, new)

    # if ext_replace:
    #     old_ext, new_ext = ext_replace
    #     if new_name.endswith(old_ext):
    #         new_name = new_name.replace(old_ext, new_ext)


    # Apply prefix and suffix
    # if prefix:
    #     new_name = prefix + new_name
    # if suffix:
    #     new_name = f"{Path(new_name).stem}{suffix}{path.suffix}"

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
    print(f"{rename_text}: {RED}{relative_path}{END} -> {GREEN}{relative_new_name}{END}")

    if not preview:
        try:
            if confirm:
                if confirm_rename(path.name, new_name):  # Confirm before renaming
                    path.rename(new_path)
                    if verbose:
                        print(f"{GREEN}File renamed successfully!{END}")
            else:
                path.rename(new_path)
                if verbose:
                    print(f"{GREEN}File renamed successfully!{END}")
        except FileExistsError:
            print(f"⚠️ Error: {new_path} already exists.", file=sys.stderr)
        except PermissionError:
            print(f"⚠️ Permission denied to rename {path}.", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error renaming {path}: {e}", file=sys.stderr)


def rename_files(directory, replacements, args, extensions, target_path, ext_replace):
    """Renames multiple files in a directory based on user-defined rules and filters."""
    directory = Path(directory).resolve()

    if not directory.is_dir():
        print(f"❌ Error: {directory} is not a valid directory.", file=sys.stderr)
        return
    
    prefix = args.prefix
    suffix = args.suffix
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
            
            rename_file(path, replacements, args, target_path, ext_replace)


def main():
    parser = argparse.ArgumentParser(description="Batch rename files.")

    parser.add_argument("-t", "--target", type=str, required=True, help="File or directory to rename. Use '.' for the current directory.")
    parser.add_argument("-r", "--replace", action=ReplaceAction, nargs='+', help="Replace old text with new text in filenames.")
    parser.add_argument("--prefix", type=str, help="Add this prefix to filenames.")
    parser.add_argument("--suffix", type=str, help="Add this suffix to filenames before the extension.")
    parser.add_argument("-R", "--recursive", action="store_true", help="Recursively rename files in subdirectories (if target is a directory).")
    parser.add_argument("--ext", action="append", type=extension_type, help="Only rename files with these extensions (e.g., --ext .txt --ext .jpg).")
    parser.add_argument("--ext-replace", nargs=2, metavar=("old_extension", "new_extension"), help="Replace file extensions (e.g., .txt .md).")
    parser.add_argument("--preview", action="store_true", help="Preview changes without renaming files.")
    parser.add_argument("--verbose", action="store_true", help="Display detailed renaming information.")
    parser.add_argument("--confirm", action="store_true", help="Prompt for confirmation before renaming each file.")
    parser.add_argument("--regex-replace", nargs=2, metavar=("pattern", "replacement"), help="Use regex to replace a pattern in filenames.")
    parser.add_argument("--clean", action="store_true", help="Remove unwanted characters (e.g., spaces, extra underscores).")


    args = parser.parse_args()
    replacements = getattr(args, 'replace', [])
    ext_replace = args.ext_replace if args.ext_replace else None

    extensions = {ext.lower() for ext in args.ext} if args.ext else None


    target_path = Path(args.target).resolve()

    if target_path.is_file():
        # Single file mode
        if extensions and target_path.suffix.lower() not in extensions:
            print(f"⚠️ Skipping {target_path} (does not match specified extensions: {extensions})")
            return
        
        rename_file(target_path, replacements, args, target_path, ext_replace)
    elif target_path.is_dir():
        # Directory mode
        rename_files(target_path, replacements, args, extensions, target_path, ext_replace)
    else:
        print(f"❌ Error: {args.target} is not a valid file or directory.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
