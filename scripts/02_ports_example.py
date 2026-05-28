from wg_toolkit.logprint import print_log, print_info, print_warning, print_error, print_done

from wg_toolkit.ports import list_serial_ports, close_all_ports


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
