# rename-cli

**rename-cli** is a versatile command-line tool for renaming files in bulk. It supports various renaming operations, including text replacements, adding prefixes and suffixes, and filtering by file extensions. The tool can operate on individual files or recursively rename files in directories.

## Features

- **Text Replacement**: Replace specific text in filenames.
- **Prefix and Suffix**: Add custom prefixes and suffixes to filenames.
- **Extension Filtering**: Rename only files with specified extensions.
- **Recursive Operation**: Rename files in subdirectories.
- **Preview Mode**: Preview changes without renaming files.
- **Verbose Output**: Display detailed renaming information.
- **Confirmation Prompt**: Prompt for confirmation before renaming each file.
- **Color-Coded Output**: Easily distinguish between old and new filenames.

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
| `-t, --target`        | **Required**. The file or directory to rename. Use `.` for the current directory.                 | `-t ./files`                                        |
| `-r, --replace`       | Apply text replacements in filenames. Can be used multiple times. Replaces `old` with `new`.       | `-r old_text new_text`                              |
| `--prefix`            | Add a prefix to all filenames.                                                                    | `--prefix new_`                                   |
| `--suffix`            | Add a suffix before the file extension.                                                           | `--suffix _v2`                                    |
| `-R, --recursive`     | Recursively rename files in subdirectories (if target is a directory).                            | `-R`                                                |
| `--ext`               | Only rename files with specific extensions. Can be used multiple times.                            | `--ext .txt --ext .jpg`                             |
| `--ext-replace`       | Replace file extensions. Replaces `old` with `new`.                                           | `--ext-replace old_ext new_ext`                             |
| `--preview`           | Preview the changes without renaming the files.                                                   | `--preview`                                         |
| `--verbose`           | Display detailed information about each renaming operation.                                       | `--verbose`                                         |
| `--confirm`           | Prompt for confirmation before renaming each file.                                                | `--confirm`                                         |


## Examples

Rename Files with Text Replacement and Prefix/Suffix
```bash
python rename.py -t . -r old_text new_text --prefix PRE_ --suffix _SUF
```
Recursively Rename Files with Specific Extensions
```bash
python rename.py -t . -r old_text new_text --ext .txt --ext .jpg -R
```
Preview Changes Without Renaming
```bash
python rename.py -t . -r old_text new_text --prefix PRE_ --suffix _SUF --preview
```
Rename with Verbose Output and Confirmation
```bash
python rename.py -t . -r old_text new_text --verbose --confirm
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.