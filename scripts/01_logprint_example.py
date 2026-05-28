from wg_toolkit.logprint import (
    printc,
    print_log,
    print_info,
    print_warning,
    print_attention,
    print_error,
    print_done,
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
