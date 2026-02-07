"""
Zoom Engine for the MP4 Zoom Viewer application.

This module provides the ZoomEngine class which manages zoom level,
tracking position, and region of interest (ROI) calculations for the
magnified zoom window view.
"""

from src.models.data_models import Point, Rectangle, Frame
import numpy as np
import cv2


class ZoomEngine:
    """
    Manages zoom level and region of interest calculations for the zoom window.
    
    The ZoomEngine is responsible for:
    - Maintaining and validating zoom levels (1.5x to 20.0x)
    - Tracking the center position for the zoom window
    - Calculating the region of interest (ROI) bounds
    - Extracting and magnifying frames for the zoom window
    
    Attributes:
        _zoom_level: Current zoom magnification level
        _tracking_position: Current center point being tracked
        _frame_width: Width of the source video frame
        _frame_height: Height of the source video frame
    """
    
    # Zoom level constraints as per Requirements 3.2
    MIN_ZOOM_LEVEL = 1.5
    MAX_ZOOM_LEVEL = 20.0
    
    def __init__(self, frame_width: int = 0, frame_height: int = 0):
        """
        Initialize the ZoomEngine.
        
        Args:
            frame_width: Width of the source video frame (optional, can be set later)
            frame_height: Height of the source video frame (optional, can be set later)
        """
        self._zoom_level = self.MIN_ZOOM_LEVEL
        self._tracking_position = Point(x=0, y=0)
        self._frame_width = frame_width
        self._frame_height = frame_height
    
    def set_zoom_level(self, level: float) -> None:
        """
        Set the zoom level with validation and clamping.
        
        Per Requirement 3.2, zoom levels must be between 1.5x and 20.0x.
        Per Requirement 3.4, values outside this range are clamped to the nearest boundary.
        
        Args:
            level: Desired zoom level (will be clamped to [1.5, 20.0])
        """
        # Clamp the zoom level to valid range (Requirement 3.4)
        if level < self.MIN_ZOOM_LEVEL:
            self._zoom_level = self.MIN_ZOOM_LEVEL
        elif level > self.MAX_ZOOM_LEVEL:
            self._zoom_level = self.MAX_ZOOM_LEVEL
        else:
            self._zoom_level = level
    
    def get_zoom_level(self) -> float:
        """
        Get the current zoom level.
        
        Returns:
            Current zoom magnification level
        """
        return self._zoom_level
    
    def set_tracking_position(self, x: int, y: int) -> None:
        """
        Update the center position for the region of interest.
        
        Per Requirements 4.1 and 4.2, this updates the tracking region to center
        on the specified coordinates (typically from cursor position or click).
        
        Args:
            x: X coordinate of the new tracking center
            y: Y coordinate of the new tracking center
        """
        self._tracking_position = Point(x=x, y=y)
    
    def get_tracking_position(self) -> Point:
        """
        Get the current tracking position.
        
        Returns:
            Current center point being tracked
        """
        return self._tracking_position
    
    def set_frame_dimensions(self, width: int, height: int) -> None:
        """
        Set the dimensions of the source video frame.
        
        This is needed for ROI boundary calculations to ensure the ROI
        stays within frame bounds.
        
        Args:
            width: Width of the source video frame
            height: Height of the source video frame
        """
        self._frame_width = width
        self._frame_height = height
    
    def get_roi_bounds(self) -> Rectangle:
        """
        Calculate the region of interest rectangle based on current zoom level and tracking position.
        
        The ROI is calculated such that:
        1. It is centered on the tracking position
        2. Its size is inversely proportional to the zoom level
        3. It is clamped to stay within frame boundaries
        
        Per Requirement 3.3, the center point of the tracking region is maintained
        when zoom level changes.
        
        Returns:
            Rectangle defining the ROI bounds in the source frame
        """
        if self._frame_width == 0 or self._frame_height == 0:
            # No frame dimensions set, return empty rectangle
            return Rectangle(x=0, y=0, width=0, height=0)
        
        # Calculate ROI dimensions (inversely proportional to zoom level)
        # At 1.5x zoom, ROI is 2/3 of frame size
        # At 20.0x zoom, ROI is 1/20 of frame size
        roi_width = int(self._frame_width / self._zoom_level)
        roi_height = int(self._frame_height / self._zoom_level)
        
        # Calculate top-left corner to center ROI on tracking position
        roi_x = self._tracking_position.x - roi_width // 2
        roi_y = self._tracking_position.y - roi_height // 2
        
        # Clamp ROI to stay within frame boundaries
        # Ensure ROI doesn't extend beyond left/top edges
        roi_x = max(0, roi_x)
        roi_y = max(0, roi_y)
        
        # Ensure ROI doesn't extend beyond right/bottom edges
        if roi_x + roi_width > self._frame_width:
            roi_x = self._frame_width - roi_width
        if roi_y + roi_height > self._frame_height:
            roi_y = self._frame_height - roi_height
        
        # Final safety check to ensure non-negative coordinates
        roi_x = max(0, roi_x)
        roi_y = max(0, roi_y)
        
        return Rectangle(x=roi_x, y=roi_y, width=roi_width, height=roi_height)
    
    def is_valid_zoom_level(self, level: float) -> bool:
        """
        Check if a zoom level is within the valid range.
        
        Per Requirement 3.2, valid zoom levels are between 1.5x and 20.0x inclusive.
        
        Args:
            level: Zoom level to validate
            
        Returns:
            True if the level is within [1.5, 20.0], False otherwise
        """
        return self.MIN_ZOOM_LEVEL <= level <= self.MAX_ZOOM_LEVEL
    
    def get_zoomed_frame(self, source_frame: Frame) -> np.ndarray:
        """
        Extract the ROI from the source frame without upscaling.
        
        This method:
        1. Calculates the current ROI bounds
        2. Extracts that region from the source frame at native resolution
        3. Returns the ROI data directly for maximum quality
        
        Per Requirement 3.3, handles edge cases where ROI extends beyond frame boundaries.
        
        Args:
            source_frame: The source video frame to extract from
            
        Returns:
            ROI frame data as numpy array at native resolution
        """
        # Update frame dimensions if they've changed
        if source_frame.width != self._frame_width or source_frame.height != self._frame_height:
            self.set_frame_dimensions(source_frame.width, source_frame.height)
        
        # Get the ROI bounds
        roi = self.get_roi_bounds()
        
        # Handle empty ROI
        if roi.width == 0 or roi.height == 0:
            return source_frame.data
        
        # Extract the ROI from the source frame at native resolution
        roi_data = source_frame.data[roi.y:roi.y + roi.height, roi.x:roi.x + roi.width]
        
        # Return the ROI at native resolution (no upscaling for better quality)
        return roi_data
