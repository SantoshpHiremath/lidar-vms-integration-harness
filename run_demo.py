"""
Runs a full simulated interoperability-test cycle end to end and prints
a real console report.
"""

from src.onvif_device import LidarDevice, DeviceCapabilities, MediaProfile
from src.point_cloud import PointCloud, count_points_in_box
from src.integration_report import run_integration_test, summarize_results

SAMPLE_PCD = """
# simulated LiDAR frame, one detected person-sized cluster near origin
0.02 0.01 1.10
0.05 -0.02 1.15
-0.03 0.04 1.08
0.01 0.00 1.20
5.20 3.10 0.50
5.25 3.15 0.55
"""


def main():
    device = LidarDevice(device_id="lidar-sim-01", ip_address="192.168.10.42",
                          capabilities=DeviceCapabilities(supports_ptz=False))
    device.add_profile(MediaProfile("main", "Main Stream", (1920, 1080), 20, "POINTCLOUD_PCD"))
    print(f"Device {device.device_id} configured with profile 'main'.")
    print(f"Stream URI: {device.get_stream_uri('main')}\n")

    cloud = PointCloud.from_ascii_pcd(SAMPLE_PCD)
    detected_count = count_points_in_box(
        cloud, x_range=(-0.5, 0.5), y_range=(-0.5, 0.5), z_range=(0.8, 1.4)
    )
    expected_count = 4
    point_count_ok = detected_count == expected_count
    print(f"Point-cloud region check: expected {expected_count} points in ROI, found {detected_count} — {'PASS' if point_count_ok else 'FAIL'}\n")

    milestone_reqs = DeviceCapabilities(supports_media=True, supports_ptz=False, supports_analytics=True, supports_events=True)
    genetec_reqs = DeviceCapabilities(supports_media=True, supports_ptz=True, supports_analytics=False, supports_events=True)

    results = [
        run_integration_test(device, "Milestone XProtect", milestone_reqs, "main", point_count_ok),
        run_integration_test(device, "Genetec Security Center", genetec_reqs, "main", point_count_ok),
    ]

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.vms_platform}: unmet={r.unmet_capabilities or 'none'}, stream_resolved={r.stream_uri_resolved}")

    summary = summarize_results(results)
    print(f"\nSummary: {summary['total_passed']}/{summary['total_tests']} platforms passed ({summary['pass_rate_pct']}%)")
    for platform, stats in summary["by_platform"].items():
        print(f"  {platform}: {stats['passed']}/{stats['tested']} passed")


if __name__ == "__main__":
    main()
