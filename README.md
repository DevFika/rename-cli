# rename-cli

**rename-cli** is a versatile command-line tool for renaming files in bulk. It supports various renaming operations, including text replacements, adding prefixes and suffixes, filtering by file extensions, and more. The tool can operate on individual files or recursively rename files in directories.  It also offers interactive mode for step-by-step renaming.

## Features

- **Batch Renaming:**: Rename multiple files based on specified patterns or transformations.
- **Interactive Mode:**: Step-by-step renaming, including options to undo, apply, and confirm changes before they are made.
- **Text Replacement**: Replace specific parts of filenames with custom text (simple and regex replacements supported).
- **Extension Filtering**: Apply renaming only to files with specific extensions.
- **Recursive Renaming**: Rename files in subdirectories.
- **Preview Mode**: Preview changes without renaming files.
- **Verbose Output**: Display detailed renaming information.
- **Filename Formatting:** Offers various options for formatting filenames (camelCase, snake_case, uppercase, lowercase, title case, trimming, etc.).
- **Prefix and Suffix**: Add custom prefixes and suffixes to filenames.
- **Confirmation Prompt**: Prompt for confirmation before renaming each file.
- **Color-Coded Output**: Easily distinguish between old and new filenames.
- **Index-based Replacement:** Replace words at specific indices.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/DevFika/rename-cli.git
   cd rename-cli
   ```
2. **Dependencies**:
   Ensure you have Python 3.x installed. This tool uses standard Python libraries.

## Arguments

| Argument             | Description                                                                                       | Example                                             |
|----------------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| General Arguments                                                                                                                                                             |
| `<target>`       | **Required**. The file or directory to rename. Use `.` for the current directory.                 | `./files`                                        |
| `--preview`           | Preview the changes without renaming the files.                                                   | `--preview`                                         |
| `--verbose`           | Display detailed information about each renaming operation.                                       | `--verbose`                                         |
| `--confirm`           | Prompt for confirmation before renaming each file.                                                | `--confirm`                                         |
| `-R, --recursive`           | Recursively rename files in subdirectories (if target is a directory).                                                | `-R`                                         |
| `-i, --interactive`           | Enable interactive renaming mode.                                                | `-i`                                         |
| Renaming Options                                                                                                                                                             |
| `-r, --replace`       | Apply text replacements in filenames. Can be used multiple times. Replaces `old` with `new`.       | `-r old_text new_text`                              |
| `-e, --replace-ext`       | Replace file extensions. Replaces `old` with `new`.                                           | `--replace-ext .png .txt`                             |
| `-x, --replace-regex`       | Replace text by pattern. Replaces `old` with `new`.                                           | `--replace-regex '\d' X`                             |
| `-p, --prefix`            | Add a prefix to all filenames.                                                                    | `--prefix new_`                                   |
| `-s, --suffix`            | Add a suffix before the file extension.                                                           | `--suffix _v2`                                    |
| `-R, --recursive`     | Recursively rename files in subdirectories (if target is a directory).                            | `-R`                                                |
| `-t, --ext`               | Only rename files with specific extensions. Can be used multiple times.                            | `--ext .txt --ext .jpg`                             |
| Filtering Options                                                                                                                                                             |
| `-t, --ext`       | 	Only rename files with these extensions. Can be used multiple times.                |                                         |
| Interactive Mode Options                                                                                                                                                             |
| `-q, --exit`       | 	Exit interactive mode.                |                                         |
| `-a, --apply`       | 	Apply changes in interactive mode.                |                                         |
| `-u, --undo`       | 	Undo the last change.                |                                         |
| Formatting Options                                                                                                                                                             |
| `--camel-to-snake`       | 	Convert CamelCase to snake_case.                |                                         |
| `--snake-to-camel`       | 	Convert snake_case to camelCase.                |                                         |
| `--snake-to-pascal`       | 	Convert snake_case to PascalCase.                |                                         |
| `--remove-zeros`       | 	Remove leading zeros from numbers.                |                                         |
| `--add-zeros`       | 	Add leading zeros to numbers.                |                                         |
| `--uppercase`       | 	Convert filename to uppercase.                |                                         |
| `--lowercase`       | 		Convert filename to lowercase.                |                                         |
| `--title-case`       | 		Convert filename to Title Case.                |                                         |
| `--remove-numbers`       | 	Remove all digits from the filename.                |                                         |
| `--standardize-dates`       | 	Convert dates like DD-MM-YYYY to YYYY-MM-DD.                |                                         |
| `--trim`       | 	Trim leading and trailing spaces.               |                                         |
| `--replace-spaces`       | 	Replace spaces with underscores.                |                                         |
| `--remove-special`       | 	Remove special characters except letters, numbers, dots, and underscores.                |                                         |
| `--clean`       | 		Remove unwanted characters (e.g., spaces, extra underscores).                |                                         |
| `--remove-non-ascii`       | 	Remove all non-ASCII characters.                |                                         |
| `--add-timestamp`       | 	Append a timestamp (year, month, day, hour, minute, second, or full).                |                                         |
| `--reverse`       | 	Reverse the entire filename or just the base name.                |                                         |
| `--ignore-extension`       | 	Apply formatting to the entire filename, including the extension.                |                                         |
## Examples

Interactive Renaming Mode
```bash
python rename.py ./files -i
```
Rename Files with Text Replacement and Prefix/Suffix
```bash
python rename.py ./files -r old_text new_text --prefix new_ --suffix _v2
```
Recursively Rename Files by Extension
```bash
python rename.py ./files -r old_text new_text --ext .txt -R
```
Replace Text Using Regular Expressions: Replace all digits (\d) with X in filenames.
```bash
python rename.py ./files --replace-regex '\d' X
```
Convert Filename to Uppercase: Change all letters in the filename to uppercase.
```bash
python rename.py ./files --uppercase
```
## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.