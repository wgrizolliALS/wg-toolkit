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

"""

from wg_toolkit.misc import timenow

__all__ = [
    "printc",
    "print_log",
    "print_info",
    "print_warning",
    "print_attention",
    "print_error",
    "print_done",
    "print_success",
]

_color_ANSI_Escape_codes = {
    "red": "91",
    "green": "92",
    "blue": "94",
    "purple": "95",
    "cyan": "96",
    "gray": "90",
    "": "0",  # Default terminal color
}


def printc(s: str, color: str = "", bold: bool = False, end: str = "\n", flush: bool = True, verbose: bool = True):
    """Print `s` to stdout wrapped in ANSI color/bold escape codes.

    Parameters
    ----------
    s : str
        The input string to colorize.
    color : str, optional
        Color name. One of: red, green, blue, purple, cyan, gray, or empty
        string for the default terminal color.
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

    if color not in _color_ANSI_Escape_codes:
        raise ValueError(f"Invalid color '{color}'. Valid options are: {list(_color_ANSI_Escape_codes.keys())}")

    color_code = _color_ANSI_Escape_codes[color]
    bold_code = "1;" if bold else ""
    print(f"\033[{bold_code}{color_code}m{s}\033[0m", end=end, flush=flush)


def print_log(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow()}] : {s}", color="gray", bold=False, end=end, flush=flush, verbose=verbose)


def print_info(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow()}] : [INFO] {s}", color="blue", bold=False, end=end, flush=flush, verbose=verbose)


def print_warning(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow()}] : [WARNING] {s}", color="purple", bold=False, end=end, flush=flush, verbose=verbose)


def print_attention(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow()}] : [ATTENTION] {s}", color="red", bold=False, end=end, flush=flush, verbose=verbose)


def print_error(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow()}] : [ERROR] {s}", color="red", bold=True, end=end, flush=flush, verbose=verbose)


def print_done(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow()}] : [DONE] {s}", color="cyan", bold=True, end=end, flush=flush, verbose=verbose)


def print_success(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow()}] : [SUCCESS] {s}", color="green", bold=True, end=end, flush=flush, verbose=verbose)

_MODULE_FUNCTIONS = [k for k, v in globals().items() if callable(v) and not k.startswith("_")]


if __name__ == "__main__":
    printc("### This module provides enhanced logging functions with color and timestamps.", color="cyan", bold=True)

    print("\n### wg-toolkit.logprint functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")

    print("\n### Example of logprint messages:")

    print_log("This is a log message. Note the automatic timestamp.")
    print_info("This is an info message. Note the automatic timestamp.")
    print_warning("This is a warning message. Note the automatic timestamp.")
    print_attention("This is an attention message. Note the automatic timestamp.")
    print_error("This is an error message. Note the automatic timestamp.")
    print_done("This is a done message. Note the automatic timestamp.")
    print_success("This is a success message. Note the automatic timestamp.")

    for _color in _color_ANSI_Escape_codes.keys():
        for _bold in [False, True]:
            printc(f"This is a message in {_color} color and bold={_bold}.", color=_color, bold=_bold)
