import pytest

from ifcclient.utils import (
    rad_to_ang,
    mps_to_fpm,
    mps_to_kph,
    pack,
    unpack,
    recieve,
)

@pytest.mark.parametrize(
        "rad, ang",
        (
            (0.5, 28.64788975654116),
            (1, 57.29577951308232),
            (2, 114.59155902616465)
        ),
    )
def test_rad_to_ang(rad, ang):
    assert rad_to_ang(rad) == ang

@pytest.mark.parametrize(
    "mps, fpm",
    (
        (1, 196.850394),
        (5, 984.25197),
        (10, 1968.50394),
    ),
)

def test_mps_to_fpm(mps, fpm):
    assert mps_to_fpm(mps) == fpm

@pytest.mark.parametrize(
    "mps, kph",
    (
        (20, 38.876889816),
        (50, 97.19222454000001),
        (100, 194.38444908000002),
        (150, 291.57667362),
    ),
)

def test_mps_to_kph(mps, kph):
    assert mps_to_kph(mps) == kph

@pytest.mark.parametrize(
    "value, data_type, payload",
    (
        (True, 0, b'\x01'),
        (False, 0, b'\x00'),
        (5, 1, b'\x05\x00\x00\x00'),
        (10, 1, b'\n\x00\x00\x00'),
        (3.14, 2, b'\xc3\xf5H@'),
        (10.8, 2, b'\xcd\xcc,A'),
        (3.14, 3, b'\x1f\x85\xebQ\xb8\x1e\t@'),
        (10.8, 3, b'\x9a\x99\x99\x99\x99\x99%@'),
        ("This is a string", 4, b'\x10\x00\x00\x00This is a string'),
        ("", 4, b'\x00\x00\x00\x00'),
        (5, 5, b'\x05\x00\x00\x00\x00\x00\x00\x00'),
        (10, 5, b'\n\x00\x00\x00\x00\x00\x00\x00'),
    ),
)

def test_pack(value, data_type, payload):
    assert pack(value, data_type) == payload

@pytest.mark.parametrize(
    "value, data_type",
    (
        (True, 3),
        (False, 4),
        (5, 2),
        (10, 4),
        (3.14, 1),
        (10.8, 4),
        (3.14, 5),
        (10.8, 5),
        ("This is a string", 1),
        ("", 3),
        (5, 3),
        (10, 2),
    ),
)

def test_pack_exception(value, data_type):
    with pytest.raises(TypeError):
        pack(value, data_type)

@pytest.mark.parametrize(
    "value, data_type, payload",
    (
        (True, 0, b'\x01'),
        (False, 0, b'\x00'),
        (5, 1, b'\x05\x00\x00\x00'),
        (10, 1, b'\n\x00\x00\x00'),
        (3.140000104904175, 2, b'\xc3\xf5H@'),
        (10.800000190734863, 2, b'\xcd\xcc,A'),
        (3.14, 3, b'\x1f\x85\xebQ\xb8\x1e\t@'),
        (10.8, 3, b'\x9a\x99\x99\x99\x99\x99%@'),
        ("This is a string", 4, b'\x10\x00\x00\x00This is a string'),
        ("", 4, b'\x00\x00\x00\x00'),
        (5, 5, b'\x05\x00\x00\x00\x00\x00\x00\x00'),
        (10, 5, b'\n\x00\x00\x00\x00\x00\x00\x00'),
    ),
)

def test_unpack(payload, data_type, value):
    assert unpack(payload, data_type) == value