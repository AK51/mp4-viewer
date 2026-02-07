"""
Data models for the MP4 Zoom Viewer application.

This module contains all the core data structures used throughout the application,
including Frame, VideoMetadata, geometric types (Point, Rectangle), and state enums.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import numpy as np


@dataclass
class Frame:
    """
    Represents a single video frame with associated metadata.
    
    Attributes:
        data: OpenCV image array in BGR format
        width: Frame width in pixels
        height: Frame height in pixels
        timestamp: Time in seconds from video start
        frame_number: Sequential frame number (0-indexed)
    """
    data: np.ndarray
    width: int
    height: int
    timestamp: float
    frame_number: int


@dataclass
class VideoMetadata:
    """
    Metadata information about a loaded video file.
    
    Attributes:
        file_path: Full path to the video file
        duration: Total video duration in seconds
        fps: Frames per second
        width: Video frame width in pixels
        height: Video frame height in pixels
        total_frames: Total number of frames in the video
        codec: Video codec identifier
    """
    file_path: str
    duration: float
    fps: float
    width: int
    height: int
    total_frames: int
    codec: str


@dataclass
class Point:
    """
    Represents a 2D point coordinate.
    
    Attributes:
        x: X coordinate (horizontal position)
        y: Y coordinate (vertical position)
    """
    x: int
    y: int


@dataclass
class Rectangle:
    """
    Represents a rectangular region.
    
    Attributes:
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Rectangle width in pixels
        height: Rectangle height in pixels
    """
    x: int
    y: int
    width: int
    height: int


class PlaybackState(Enum):
    """
    Enumeration of possible video playback states.
    """
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class TrackingMode(Enum):
    """
    Enumeration of zoom window tracking modes.
    """
    MANUAL = "manual"      # User controls zoom position with cursor
    TEMPLATE = "template"  # Zoom follows template matching results


@dataclass
class ZoomState:
    """
    Represents the current state of the zoom window.
    
    Attributes:
        active: Whether the zoom window is currently active
        zoom_level: Current magnification level (1.5 to 10.0)
        tracking_position: Current center point being tracked
        tracking_mode: Current tracking mode (manual or template)
    """
    active: bool
    zoom_level: float
    tracking_position: Point
    tracking_mode: TrackingMode


@dataclass
class MatchResult:
    """
    Result of a template matching operation.
    
    Attributes:
        found: Whether a match was found above confidence threshold
        location: Center point of the matched region (None if not found)
        confidence: Match confidence score (0.0 to 1.0)
        bounding_box: Rectangle defining the matched region (None if not found)
    """
    found: bool
    location: Optional[Point]
    confidence: float
    bounding_box: Optional[Rectangle]
