"""
Pytest configuration and shared fixtures for MP4 Zoom Viewer tests.
"""

import pytest
from hypothesis import settings, Verbosity

# Configure Hypothesis for property-based testing
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=200, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=10, verbosity=Verbosity.verbose)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.debug)

# Load the default profile
settings.load_profile("default")


@pytest.fixture
def sample_frame_data():
    """Provides sample frame data for testing."""
    import numpy as np
    # Create a simple 640x480 BGR frame with a gradient pattern
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    for i in range(480):
        frame[i, :, 0] = int(i * 255 / 480)  # Blue channel gradient
    return frame


@pytest.fixture
def sample_video_metadata():
    """Provides sample video metadata for testing."""
    return {
        'file_path': 'test_video.mp4',
        'duration': 10.0,
        'fps': 30.0,
        'width': 1920,
        'height': 1080,
        'total_frames': 300,
        'codec': 'h264'
    }


@pytest.fixture
def temp_video_file(tmp_path):
    """Creates a temporary video file for testing."""
    video_path = tmp_path / "test_video.mp4"
    # Note: Actual video creation would require OpenCV
    # This is a placeholder that returns the path
    return str(video_path)
