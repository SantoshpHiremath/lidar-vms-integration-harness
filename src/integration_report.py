"""
Documents integration-test results -- the "Validation & Documentation"
task named in the posting: "You document integration results,
compliance findings, and system behavior to support interoperability
improvements and product development."
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.onvif_device import LidarDevice, DeviceCapabilities, negotiate_common_capabilities


@dataclass
class IntegrationTestResult:
    vms_platform: str
    device_id: str
    profile_token: str
    stream_uri_resolved: bool
    unmet_capabilities: list[str]
    point_count_check_passed: bool
    notes: str = ""

    @property
    def passed(self) -> bool:
        return self.stream_uri_resolved and not self.unmet_capabilities and self.point_count_check_passed


def run_integration_test(
    device: LidarDevice,
    vms_platform: str,
    vms_requirements: DeviceCapabilities,
    profile_token: str,
    point_count_check_passed: bool,
) -> IntegrationTestResult:
    """Runs a single interoperability test of a device against a named
    VMS platform's requirements, mirroring the posting's own
    integration-test workflow: capability negotiation, stream-URI
    resolution, and point-cloud validation."""
    unmet = negotiate_common_capabilities(device, vms_requirements)
    try:
        device.get_stream_uri(profile_token)
        stream_resolved = True
    except (ValueError,) :
        stream_resolved = False

    notes = "All checks passed." if (stream_resolved and not unmet and point_count_check_passed) else "See unmet_capabilities / flags."
    return IntegrationTestResult(
        vms_platform=vms_platform, device_id=device.device_id, profile_token=profile_token,
        stream_uri_resolved=stream_resolved, unmet_capabilities=unmet,
        point_count_check_passed=point_count_check_passed, notes=notes,
    )


def summarize_results(results: list[IntegrationTestResult]) -> dict:
    """Produces a compliance summary across multiple VMS platforms --
    the documentation output a real interoperability test suite needs
    to hand to product development."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    by_platform = {}
    for r in results:
        by_platform.setdefault(r.vms_platform, []).append(r.passed)
    platform_summary = {
        platform: {"tested": len(flags), "passed": sum(flags)}
        for platform, flags in by_platform.items()
    }
    return {
        "total_tests": total,
        "total_passed": passed,
        "pass_rate_pct": round((passed / total) * 100, 1) if total else 0.0,
        "by_platform": platform_summary,
    }
