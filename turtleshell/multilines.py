"""This module has functions for handling control flows or statements spread across multiple lines."""

import re

pattern = r"([\"'])(?:(?=(\\?))\2.)*?\1"


def is_complete(text: str) -> bool:
    """Returns true if there's a complete statement or not."""
    # Check if the line ends with a slash
    if text.strip().endswith(" \\"):
        return False

    # Count the number of unescaped braces and brackets
    # We need to ignore anything inside a string, so for this purpose, we can pretend any strings
    #   don't exist.
    nostring_text = re.sub(pattern, "", text)

    bracket_styles = ("()", "{}")
    for bstyle in bracket_styles:
        lbrace, rbrace = bstyle
        nl = nostring_text.count(lbrace) - nostring_text.count("\\" + lbrace)
        nr = nostring_text.count(rbrace) - nostring_text.count("\\" + rbrace)
        if nl == nr + 1:
            return False

    # Default to True so we don't get stuck perpetually waiting for more input if the uer made a
    #   syntax error
    return True


def concatenate_incomplete_lines(lines: list[str]):
    """Takes a bunch of potentially-incomplete lines, and concatenates them."""
    complete_lines: list[str] = []  # Holder of complete lines
    line_buffer: str = ""  # Store parts of complete lines until we find the end of them

    for line in lines:
        if is_complete(line_buffer + line):
            complete_lines.append(line_buffer + line)
            line_buffer = ""
        else:
            if line.strip().endswith(" \\"):
                # Remove trailing '\'
                line = line.strip()[:-2]
            line_buffer += line.strip() + " "

    return " ".join(complete_lines)
