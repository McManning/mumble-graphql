
import ipaddress


def address_tuple_to_ipv6(address):
    """Convert an address tuple to an IPv6Address object"""
    groups = ['{:02X}{:02X}'.format(address[i], address[i+1])
              for i in range(0, 16, 2)]
    long_form = ':'.join(groups)

    return ipaddress.IPv6Address(long_form)
