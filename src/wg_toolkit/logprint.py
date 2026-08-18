"""

# Description:

This module provides enhanced logging functions that print messages
with timestamps and color coding to the terminal.

## Functions:

printc,
print_log,
print_info,
print_warning,
print_attention,
print_error,
print_done,
print_success,

## Recomended use
```
from wg_toolkit.logprint import print_log, print_info, print_warning, print_error


"""

from datetime import datetime


def _timenow() -> str:
    # Private copy to avoid circular import with misc.py. Public version: wg_toolkit.misc.timenow
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

__all__ = [
    "print_attention",
    "print_available_colors",
    "print_done",
    "print_error",
    "print_info",
    "print_log",
    "print_success",
    "print_warning",
    "printc",
]

_ANSI_escape_color_codes = {
    "": "0",  # Default terminal color
    # Normal (30-37)
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "purple": "35",  # magenta
    "cyan": "36",
    "white": "37",
    # Bright (90-97)
    "gray": "90",  # bright black
    "bright_red": "91",
    "bright_green": "92",
    "bright_yellow": "93",
    "bright_blue": "94",
    "bright_purple": "95",  # bright magenta
    "bright_cyan": "96",
    "bright_white": "97",
    "bg_black": "40",  # background colors have the bg_ prefix
    "bg_red": "41",
    "bg_green": "42",
    "bg_yellow": "43",
    "bg_blue": "44",
    "bg_purple": "45",  # magenta
    "bg_cyan": "46",
    "bg_white": "47",
    # Bright (100-107)
    "bg_gray": "100",  # bright black
    "bg_bright_red": "101",
    "bg_bright_green": "102",
    "bg_bright_yellow": "103",
    "bg_bright_blue": "104",
    "bg_bright_purple": "105",  # bright magenta
    "bg_bright_cyan": "106",
    "bg_bright_white": "107",
}

# the available colors are described in https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit

# Range	Meaning
# 30-37	foreground, normal
# 40-47	background, normal
# 90-97	foreground, bright
# 100-107	background, bright


def logprint_available_colors():
    """Print the available colors and their corresponding ANSI escape codes."""
    print("Available colors:")
    for color, code in _ANSI_escape_color_codes.items():
        print(f"{color}: \033[{code}mSample Text\033[0m")

def printc(s: str, color: str = "", bold: bool = False, end: str = "\n", flush: bool = True, verbose: bool = True):
    """Print `s` to stdout wrapped in ANSI color/bold escape codes.

    Parameters
    ----------
    s : str
        The input string to colorize.
    color : str, optional
        Color name. Use `logprint_available_colors()` to see the available colors. Default is no color.
    bold : bool, optional
        If True, make the text bold.
    end : str, optional
        String appended after the last character. Default is newline.
    flush : bool, optional
        Whether to flush the output buffer.
    verbose : bool, optional
        If False, suppress printing.
    """

    if not verbose:
        return

    if color not in _ANSI_escape_color_codes:
        raise ValueError(f"Invalid color '{color}'. Valid options are: {list(_ANSI_escape_color_codes.keys())}")

    color_code = _ANSI_escape_color_codes[color]
    bold_code = "1;" if bold else ""
    print(f"\033[{bold_code}{color_code}m{s}\033[0m", end=end, flush=flush)


def print_log(s: str = "", end: str = "\n", flush: bool = True,
               highlight: bool = False, verbose: bool = True):
    color = "bg_gray" if highlight else "gray"
    printc(f"[{_timenow()}] : {s}", color=color, bold=False, end=end, flush=flush, verbose=verbose)

def print_info(s: str = "",
               end: str = "\n",
               flush: bool = True,
               highlight: bool = False,
               verbose: bool = True):
    color = "bg_blue" if highlight else "blue"
    printc(f"[{_timenow()}] : [INFO] {s}", color=color, bold=False, end=end, flush=flush, verbose=verbose)

def print_warning(s: str = "", end: str = "\n", flush: bool = True, highlight: bool = False, verbose: bool = True):
    color = "bg_red" if highlight else "red"
    printc(f"[{_timenow()}] : [WARNING] {s}", color=color, bold=False, end=end, flush=flush, verbose=verbose)


def print_attention(s: str = "", end: str = "\n", flush: bool = True, highlight: bool = False, verbose: bool = True):
    color = "bg_yellow" if highlight else "yellow"
    printc(f"[{_timenow()}] : [ATTENTION] {s}", color=color, bold=False, end=end, flush=flush, verbose=verbose)


def print_error(s: str = "", end: str = "\n", flush: bool = True, highlight: bool = False, verbose: bool = True):
    color = "bg_bright_red" if highlight else "bright_red"
    printc(f"[{_timenow()}] : [ERROR] {s}", color=color, bold=True, end=end, flush=flush, verbose=verbose)


def print_done(s: str = "", end: str = "\n", flush: bool = True, highlight: bool = False, verbose: bool = True):
    color = "bg_green" if highlight else "green"
    printc(f"[{_timenow()}] : [DONE] {s}", color=color, bold=False, end=end, flush=flush, verbose=verbose)


def print_success(s: str = "", end: str = "\n", flush: bool = True, highlight: bool = False, verbose: bool = True):
    color = "bg_green" if highlight else "green"
    printc(f"[{_timenow()}] : [SUCCESS] {s}", color=color, bold=True, end=end, flush=flush, verbose=verbose)

_MODULE_FUNCTIONS = [
    k
    for k, v in globals().items()
    if callable(v) and not k.startswith("_") and getattr(v, "__module__", None) == __name__
]

def _helper_print_functions():
    for name in _MODULE_FUNCTIONS:
        if name in __all__:
            eval(f"{name}('Example of {name}')")
            if name.startswith("print_"):
                eval(f"{name}('Example of {name} with highlight', highlight=True)")

if __name__ == "__main__":
    printc("\n ### Example of printc messages with different colors and boldness ### ", color="bg_yellow", bold=True)

    for _color in _ANSI_escape_color_codes:
        for _bold in [False, True]:
            printc(f"This is a message in {_color} color and bold={_bold}.", color=_color, bold=_bold)

    printc("\n### wg-toolkit.logprint functions:", color="bg_yellow", bold=True)
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")

    for name in _MODULE_FUNCTIONS:
        if name not in __all__:
            print_warning(f"Error: '{name}' is defined but missing from __all__.")

    printc("\n### Example of logprint messages:", color="bg_yellow", bold=True)

    print("\n### Example of functions in __all__ ###")
    _helper_print_functions()
