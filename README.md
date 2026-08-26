# LiDAR / VMS Interoperability Test Harness

A real, tested Python project that models the shape of LiDAR-device-to-Video-Management-System (VMS) interoperability testing — device capability negotiation, RTSP stream-URI resolution, 3D point-cloud region validation, and compliance reporting — built specifically to close a gap identified against Blickfeld GmbH's "Working Student / IDP: Software Development" posting: nothing in this portfolio previously touched device software, video-surveillance protocols, or point-cloud data at all.

## What this is (read before citing anywhere)

**This is not a real ONVIF implementation, and it has never talked to a real LiDAR sensor or a real VMS platform.** There is no SOAP/WSDL layer, no ONVIF Device Test Tool conformance, no real network device, and no access to Milestone XProtect, Genetec, or any other actual VMS software. What's here instead:

1. **`src/onvif_device.py`** — a hand-written model of the *shape* of ONVIF Device Management and Media service interactions: capability negotiation (`GetCapabilities`-style), media profile configuration, and RTSP stream-URI resolution (`GetStreamUri`-style). This demonstrates understanding of the integration pattern a device's software stack needs to expose, not conformance to the real ONVIF specification or a real interop test against Blickfeld's or any vendor's actual device.

2. **`src/point_cloud.py`** — basic 3D point-cloud utilities (parsing a simplified ASCII point format, counting points within a box or radius region of interest, computing a bounding box) implemented directly in Python/NumPy. **This does not use `open3d`** (not installed in this sandbox, and no real LiDAR sensor output was available to test against) — the point-cloud logic here is hand-built and tested against synthetic point sets, not validated against a real Blickfeld sensor's output format.

3. **`src/integration_report.py`** — runs simulated interoperability tests of a simulated device against named VMS platforms' capability requirements, and produces a pass/fail compliance summary — modeling the "Validation & Documentation" task in the posting (documenting integration results and compliance findings), on synthetic data only.

4. **`run_demo.py`** — runs the full simulated flow end to end and prints a real console report (see sample output below, copied from an actual run).

## Why this exists

The posting's core technical stack — ONVIF, RTSP, gStreamer, gRPC, Protobuf, and manual point-cloud region counting — had zero coverage anywhere in this portfolio before this project. Rather than stretch an unrelated project's framing to imply protocol-integration experience that doesn't exist, this project builds the actual shape of the work: negotiating what a device and a VMS platform each support, resolving a stream endpoint, and validating a point-cloud region against an expected count — the same three-part interoperability check named directly in the posting's task list.

## Verification

27 automated tests (`tests/`), all passing on the first full run, covering: device capability negotiation (fully met, partially met, and correctly *not* flagging capabilities the VMS doesn't require), media-profile stream limits and stream-URI construction, point-cloud parsing (including malformed input and empty clouds), box- and radius-based region point-counting (including edge cases at cluster boundaries and empty clouds), and end-to-end integration-test result summarization across multiple simulated VMS platforms.

```bash
python3 -m pytest -v    # 27 tests, all passing
python3 run_demo.py     # runs a full simulated interoperability-test cycle
```

## Sample output (from an actual run)

```
Device blickfeld-sim-01 configured with profile 'main'.
Stream URI: rtsp://192.168.10.42:554/onvif/main

Point-cloud region check: expected 4 points in ROI, found 4 — PASS

[PASS] Milestone XProtect: unmet=none, stream_resolved=True
[FAIL] Genetec Security Center: unmet=['ptz'], stream_resolved=True

Summary: 1/2 platforms passed (50.0%)
  Milestone XProtect: 1/1 passed
  Genetec Security Center: 0/1 passed
```

## Honest limitations

- No real hardware, no real LiDAR sensor, no real VMS/CCTV platform (Milestone XProtect and Genetec Security Center are referenced only as realistic named examples of the kind of platform this role would test against — no real integration with either was performed or claimed).
- No SOAP/WSDL, no real ONVIF conformance testing, no `open3d`, no `gRPC`/`Protobuf`/`gStreamer` usage — this project demonstrates the *shape* of the integration and validation logic in plain Python, not hands-on experience with those specific libraries or protocols.
- The point-cloud data is entirely synthetic, generated to demonstrate the counting/validation logic, not derived from or claiming to match any real Blickfeld sensor output.
- This closes part of the gap against the posting (interoperability-testing logic, capability negotiation, point-cloud region validation, structured documentation) — it does not close the CMake/Asyncio/gRPC/Protobuf/RTSP-streaming/gStreamer/ONVIF-conformance gap, which remains real and is disclosed as such in the CV and cover letter.
