from datetime import datetime

__all__ = [
    "datenow_str",
    "timenow_str",
    "printc",
    "print_log",
    "print_info",
    "print_warning",
    "print_attention",
    "print_error",
    "print_done",
]


def datenow_str():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def timenow_str():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


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
    }

    if not verbose:
        return

    if color not in color_codes:
        print(s, end=end, flush=flush)
        return

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
