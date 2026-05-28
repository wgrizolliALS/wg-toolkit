from wg_toolkit.misc import timenow_str

__all__ = [
    "printc",
    "print_log",
    "print_info",
    "print_warning",
    "print_attention",
    "print_error",
    "print_done",
]


def printc(s: str, color: str = "", bold: bool = False, end: str = "\n", flush: bool = True, verbose: bool = True):
    """Print `s` to stdout wrapped in ANSI color/bold escape codes.

    Args:
        s: The input string to colorize.
        color: Optional color name (red, green, blue, purple, cyan).
        bold: If True, make the text bold.
        end: String appended after the last character (default newline).
        flush: Whether to flush the output buffer.
        verbose: If False, suppress printing.
    """
    color_codes = {
        "red": "91",
        "green": "92",
        "blue": "94",
        "purple": "95",
        "cyan": "96",
        "": "0",  # Default terminal color
    }

    if not verbose:
        return

    if color not in color_codes:
        raise ValueError(f"Invalid color '{color}'. Valid options are: {list(color_codes.keys())}")

    color_code = color_codes[color]
    bold_code = "1;" if bold else ""
    print(f"\033[{bold_code}{color_code}m{s}\033[0m", end=end, flush=flush)


def print_log(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow_str()}] : {s}", color="purple", bold=False, end=end, flush=flush, verbose=verbose)


def print_info(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow_str()}] : [INFO] {s}", color="blue", bold=False, end=end, flush=flush, verbose=verbose)


def print_warning(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow_str()}] : [WARNING] {s}", color="red", bold=False, end=end, flush=flush, verbose=verbose)


def print_attention(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow_str()}] : [ATTENTION] {s}", color="red", bold=True, end=end, flush=flush, verbose=verbose)


def print_error(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow_str()}] : [ERROR] {s}", color="red", bold=True, end=end, flush=flush, verbose=verbose)


def print_done(s: str, end: str = "\n", flush: bool = True, verbose: bool = True):
    printc(f"[{timenow_str()}] : [DONE] {s}", color="green", bold=True, end=end, flush=flush, verbose=verbose)


if __name__ == "__main__":
    printc("This module provides enhanced logging functions with color and timestamps.", color="cyan", bold=True)
    printc(
        "Use print_log(), print_info(), print_warning(), print_attention(), print_error(), and print_done() for different log levels.",
        color="cyan",
        bold=True,
    )

    print_log("This is a log message.")
    print_info("This is an info message.")
    print_warning("This is a warning message.")
    print_attention("This is an attention message.")
    print_error("This is an error message.")
    print_done("This is a done message.")

    for _color in ["red", "green", "blue", "purple", "cyan"]:
        for _bold in [False, True]:
            printc(f"This is a message in {_color} color and bold={_bold}.", color=_color, bold=_bold)
