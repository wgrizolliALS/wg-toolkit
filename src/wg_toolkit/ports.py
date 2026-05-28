import serial
from serial.tools import list_ports

from wg_toolkit.logprint import print_info, print_warning, printc

__all__ = [
    "list_serial_ports",
    "close_all_ports",
]


def list_serial_ports(verbose=False):
    """List all available serial ports on the system.

    Note: lists all COM ports recognized by the OS regardless of whether a
    device is actually connected or powered on.

    Returns:
        List of ListPortInfo objects, or an empty list if none found.
    """
    ports = list(list_ports.comports())
    if ports:
        print_info("Available serial ports:", verbose=verbose)
        for port in ports:
            print_info(f"\t- Device: {port.device}, Description: {port.description}", verbose=verbose)
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


if __name__ == "__main__":
    printc("This module provides functions for listing and closing serial ports.", color="cyan", bold=True)
    printc(
        "Use list_serial_ports() to see available ports and close_all_ports() to close them.", color="cyan", bold=True
    )

    ports = list_serial_ports(verbose=True)
    if ports:
        printc("\nAttempting to close all open serial ports...", color="cyan", bold=True)
        close_all_ports()
