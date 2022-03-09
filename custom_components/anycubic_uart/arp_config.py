from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from python_arptable import get_arp_table


SUPPORTED_MACS = ["28:6d:cd"]


def get_unattached_devices(hass: HomeAssistant) -> list:
    """Scan all the devices and see which ones are availble for use.
    @Param hass - reference to home assistant"""
    arps = get_devices_via_arp_table()
    # remove_mac_duplicates_in_other_domain_entry(hass, arps)
    return arps


def remove_mac_duplicates_in_other_domain_entry(
    hass: HomeAssistant, arps: list
) -> None:
    """Remove existing devices tied to the domain.
    @Param hass - reference to home assistant.
    @Param arps - a list of arp responses."""

    for existing_entry in hass.config_entries[DOMAIN]:
        for arp in arps:
            if existing_entry[CONF_MAC] == arp["Mac"]:
                arps.remove(arp)


def get_devices_via_arp_table() -> list:
    """Scan ARP tables on device and find supported devices.
    Supported devices are defined in the SUPPORTED_MACS variable."""
    devices = []
    data = get_arp_table()
    for device in data:
        dev_address = device.get("HW address")
        if len(dev_address) >= 8:
            device_mac = device.get("HW address")[:8]
            for check_mac in SUPPORTED_MACS:
                if device_mac == check_mac[0:8]:
                    devices.append(device)
    #
    #
    # FOR TEST PURPOSES
    #
    #
    # devices = [
    #     {
    #         "IP address": "192.168.1.254",
    #         "HW type": "0x1",
    #         "Flags": "0x2",
    #         "HW address": "28:6d:cd:a2:8b:3a",
    #         "Mask": "*",
    #         "Device": "eth0",
    #     }
    # ]
    return devices
