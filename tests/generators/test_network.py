import ipaddress

import pytest
from pydantic import EmailStr, NameEmail, TypeAdapter
from pydantic.networks import UrlConstraints

from pyfake.core.context import Context
from pyfake.generators import network


@pytest.mark.datatypes
@pytest.mark.network
class TestNetworkGenerators:
    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_email_is_valid(self, seed):
        email = network.generate_email(context=Context(seed=seed))
        TypeAdapter(EmailStr).validate_python(email)
        assert email.split("@")[1] in {"example.com", "example.org", "example.net"}

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_name_email_is_valid(self, seed):
        value = TypeAdapter(NameEmail).validate_python(
            network.generate_name_email(context=Context(seed=seed))
        )
        assert value.name
        assert value.email.endswith((".com", ".org", ".net"))

    def test_url_defaults_to_http(self):
        url = network.generate_url(context=Context(seed=1))
        assert url.startswith(("http://", "https://"))

    @pytest.mark.parametrize(
        "schemes,prefix",
        [
            (["file"], "file:///"),
            (["ws", "wss"], "ws"),
            (["postgresql"], "postgresql://"),
        ],
    )
    def test_url_uses_allowed_schemes(self, schemes, prefix):
        url = network.generate_url(
            constraints=UrlConstraints(allowed_schemes=schemes), context=Context(seed=1)
        )
        assert url.startswith(prefix)

    def test_dsn_has_credentials_and_port(self):
        url = network.generate_url(
            constraints=UrlConstraints(allowed_schemes=["redis"]),
            context=Context(seed=1),
        )
        assert "@" in url and url.rsplit(":", 1)[1].split("/")[0].isdigit()

    @pytest.mark.parametrize(
        "version,cls", [(4, ipaddress.IPv4Address), (6, ipaddress.IPv6Address)]
    )
    def test_ip_address_version(self, version, cls):
        address = network.generate_ip_address(version=version, context=Context(seed=1))
        assert isinstance(ipaddress.ip_address(address), cls)

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_ip_network_has_no_host_bits(self, seed):
        # strict=True raises if host bits are set
        ipaddress.ip_network(
            network.generate_ip_network(context=Context(seed=seed)), strict=True
        )

    @pytest.mark.parametrize("version", [4, 6, None])
    def test_ip_interface(self, version):
        ipaddress.ip_interface(
            network.generate_ip_interface(version=version, context=Context(seed=5))
        )

    @pytest.mark.parametrize(
        "generator",
        [
            network.generate_email,
            network.generate_name_email,
            network.generate_url,
            network.generate_ip_address,
            network.generate_ip_network,
            network.generate_ip_interface,
        ],
    )
    def test_deterministic_with_seed(self, generator):
        assert generator(context=Context(seed=3)) == generator(context=Context(seed=3))

    @pytest.mark.parametrize(
        "generator",
        [
            network.generate_email,
            network.generate_name_email,
            network.generate_url,
            network.generate_ip_address,
            network.generate_ip_network,
            network.generate_ip_interface,
        ],
    )
    def test_no_context_creates_one(self, generator):
        assert isinstance(generator(), str)
