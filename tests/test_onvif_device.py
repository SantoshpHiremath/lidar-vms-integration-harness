import pytest

from src.onvif_device import (
    LidarDevice, DeviceCapabilities, MediaProfile,
    UnsupportedCapabilityError, negotiate_common_capabilities,
)


def make_device(**overrides):
    caps = overrides.pop("capabilities", DeviceCapabilities())
    defaults = dict(device_id="lidar-001", ip_address="10.0.1.20", rtsp_port=554, capabilities=caps)
    defaults.update(overrides)
    return LidarDevice(**defaults)


def test_add_profile_within_limit():
    device = make_device(capabilities=DeviceCapabilities(max_streams=2))
    device.add_profile(MediaProfile("p1", "Main", (1920, 1080), 30, "H264"))
    device.add_profile(MediaProfile("p2", "Sub", (640, 480), 15, "H264"))
    assert len(device.profiles) == 2


def test_add_profile_beyond_limit_raises():
    device = make_device(capabilities=DeviceCapabilities(max_streams=1))
    device.add_profile(MediaProfile("p1", "Main", (1920, 1080), 30, "H264"))
    with pytest.raises(UnsupportedCapabilityError):
        device.add_profile(MediaProfile("p2", "Sub", (640, 480), 15, "H264"))


def test_get_profile_found():
    device = make_device()
    profile = MediaProfile("p1", "Main", (1920, 1080), 30, "POINTCLOUD_PCD")
    device.add_profile(profile)
    assert device.get_profile("p1") is profile


def test_get_profile_not_found_returns_none():
    device = make_device()
    assert device.get_profile("missing") is None


def test_get_stream_uri_builds_expected_rtsp_url():
    device = make_device(ip_address="192.168.1.50", rtsp_port=8554)
    device.add_profile(MediaProfile("main-stream", "Main", (1920, 1080), 30, "H264"))
    uri = device.get_stream_uri("main-stream")
    assert uri == "rtsp://192.168.1.50:8554/onvif/main-stream"


def test_get_stream_uri_unknown_profile_raises():
    device = make_device()
    with pytest.raises(ValueError):
        device.get_stream_uri("does-not-exist")


def test_negotiate_no_gaps_when_fully_supported():
    device = make_device(capabilities=DeviceCapabilities(
        supports_media=True, supports_ptz=True, supports_analytics=True, supports_events=True,
    ))
    requirements = DeviceCapabilities(supports_media=True, supports_ptz=True, supports_analytics=True, supports_events=True)
    assert negotiate_common_capabilities(device, requirements) == []


def test_negotiate_flags_unmet_ptz():
    device = make_device(capabilities=DeviceCapabilities(supports_ptz=False))
    requirements = DeviceCapabilities(supports_media=True, supports_ptz=True, supports_analytics=False, supports_events=False)
    unmet = negotiate_common_capabilities(device, requirements)
    assert unmet == ["ptz"]


def test_negotiate_flags_multiple_unmet():
    device = make_device(capabilities=DeviceCapabilities(
        supports_media=True, supports_ptz=False, supports_analytics=False, supports_events=False,
    ))
    requirements = DeviceCapabilities(supports_media=True, supports_ptz=True, supports_analytics=True, supports_events=True)
    unmet = negotiate_common_capabilities(device, requirements)
    assert set(unmet) == {"ptz", "analytics", "events"}


def test_negotiate_does_not_flag_unrequired_gaps():
    # Device lacks PTZ, but VMS doesn't require it -- should not be flagged.
    device = make_device(capabilities=DeviceCapabilities(supports_ptz=False))
    requirements = DeviceCapabilities(supports_media=True, supports_ptz=False, supports_analytics=False, supports_events=False)
    assert negotiate_common_capabilities(device, requirements) == []
