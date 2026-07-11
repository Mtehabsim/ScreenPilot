"""Screen-stability perception helpers (cross-platform).

The timing data showed ~98% of blocking time is the agent loop (reasoning +
round-trips), not tool work. The biggest lever is therefore FEWER round-trips.
`capture_when_stable` supports that: instead of the agent doing
"act -> screenshot -> still loading? -> screenshot -> screenshot ...", a tool
can act once, wait server-side until the screen stops changing, and return a
single settled screenshot. One round-trip instead of several.

Pure pyautogui + PIL, so it works on any platform ScreenPilot already supports.
"""
import time
import pyautogui
from PIL import Image as PILImage, ImageChops

from timing import section

# Downscale to a tiny grayscale fingerprint for fast frame comparison. 64x64 is
# plenty to detect meaningful UI changes while ignoring sub-pixel noise.
_FP_SIZE = (64, 64)
# Mean per-pixel difference (0-255 scale) below which two frames count as "same".
# Small enough to catch real content changes, large enough to ignore cursor
# blink / anti-aliasing jitter.
_DIFF_THRESHOLD = 3.0


def _fingerprint(img):
    return img.convert("L").resize(_FP_SIZE, PILImage.BILINEAR)


def _mean_diff(fp_a, fp_b) -> float:
    """Mean absolute per-pixel difference between two fingerprints (0-255)."""
    diff = ImageChops.difference(fp_a, fp_b)
    hist = diff.histogram()
    total = sum(i * c for i, c in enumerate(hist))
    count = sum(hist)
    return (total / count) if count else 0.0


def frames_differ(img_a, img_b, threshold: float = _DIFF_THRESHOLD) -> bool:
    """True if two PIL screenshots differ meaningfully (screen-diff signal)."""
    return _mean_diff(_fingerprint(img_a), _fingerprint(img_b)) > threshold


def capture_when_stable(timeout: float = 6.0, poll_interval: float = 0.1,
                        stability_period: float = 0.25, threshold: float = _DIFF_THRESHOLD):
    """Poll the screen until it stops changing, then return the settled frame.

    Args:
        timeout: hard cap; return the latest frame even if never fully stable
                 (e.g. a page with a constant animation/spinner).
        poll_interval: sleep between captures.
        stability_period: screen must stay unchanged this long to count settled.
        threshold: mean per-pixel diff below which frames are considered equal.

    Returns:
        (screenshot, info) where screenshot is a PIL image and info has:
        stabilized (bool), waited_ms (float), frames (int).
    """
    t0 = time.perf_counter()
    with section("capture"):
        last = pyautogui.screenshot()
    last_fp = _fingerprint(last)
    stable_since = None
    frames = 1

    while True:
        elapsed = time.perf_counter() - t0
        if elapsed >= timeout:
            return last, {"stabilized": False,
                          "waited_ms": round(elapsed * 1000, 1),
                          "frames": frames}
        time.sleep(poll_interval)
        with section("capture"):
            cur = pyautogui.screenshot()
        frames += 1
        cur_fp = _fingerprint(cur)
        changed = _mean_diff(last_fp, cur_fp) > threshold
        last, last_fp = cur, cur_fp
        now = time.perf_counter()

        if changed:
            stable_since = None
        else:
            if stable_since is None:
                stable_since = now
            elif (now - stable_since) >= stability_period:
                return cur, {"stabilized": True,
                             "waited_ms": round((now - t0) * 1000, 1),
                             "frames": frames}
