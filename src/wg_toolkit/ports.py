import serial
from serial.tools import list_ports

__all__ = [
    "list_serial_ports",
    "close_all_ports",
]


def list_serial_ports():
    """List all available serial ports on the system.

    Note: lists all COM ports recognized by the OS regardless of whether a
    device is actually connected or powered on.

    Returns:
        List of ListPortInfo objects, or an empty list if none found.
    """
    ports = list(list_ports.comports())
    if ports:
        print("Available serial ports:")
        for port in ports:
            print(f"\t- Device: {port.device}, Description: {port.description}")
    else:
        print("No serial ports found!")
    return ports


def close_all_ports():
    """Close all open serial ports."""
    ports = list_serial_ports()
    for port in ports:
        try:
            ser = serial.Serial(port.device)
            ser.close()
            print(f"Closed port: {port.device}")
        except Exception as e:
            print(f"Could not close port {port.device}: {e}")
