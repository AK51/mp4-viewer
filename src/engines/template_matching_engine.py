"""
Template Matching Engine for the MP4 Zoom Viewer application.

This module provides the TemplateMatchingEngine class which manages template
selection, validation, and OpenCV-based template matching for automatic object
tracking across video frames.
"""

from typing import Optional, Tuple
from src.models.data_models import Frame, Point, Rectangle, MatchResult
import numpy as np
import cv2


class TemplateMatchingError(Exception):
    """Exception raised for template matching related errors."""
    pass


class TemplateMatchingEngine:
    """
    Manages template selection and matching for automatic object tracking.
    
    The TemplateMatchingEngine is responsible for:
    - Storing and validating user-selected template images
    - Performing OpenCV template matching on video frames
    - Calculating match confidence scores
    - Tracking consecutive failed matches
    - Managing tracking state
    
    Attributes:
        _template: The stored template image data
        _template_width: Width of the template in pixels
        _template_height: Height of the template in pixels
        _source_location: Original location where template was captured
        _last_match_location: Location of the most recent successful match
        _consecutive_failures: Count of consecutive frames with low confidence
        _tracking_active: Whether template tracking is currently active
        _confidence_threshold: Minimum confidence score for valid matches
        _max_consecutive_failures: Maximum failures before tracking loss
    """
    
    # Template size constraints as per Requirements 5.4, 5.5
    MIN_TEMPLATE_SIZE = 10
    MAX_TEMPLATE_SIZE = 200
    
    # Matching parameters as per Requirement 6.5
    CONFIDENCE_THRESHOLD = 0.6
    MAX_CONSECUTIVE_FAILURES = 5
    
    def __init__(self):
        """Initialize the TemplateMatchingEngine."""
        self._template: Optional[np.ndarray] = None
        self._template_width: int = 0
        self._template_height: int = 0
        self._source_location: Optional[Point] = None
        self._last_match_location: Optional[Point] = None
        self._consecutive_failures: int = 0
        self._tracking_active: bool = False
    
    def set_template(self, template_image: Frame, source_location: Point) -> None:
        """
        Store the user-selected template image and validate its size.
        
        Per Requirement 5.1, captures the selected region as the template.
        Per Requirement 5.4, template sizes must be between 10x10 and 200x200 pixels.
        Per Requirement 5.5, templates smaller than 10x10 pixels are rejected.
        Per Requirement 5.3, new templates replace previously selected templates.
        
        Args:
            template_image: Frame containing the template image data
            source_location: Point indicating where the template was captured
            
        Raises:
            TemplateMatchingError: If template dimensions are invalid
        """
        # Validate template dimensions
        width = template_image.width
        height = template_image.height
        
        # Check minimum size (Requirement 5.5)
        if width < self.MIN_TEMPLATE_SIZE or height < self.MIN_TEMPLATE_SIZE:
            raise TemplateMatchingError(
                f"Template must be at least {self.MIN_TEMPLATE_SIZE}x{self.MIN_TEMPLATE_SIZE} pixels."
            )
        
        # Check maximum size (Requirement 5.4)
        if width > self.MAX_TEMPLATE_SIZE or height > self.MAX_TEMPLATE_SIZE:
            raise TemplateMatchingError(
                f"Template must not exceed {self.MAX_TEMPLATE_SIZE}x{self.MAX_TEMPLATE_SIZE} pixels."
            )
        
        # Store the template (Requirement 5.1, 5.3)
        self._template = template_image.data.copy()
        self._template_width = width
        self._template_height = height
        self._source_location = source_location
        
        # Reset tracking state when new template is set
        self._last_match_location = source_location
        self._consecutive_failures = 0
        self._tracking_active = True
    
    def get_template(self) -> Optional[np.ndarray]:
        """
        Get the currently stored template image.
        
        Returns:
            Template image data as numpy array, or None if no template is set
        """
        return self._template
    
    def get_template_size(self) -> Tuple[int, int]:
        """
        Get the dimensions of the currently stored template.
        
        Returns:
            Tuple of (width, height) in pixels, or (0, 0) if no template is set
        """
        return (self._template_width, self._template_height)
    
    def is_tracking_active(self) -> bool:
        """
        Check if template tracking is currently active.
        
        Returns:
            True if tracking is active, False otherwise
        """
        return self._tracking_active
    
    def reset_tracking(self) -> None:
        """
        Reset tracking state and clear the template.
        
        This clears the stored template and resets all tracking state.
        """
        self._template = None
        self._template_width = 0
        self._template_height = 0
        self._source_location = None
        self._last_match_location = None
        self._consecutive_failures = 0
        self._tracking_active = False
    
    def get_current_match_location(self) -> Optional[Point]:
        """
        Get the location of the most recent successful match.
        
        Returns:
            Point indicating the center of the last match, or None if no match yet
        """
        return self._last_match_location
    
    def match_template(self, frame: Frame) -> MatchResult:
        """
        Perform template matching on the given frame using OpenCV.
        
        Per Requirement 6.1, searches for the template in the frame.
        Per Requirement 6.4, uses OpenCV template matching with normalized cross-correlation.
        Per Requirement 6.5, confidence threshold of 0.6 for valid matches.
        Per Requirement 8.2, tracks consecutive failed matches.
        
        Args:
            frame: The video frame to search for the template
            
        Returns:
            MatchResult containing match status, location, confidence, and bounding box
            
        Raises:
            TemplateMatchingError: If no template has been set
        """
        # Check if template is set
        if self._template is None:
            raise TemplateMatchingError("No template selected. Please select a region to track.")
        
        # Ensure frame is large enough to contain template
        if frame.width < self._template_width or frame.height < self._template_height:
            return MatchResult(
                found=False,
                location=None,
                confidence=0.0,
                bounding_box=None
            )
        
        # Perform template matching using normalized cross-correlation (Requirement 6.4)
        result = cv2.matchTemplate(frame.data, self._template, cv2.TM_CCOEFF_NORMED)
        
        # Find the best match location
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # max_val is the confidence score for TM_CCOEFF_NORMED
        confidence = float(max_val)
        
        # Check if confidence meets threshold (Requirement 6.5)
        if confidence >= self.CONFIDENCE_THRESHOLD:
            # Match found - calculate center point
            top_left_x, top_left_y = max_loc
            center_x = top_left_x + self._template_width // 2
            center_y = top_left_y + self._template_height // 2
            
            match_location = Point(x=center_x, y=center_y)
            bounding_box = Rectangle(
                x=top_left_x,
                y=top_left_y,
                width=self._template_width,
                height=self._template_height
            )
            
            # Update tracking state
            self._last_match_location = match_location
            self._consecutive_failures = 0
            
            return MatchResult(
                found=True,
                location=match_location,
                confidence=confidence,
                bounding_box=bounding_box
            )
        else:
            # Match confidence too low (Requirement 6.5)
            self._consecutive_failures += 1
            
            # Check for tracking loss (Requirement 8.2)
            if self._consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                self._tracking_active = False
            
            return MatchResult(
                found=False,
                location=self._last_match_location,  # Maintain previous location
                confidence=confidence,
                bounding_box=None
            )
    
    def get_match_confidence(self) -> float:
        """
        Get the confidence score of the most recent match attempt.
        
        This is primarily used for testing and debugging purposes.
        
        Returns:
            Confidence score from 0.0 to 1.0, or 0.0 if no match attempted yet
        """
        # This would need to be tracked separately if needed
        # For now, return 0.0 as a placeholder
        return 0.0
    
    def get_consecutive_failures(self) -> int:
        """
        Get the count of consecutive failed match attempts.
        
        Returns:
            Number of consecutive frames with confidence below threshold
        """
        return self._consecutive_failures
