"""
A minimal, real ONVIF-style device-integration model: device discovery,
capability negotiation, and profile/stream configuration -- the shape of
what a LiDAR sensor's device-software stack has to expose to a Video
Management System (VMS) for interoperability.

This is NOT a real ONVIF implementation (no SOAP/WSDL, no real ONVIF
Device Test Tool conformance) -- it models the request/response
structure and negotiation logic of the ONVIF Device Management and
Media services by hand, in plain Python, to demonstrate understanding
of the integration shape without claiming conformance to the actual
ONVIF standard. See README for the full honest disclosure.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class UnsupportedCapabilityError(Exception):
    pass


@dataclass
class DeviceCapabilities:
    """Mirrors the shape of an ONVIF GetCapabilities response: which
    services a device exposes."""
    supports_media: bool = True
    supports_ptz: bool = False
    supports_analytics: bool = True
    supports_events: bool = True
    max_streams: int = 2


@dataclass
class MediaProfile:
    """Mirrors an ONVIF media profile: one named configuration bundling
    a video/point-cloud source and its encoding/stream settings."""
    profile_token: str
    name: str
    resolution: tuple[int, int]
    frame_rate_fps: int
    encoding: str  # e.g. "H264", "POINTCLOUD_PCD"


@dataclass
class LidarDevice:
    """A simulated Blickfeld-style LiDAR device exposing an
    ONVIF-shaped device/media interface for VMS integration testing."""
    device_id: str
    ip_address: str
    rtsp_port: int = 554
    capabilities: DeviceCapabilities = field(default_factory=DeviceCapabilities)
    profiles: list[MediaProfile] = field(default_factory=list)

    def add_profile(self, profile: MediaProfile) -> None:
        if len(self.profiles) >= self.capabilities.max_streams:
            raise UnsupportedCapabilityError(
                f"device {self.device_id} supports at most "
                f"{self.capabilities.max_streams} concurrent streams"
            )
        self.profiles.append(profile)

    def get_profile(self, profile_token: str) -> MediaProfile | None:
        return next((p for p in self.profiles if p.profile_token == profile_token), None)

    def get_stream_uri(self, profile_token: str) -> str:
        """Builds the RTSP stream URI for a given profile, mirroring
        ONVIF Media GetStreamUri semantics (profile-scoped RTSP path)."""
        profile = self.get_profile(profile_token)
        if profile is None:
            raise ValueError(f"unknown profile token: {profile_token}")
        return f"rtsp://{self.ip_address}:{self.rtsp_port}/onvif/{profile.profile_token}"


def negotiate_common_capabilities(device: LidarDevice, vms_requirements: DeviceCapabilities) -> list[str]:
    """Compares a device's capabilities against what a VMS platform
    requires for integration, returning a list of unmet requirements --
    exactly the interoperability-check step named in the posting
    ("test the interoperability... to ensure seamless integration")."""
    unmet = []
    if vms_requirements.supports_media and not device.capabilities.supports_media:
        unmet.append("media")
    if vms_requirements.supports_ptz and not device.capabilities.supports_ptz:
        unmet.append("ptz")
    if vms_requirements.supports_analytics and not device.capabilities.supports_analytics:
        unmet.append("analytics")
    if vms_requirements.supports_events and not device.capabilities.supports_events:
        unmet.append("events")
    return unmet
