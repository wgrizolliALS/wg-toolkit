import time

import serial  # type: ignore
from serial.tools import list_ports  # type: ignore

from wg_toolkit.logprint import (
    print_error,
    print_info,
    print_warning,
    printc,
)

__all__ = [
    "close_all_ports",
    "close_serial_connection",
    "list_serial_ports",
    "serial_batched",
    "serial_query",
]

DEBUG = False


def list_serial_ports(verbose=False):
    """List all available serial ports on the system.

    Parameters
    ----------
    verbose : bool, optional
        If True, print the list of available ports.

    Returns
    -------
    list
        List of ListPortInfo objects, or an empty list if none found.

    Notes
    -----
    Lists all COM ports recognized by the OS regardless of whether a device
    is actually connected or powered on.
    """
    ports = list(list_ports.comports())
    if ports:
        print_info("Available serial ports:", verbose=verbose)
        for port in ports:
            print_info(
                f"\t- Device: {port.device}, Description: {port.description}",
                verbose=verbose,
            )
    else:
        print_warning("No serial ports found.", verbose=verbose)
    return ports


def close_all_ports():
    """Close all open serial ports."""
    ports = list_serial_ports(verbose=False)
    if not ports:
        print_warning("No serial ports to close.")
        return
    for port in ports:
        try:
            ser = serial.Serial(port.device)
            ser.close()
            print_info(f"Closed port: {port.device}")
        except Exception as e:
            print_warning(f"Could not close port {port.device}: {e}")


def close_serial_connection(port: str, verbose: bool = True):
    """Attempt to close a serial connection on `port` if open.

    Parameters
    ----------
    port : str
        Serial device path.
    verbose : bool, optional
        If True, enable informational printing about the close operation.
    """
    try:
        ser = serial.Serial(port)
        if ser.is_open:
            ser.close()
            print_info(f"Serial connection on {port} closed.", verbose=verbose)
        else:
            print_info(
                f"Serial connection on {port} was already closed.", verbose=verbose
            )
    except Exception as e:
        print_error(
            f"Failed to close serial connection on {port}: {e}", verbose=verbose
        )


def serial_query(
    cmd: str,
    port: str,
    baudrate: int = 9600,
    wait_serial=False,
    verbose: bool = False,
    debug: bool = DEBUG,
    wait_before_read: float = 0.05,
) -> str | None:
    """Send a command string to a serial device and read a single-line response.

    Opens the serial port, writes cmd, optionally waits for data to become
    available, then reads one line and returns it.

    Parameters
    ----------
    cmd : str
        Command string to send. A newline is appended automatically.
    port : str
        Serial device path (e.g. ``COM3`` or ``/dev/ttyUSB0``).
    baudrate : int, optional
        Serial baud rate.
    wait_serial : bool, optional
        If True, poll until data is available or a timeout occurs.
    verbose : bool, optional
        If True, enable informational printing.
    debug : bool, optional
        If True, enable debug printing.
    wait_before_read : float, optional
        Sleep interval in seconds between polls when wait_serial is True.

    Returns
    -------
    str or None
        The decoded response string, or None on empty response or error.
    """
    printc(
        f"[DEBUG] : Attempting to open serial port {port} at baudrate {baudrate}",
        verbose=debug,
    )

    try:
        with serial.Serial(port, baudrate=baudrate, timeout=0.5) as ser:
            printc(f"[COMMAND] = {cmd}", verbose=verbose, color="cyan", bold=True)
            ser.write(f"{cmd}\n".encode())

            _time_init = time.time()
            while wait_serial and ser.in_waiting == 0:
                time.sleep(wait_before_read)
                printc(f"[DEBUG] : Waiting for response from {cmd}...", verbose=debug)

                if time.time() - _time_init >= 5 * ser.timeout:  # type: ignore
                    raise TimeoutError(
                        f"Timeout waiting for response to {cmd} on {port}"
                    )

            response = ser.readline().decode(errors="ignore").strip()

        if response == "":
            printc(
                "[RESPONSE] = [EMPTY PORT]",
                verbose=verbose,
                color="cyan",
                bold=False,
            )
        else:
            printc(
                f"[RESPONSE] = {response}",
                verbose=verbose,
                color="green",
                bold=True,
            )

        printc(f"[DEBUG] : {type(response) = }", verbose=debug)

        return response

    except serial.SerialException as e:
        print_error(f"Error communicating with device on {port}: {e}", verbose=verbose)
        return None
    except TimeoutError as e:
        print_error(f"{e}", verbose=verbose)
        return None
    except Exception as e:
        print_error(f"Unexpected error on {port}: {e}", verbose=verbose)
        return None


def serial_batched(
    cmds: list,
    port: str,
    verbose: bool = True,
    debug: bool = DEBUG,
    send_individually: bool = False,
    wait_between_cmds: float = 0.05,
) -> str | None:
    """Send a list of serial commands either batched or individually.

    If any command contains a question mark (a query) or send_individually is
    True, commands are sent one-by-one with a small delay between them.
    Otherwise the list is joined with ``;`` and sent as a single batched write.

    Parameters
    ----------
    cmds : list
        List of command strings to send.
    port : str
        Serial device path.
    verbose : bool, optional
        If True, enable informational printing.
    debug : bool, optional
        If True, enable debug printing.
    send_individually : bool, optional
        If True, force sending commands individually regardless of content.
    wait_between_cmds : float, optional
        Seconds to sleep between commands.

    Returns
    -------
    str or None
        The last received response, or None.
    """

    res = None
    if any("?" in _str for _str in cmds) or send_individually:
        for cmd in cmds:
            res = serial_query(cmd, port, verbose=verbose, debug=debug)
            time.sleep(wait_between_cmds)
    else:
        batch_cmd = ";".join(cmds)
        res = serial_query(batch_cmd, port, verbose=verbose, debug=debug)

        time.sleep(wait_between_cmds)
    return res


_MODULE_FUNCTIONS = [
    k
    for k, v in globals().items()
    if callable(v)
    and not k.startswith("_")
    and getattr(v, "__module__", None) == __name__
]

if __name__ == "__main__":
    print("\n### wg-toolkit.ports functions:")
    for name in _MODULE_FUNCTIONS:
        print(f"  {name}")

    for name in _MODULE_FUNCTIONS:
        if name not in __all__:
            print(f"Error: '{name}' is defined but missing from __all__.")

    printc(
        "This module provides functions for listing and closing serial ports.",
        color="cyan",
        bold=True,
    )
    printc(
        "Use list_serial_ports() to see available ports and close_all_ports() to close them.",
        color="cyan",
        bold=True,
    )

    ports = list_serial_ports(verbose=True)
    if ports:
        printc(
            "\nAttempting to close all open serial ports...", color="cyan", bold=True
        )
        close_all_ports()
