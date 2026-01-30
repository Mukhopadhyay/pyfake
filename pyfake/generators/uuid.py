from pyfake.core.context import Context
from typing import Optional
import uuid
import time
import hashlib


def generate_uuid1(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    return str(uuid.uuid1())


def generate_uuid3(
    *,
    namespace: Optional[str] = uuid.NAMESPACE_DNS,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if not namespace:
        namespace = uuid.NAMESPACE_DNS
    return str(uuid.uuid3(namespace, str(uuid.uuid4())))


def generate_uuid4(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    return str(uuid.uuid4())


def generate_uuid5(
    *,
    namespace: Optional[str] = uuid.NAMESPACE_DNS,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    if not namespace:
        namespace = uuid.NAMESPACE_DNS
    return str(uuid.uuid5(namespace, str(uuid.uuid4())))


def generate_uuid6(
    *,
    context: Optional["Context"] = None,
    **kwargs,
) -> str:
    # Start from UUIDv1 (contains timestamp, clock seq, node)
    u1 = uuid.uuid1()

    time_low, time_mid, time_hi_version, clock_seq_hi, clock_seq_low, node = u1.fields

    # Reconstruct the 60-bit timestamp from UUIDv1
    timestamp = ((time_hi_version & 0x0FFF) << 48) | (time_mid << 32) | time_low

    # UUIDv6 timestamp is big-endian
    time_high = (timestamp >> 28) & 0xFFFFFFFF
    time_mid = (timestamp >> 12) & 0xFFFF
    time_low = timestamp & 0xFFF

    # Assemble UUID fields
    time_hi_version = time_low | (6 << 12)

    # Preserve clock sequence
    clock_seq = ((clock_seq_hi & 0x3F) << 8) | clock_seq_low
    clock_seq_hi = (clock_seq >> 8) | 0x80  # RFC 4122 variant
    clock_seq_low = clock_seq & 0xFF

    u6 = uuid.UUID(
        fields=(
            time_high,
            time_mid,
            time_hi_version,
            clock_seq_hi,
            clock_seq_low,
            node,
        )
    )

    return str(u6)


def generate_uuid7(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> uuid.UUID:
    # 48-bit timestamp (milliseconds)
    ts = int(time.time() * 1000) & ((1 << 48) - 1)

    # 80 bits of randomness
    # rand = random.getrandbits(80)
    rand = context.random.getrandbits(80)

    # Assemble UUID fields
    value = (ts << 80) | (0x7 << 76) | (rand & ((1 << 76) - 1))  # version 7

    # Set RFC 4122 variant (10xx)
    value &= ~(0b11 << 62)
    value |= 0b10 << 62

    return str(uuid.UUID(int=value))


def generate_uuid8(
    *,
    namespace: Optional[str] = "pyfake",
    context: Optional[Context] = None,
    **kwargs,
) -> uuid.UUID:

    if not namespace:
        namespace = "pyfake"

    ts = int(time.time() * 1000)
    h = hashlib.sha256(f"{namespace}:{ts}".encode()).digest()

    value = int.from_bytes(h[:16], "big")

    # set version 8
    value &= ~(0xF << 76)
    value |= 8 << 76

    # set variant
    value &= ~(0b11 << 62)
    value |= 0b10 << 62

    return str(uuid.UUID(int=value))
