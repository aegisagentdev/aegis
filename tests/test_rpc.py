from kabuto.rpc import decode_address, decode_string, decode_uint, encode_call

ADDR = "0x1111111111111111111111111111111111111111"


def test_encode_call_no_args():
    assert encode_call("decimals") == "0x313ce567"


def test_encode_call_address_arg():
    data = encode_call("balanceOf", ADDR)
    assert data.startswith("0x70a08231")
    # selector (4 bytes) + one 32-byte word
    assert len(data) == 2 + 8 + 64
    assert data.endswith("1" * 40)


def test_decode_uint():
    raw = (12345).to_bytes(32, "big")
    assert decode_uint(raw) == 12345
    assert decode_uint(b"") == 0


def test_decode_address():
    raw = bytes(12) + bytes.fromhex("11" * 20)
    assert decode_address(raw) == ADDR


def test_decode_string_dynamic():
    # ABI: offset word, length word, data
    body = b"USDG"
    raw = (32).to_bytes(32, "big") + len(body).to_bytes(32, "big") + body.ljust(32, b"\x00")
    assert decode_string(raw) == "USDG"


def test_decode_string_bytes32_packed():
    raw = b"WETH".ljust(32, b"\x00")
    assert decode_string(raw) == "WETH"
