# LiDAR / VMS Interoperability Test Harness

A tested Python project that models the shape of LiDAR-device-to-Video-Management-System (VMS) interoperability testing: device capability negotiation, RTSP stream-URI resolution, 3D point-cloud region validation, and compliance reporting. It covers the three-part check at the heart of device integration work: negotiating what a device and a VMS platform each support, resolving a stream endpoint, and validating a point-cloud region against an expected count.

## Scope

**This is not a real ONVIF implementation, and it has never talked to a real LiDAR sensor or a real VMS platform.** There is no SOAP/WSDL layer, no ONVIF Device Test Tool conformance, no real network device, and no access to Milestone XProtect, Genetec, or any other actual VMS software. What's here instead:

1. **`src/onvif_device.py`** — a hand-written model of the *shape* of ONVIF Device Management and Media service interactions: capability negotiation (`GetCapabilities`-style), media profile configuration, and RTSP stream-URI resolution (`GetStreamUri`-style). It demonstrates the integration pattern a device's software stack needs to expose, not conformance to the real ONVIF specification or an interop test against a vendor's actual device.

2. **`src/point_cloud.py`** — basic 3D point-cloud utilities (parsing a simplified ASCII point format, counting points within a box or radius region of interest, computing a bounding box) implemented directly in Python/NumPy. It does not use `open3d` (not installed in my sandbox, and no real LiDAR sensor output was available to test against); the point-cloud logic is hand-built and tested against synthetic point sets, not validated against a real sensor's output format.

3. **`src/integration_report.py`** — runs simulated interoperability tests of a simulated device against named VMS platforms' capability requirements, and produces a pass/fail compliance summary, documenting integration results and compliance findings on synthetic data.

4. **`run_demo.py`** — runs the full simulated flow end to end and prints a console report (see sample output below, copied from an actual run).

## Why this exists

Device integration work typically involves ONVIF, RTSP, and point-cloud region counting. I built the actual shape of that work in plain Python so it can be tested: negotiating what a device and a VMS platform each support, resolving a stream endpoint, and validating a point-cloud region against an expected count.

## Testing

27 automated tests (`tests/`), all passing on the first full run, covering: device capability negotiation (fully met, partially met, and correctly *not* flagging capabilities the VMS doesn't require), media-profile stream limits and stream-URI construction, point-cloud parsing (including malformed input and empty clouds), box- and radius-based region point-counting (including edge cases at cluster boundaries and empty clouds), and end-to-end integration-test result summarization across multiple simulated VMS platforms.

```bash
python3 -m pytest -v    # 27 tests, all passing
python3 run_demo.py     # runs a full simulated interoperability-test cycle
```

## Sample output (from an actual run)

```
Device lidar-sim-01 configured with profile 'main'.
Stream URI: rtsp://192.168.10.42:554/onvif/main

Point-cloud region check: expected 4 points in ROI, found 4 — PASS

[PASS] Milestone XProtect: unmet=none, stream_resolved=True
[FAIL] Genetec Security Center: unmet=['ptz'], stream_resolved=True

Summary: 1/2 platforms passed (50.0%)
  Milestone XProtect: 1/1 passed
  Genetec Security Center: 0/1 passed
```

## Notes

- No real hardware, LiDAR sensor, or VMS/CCTV platform was used. Milestone XProtect and Genetec Security Center appear only as realistic named examples of the kind of platform a device is tested against.
- The project uses no SOAP/WSDL, real ONVIF conformance testing, `open3d`, `gRPC`, `Protobuf`, or `gStreamer`; it demonstrates the *shape* of the integration and validation logic in plain Python.
- The point-cloud data is entirely synthetic, generated to demonstrate the counting and validation logic, and isn't derived from any real sensor's output.
