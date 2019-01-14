import io
import os
import sublime
import sublime_plugin
import subprocess
import tempfile
import time


def path_contains_pattern(file_path, pattern):
    """Return True if file_path contains pattern anywhere except the filename itself."""
    path = os.path.dirname(os.path.normpath(file_path))
    pattern = os.path.normpath(pattern)

    pattern_toks = pattern.split(os.sep)
    if len(pattern_toks) == 0:
        return False

    pat_i = 0
    for path_tok in path.split(os.sep):
        if path_tok != pattern_toks[pat_i]:
            pat_i = 0
            continue

        if pat_i == len(pattern_toks) - 1:
            return True

        pat_i += 1

    return False


def find_fmt_config(src_path):
    formatters = sublime.load_settings("SublimeFmt.sublime-settings").get(
        "formatters", []
    )
    for config in formatters:
        if path_matches_formatter(src_path, config):
            return config

    return None


def path_matches_formatter(src_path, config):
    """Return True if the given formatter matches the provided path"""

    # Extension filter
    if "extensions" not in config:
        return False

    _, ext = os.path.splitext(src_path)
    if ext not in config["extensions"]:
        return False

    # Path inclusion filter
    include_patterns = config.get("folder_include_patterns", [])
    if len(include_patterns) > 0:
        if not any(
            path_contains_pattern(src_path, pattern) for pattern in include_patterns
        ):
            return False

    # Path exclusion filter
    exclude_patterns = config.get("folder_exclude_patterns", [])
    if any(path_contains_pattern(src_path, pattern) for pattern in exclude_patterns):
        return False

    return True


class SublimeFmtCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        start = time.time()

        src_path = self.view.file_name()
        config = find_fmt_config(src_path)
        fmt_cmd = config["cmd"]
        if fmt_cmd is None:
            return

        cwd = os.path.dirname(src_path)

        region = sublime.Region(0, self.view.size())
        contents = self.view.substr(region)

        # Copy the view buffer into a tempfile, pass the contents to the formatter
        # command.
        fd, p = tempfile.mkstemp(dir=cwd)
        try:
            os.write(fd, bytes(contents, "UTF-8"))
            os.close(fd)

            cmd = '%s "%s"' % (fmt_cmd, p)
            if config.get("use_stdin", False):
                cmd = '%s < "%s"' % (fmt_cmd, p)

            formatted = subprocess.check_output(cmd, shell=True, cwd=cwd).decode(
                "UTF-8"
            )
            self.view.replace(edit, region, formatted)
        finally:
            # Ensure that the tempile fd is closed, and that the tempfile is removed.
            try:
                os.close(fd)
            except OSError:
                pass

            os.unlink(p)

        print("SublimeFmt executed in %.3fs" % (time.time() - start))


class SublimeFmtListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        view.run_command("sublime_fmt")
