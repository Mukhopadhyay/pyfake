"""
Generators for emails, URLs and IP addresses.

Hosts and email domains use the `example.*` domains reserved by RFC 2606, so generated
values never point at a real server or mailbox.
"""

import ipaddress
import string

from pydantic.networks import UrlConstraints

from pyfake.core.context import Context

_DOMAINS = ("example.com", "example.org", "example.net")
# Schemes written as "scheme://host/path". Any other scheme gets DSN form, "scheme://user:password@host:port/name"
_WEB_SCHEMES = {"http", "https", "ws", "wss", "ftp"}


def _word(context: Context) -> str:
    return "".join(
        context.random.choice(string.ascii_lowercase)
        for _ in range(context.random.randint(3, 8))
    )


def generate_email(
    *,
    context: Context | None = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()
    return f"{_word(context)}.{_word(context)}{context.random.randint(1, 99)}@{context.random.choice(_DOMAINS)}"


def generate_name_email(
    *,
    context: Context | None = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()
    first, last = _word(context), _word(context)
    return f"{first.capitalize()} {last.capitalize()} <{first}.{last}@{context.random.choice(_DOMAINS)}>"


def generate_url(
    *,
    constraints: UrlConstraints | None = None,
    context: Context | None = None,
    **kwargs,
) -> str:
    """
    Generate a URL whose scheme is one of `constraints.allowed_schemes` (http/https by default).
    """
    if context is None:
        context = Context()

    if constraints is not None and constraints.allowed_schemes:
        schemes = sorted(constraints.allowed_schemes)
    else:
        schemes = ["http", "https"]
    scheme = context.random.choice(schemes)

    if scheme == "file":
        return f"file:///{_word(context)}/{_word(context)}.txt"

    host = f"{_word(context)}.{context.random.choice(_DOMAINS)}"
    if scheme in _WEB_SCHEMES:
        return f"{scheme}://{host}/{_word(context)}"

    port = context.random.randint(1024, 65535)
    return (
        f"{scheme}://{_word(context)}:{_word(context)}@{host}:{port}/{_word(context)}"
    )


def generate_ip_address(
    *,
    version: int | None = None,
    context: Context | None = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()
    address, _ = _random_address(version, context)
    return str(address)


def generate_ip_network(
    *,
    version: int | None = None,
    context: Context | None = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()
    address, prefix = _random_address(version, context)
    # strict=False zeroes the host bits, which pydantic's network types require
    return str(ipaddress.ip_network(f"{address}/{prefix}", strict=False))


def generate_ip_interface(
    *,
    version: int | None = None,
    context: Context | None = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()
    address, prefix = _random_address(version, context)
    return f"{address}/{prefix}"


def _random_address(version: int | None, context: Context):
    """A random address of the given IP version (4 or 6, random if None) and a prefix length for it"""
    version = version or context.random.choice((4, 6))
    if version == 4:
        return ipaddress.IPv4Address(
            context.random.getrandbits(32)
        ), context.random.randint(8, 30)
    return ipaddress.IPv6Address(
        context.random.getrandbits(128)
    ), context.random.randint(32, 64)
