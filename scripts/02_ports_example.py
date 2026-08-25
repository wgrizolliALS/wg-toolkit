from wg_toolkit.logprint import (
    print_done,
    print_info,
    print_log,
    print_warning,
)
from wg_toolkit.ports import close_all_ports, list_serial_ports

print_info("Listing available serial ports:")
ports = list_serial_ports(verbose=False)

if not ports:
    print_warning("No serial ports found. Please connect a device and try again.")
else:
    print_done(f"Found {len(ports)} serial port(s):")
    for port in ports:
        print_log(f"Port: {port.device}, Description: {port.description}")

print_info("\nAttempting to close all open serial ports:")
close_all_ports()
print_done("\nPorts example script completed.")
