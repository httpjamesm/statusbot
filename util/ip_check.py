# This function checks whether a host is an IP address or a domain name. If an IP address is input, it returns True.
def is_ip(address):
    return address.replace('.', '').isnumeric()