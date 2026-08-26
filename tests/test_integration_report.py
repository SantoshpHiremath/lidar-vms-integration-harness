from src.onvif_device import LidarDevice, DeviceCapabilities, MediaProfile
from src.integration_report import run_integration_test, summarize_results


def make_device_with_profile(caps=None, profile_token="main"):
    device = LidarDevice(
        device_id="lidar-test-01", ip_address="10.0.5.5",
        capabilities=caps or DeviceCapabilities(),
    )
    device.add_profile(MediaProfile(profile_token, "Main", (1920, 1080), 30, "POINTCLOUD_PCD"))
    return device


def test_run_integration_test_passes_when_all_ok():
    device = make_device_with_profile()
    requirements = DeviceCapabilities(supports_media=True, supports_ptz=False, supports_analytics=True, supports_events=True)
    result = run_integration_test(device, "Milestone XProtect", requirements, "main", point_count_check_passed=True)
    assert result.passed is True
    assert result.stream_uri_resolved is True
    assert result.unmet_capabilities == []


def test_run_integration_test_fails_on_unmet_capability():
    device = make_device_with_profile(caps=DeviceCapabilities(supports_ptz=False))
    requirements = DeviceCapabilities(supports_media=True, supports_ptz=True, supports_analytics=False, supports_events=False)
    result = run_integration_test(device, "Genetec Security Center", requirements, "main", point_count_check_passed=True)
    assert result.passed is False
    assert "ptz" in result.unmet_capabilities


def test_run_integration_test_fails_on_unknown_profile():
    device = make_device_with_profile()
    requirements = DeviceCapabilities()
    result = run_integration_test(device, "Milestone XProtect", requirements, "nonexistent-profile", point_count_check_passed=True)
    assert result.stream_uri_resolved is False
    assert result.passed is False


def test_run_integration_test_fails_on_point_count_mismatch():
    device = make_device_with_profile()
    requirements = DeviceCapabilities(supports_media=True, supports_ptz=False, supports_analytics=False, supports_events=False)
    result = run_integration_test(device, "Milestone XProtect", requirements, "main", point_count_check_passed=False)
    assert result.passed is False
    assert result.point_count_check_passed is False


def test_summarize_results_counts_correctly():
    results = [
        run_integration_test(
            make_device_with_profile(), "Milestone XProtect",
            DeviceCapabilities(supports_media=True, supports_ptz=False, supports_analytics=False, supports_events=False),
            "main", point_count_check_passed=True,
        ),
        run_integration_test(
            make_device_with_profile(caps=DeviceCapabilities(supports_ptz=False)), "Genetec Security Center",
            DeviceCapabilities(supports_media=True, supports_ptz=True, supports_analytics=False, supports_events=False),
            "main", point_count_check_passed=True,
        ),
    ]
    summary = summarize_results(results)
    assert summary["total_tests"] == 2
    assert summary["total_passed"] == 1
    assert summary["pass_rate_pct"] == 50.0
    assert summary["by_platform"]["Milestone XProtect"]["passed"] == 1
    assert summary["by_platform"]["Genetec Security Center"]["passed"] == 0


def test_summarize_results_empty_list():
    summary = summarize_results([])
    assert summary["total_tests"] == 0
    assert summary["pass_rate_pct"] == 0.0
