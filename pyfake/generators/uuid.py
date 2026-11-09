"""
UUID generators.

All randomness comes from the context, so seeded runs give the same UUIDs. Time-based
versions (v1, v6, v7) use a timestamp from the 24 hours before `context.now`.
"""

from typing import Optional
import uuid
import hashlib
from pyfake.core.context import Context

# 100-nanosecond intervals between the Gregorian epoch (1582-10-15)
# used by v1/v6 and the Unix epoch
_GREGORIAN_OFFSET = 0x01B21DD213814000
_MS_PER_DAY = 86_400_000


def _with_version(value: int, version: int) -> uuid.UUID:
    """Set the version and the RFC 4122 variant bits on a 128-bit integer"""
    value &= ~(0xF << 76)
    value |= version << 76
    value &= ~(0b11 << 62)
    value |= 0b10 << 62
    return uuid.UUID(int=value)


def _timestamp_ms(context: Context) -> int:
    """Milliseconds since the Unix epoch, within the day before `context.now`"""
    return int(context.now.timestamp() * 1000) - context.random.randrange(_MS_PER_DAY)


def _gregorian_timestamp(context: Context) -> int:
    """The 60-bit v1/v6 timestamp: 100-nanosecond intervals since the Gregorian epoch"""
    return (
        _timestamp_ms(context) * 10_000
        + context.random.randrange(10_000)
        + _GREGORIAN_OFFSET
    )


def _clock_seq_and_node(context: Context):
    clock_seq = context.random.getrandbits(14)
    # Random node IDs set the multicast bit, so they can't clash with a real MAC address (RFC 4122 §4.5)
    node = context.random.getrandbits(48) | (1 << 40)
    return ((clock_seq >> 8) & 0x3F) | 0x80, clock_seq & 0xFF, node


def generate_uuid1(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()

    timestamp = _gregorian_timestamp(context)
    clock_seq_hi, clock_seq_low, node = _clock_seq_and_node(context)

    time_low = timestamp & 0xFFFFFFFF
    time_mid = (timestamp >> 32) & 0xFFFF
    time_hi_version = ((timestamp >> 48) & 0x0FFF) | (1 << 12)

    return str(
        uuid.UUID(
            fields=(
                time_low,
                time_mid,
                time_hi_version,
                clock_seq_hi,
                clock_seq_low,
                node,
            )
        )
    )


def generate_uuid3(
    *,
    namespace: Optional[uuid.UUID] = uuid.NAMESPACE_DNS,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if not namespace:
        namespace = uuid.NAMESPACE_DNS
    return str(uuid.uuid3(namespace, generate_uuid4(context=context)))


def generate_uuid4(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()
    return str(_with_version(context.random.getrandbits(128), 4))


def generate_uuid5(
    *,
    namespace: Optional[uuid.UUID] = uuid.NAMESPACE_DNS,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if not namespace:
        namespace = uuid.NAMESPACE_DNS
    return str(uuid.uuid5(namespace, generate_uuid4(context=context)))


def generate_uuid6(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()

    # Same fields as UUIDv1, but the timestamp is stored big-endian so the UUIDs sort by time
    timestamp = _gregorian_timestamp(context)
    clock_seq_hi, clock_seq_low, node = _clock_seq_and_node(context)

    time_high = (timestamp >> 28) & 0xFFFFFFFF
    time_mid = (timestamp >> 12) & 0xFFFF
    time_low_version = (timestamp & 0x0FFF) | (6 << 12)

    return str(
        uuid.UUID(
            fields=(
                time_high,
                time_mid,
                time_low_version,
                clock_seq_hi,
                clock_seq_low,
                node,
            )
        )
    )


def generate_uuid7(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()

    # 48-bit timestamp (milliseconds), followed by 80 bits of randomness
    ts = _timestamp_ms(context) & ((1 << 48) - 1)
    rand = context.random.getrandbits(80)

    return str(_with_version((ts << 80) | rand, 7))


def generate_uuid8(
    *,
    namespace: Optional[str] = "pyfake",
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if context is None:
        context = Context()

    if not namespace:
        namespace = "pyfake"

    # UUIDv8 layout is vendor-defined: here, a hash of the namespace and random bits
    h = hashlib.sha256(
        f"{namespace}:{context.random.getrandbits(128)}".encode()
    ).digest()

    return str(_with_version(int.from_bytes(h[:16], "big"), 8))
