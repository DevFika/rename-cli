import re
import os
from datetime import datetime


class FileFilter:
    def __init__(self, filters: dict):
        self.ext_filter = filters.get("ext", None)
        self.regex_filter = filters.get("regex", None)
        self.prefix_filter = filters.get("prefix", None)
        self.size_filter = filters.get("size", None)  # (min_size, max_size)
        self.date_filter = filters.get("date", None)  # (min_date, max_date)

    def filter(self, abs_path, file_name):
        if self.ext_filter and not self._filter_by_extension(abs_path):
            return False  # Skip if the file doesn't match the extension filter

        if self.regex_filter and not self._filter_by_regex(file_name):
            return False  # Skip if the filename doesn't match the regex filter

        if self.prefix_filter and not self._filter_by_prefix(file_name):
            return False  # Skip if the filename doesn't start with the prefix filter

        if self.size_filter and not self._filter_by_size(abs_path):
            return False  # Skip if the file doesn't match the size filter

        if self.date_filter and not self._filter_by_date(abs_path):
            return False  # Skip if the file doesn't match the date filter

        return True

    def _filter_by_extension(self, abs_path):
        """Check if file ends with the given extension(s)"""
        if isinstance(self.ext_filter, str):
            return abs_path.endswith(self.ext_filter)
        elif isinstance(self.ext_filter, list):
            return any(abs_path.endswith(ext) for ext in self.ext_filter)
        return False

    def _filter_by_regex(self, file_name):
        """Check if file name matches the given regex pattern"""
        try:
            return bool(re.search(self.regex_filter, file_name))
        except re.error:
            raise ValueError(f"Invalid regex pattern: {self.regex_filter}")

    def _filter_by_prefix(self, file_name):
        """Check if file name starts with the given prefix"""
        return file_name.startswith(self.prefix_filter)

    def _filter_by_size(self, abs_path):
        """Check if file size is within the given size range (min_size, max_size)"""
        min_size, max_size = self.size_filter
        file_size = os.path.getsize(abs_path)
        return (min_size is None or file_size >= min_size) and (max_size is None or file_size <= max_size)

    def _filter_by_date(self, abs_path):
        """Check if file's last modified date is within the given date range (min_date, max_date)"""
        file_mod_time = os.path.getmtime(abs_path)
        file_mod_date = datetime.fromtimestamp(file_mod_time)

        min_date, max_date = self.date_filter

        if min_date and file_mod_date < min_date:
            return False
        if max_date and file_mod_date > max_date:
            return False
        return True
