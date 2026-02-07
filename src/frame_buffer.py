"""
Thread-safe frame buffer for the MP4 Zoom Viewer application.

This module provides a FrameBuffer class that allows multiple consumers
(main player, zoom window, template matcher) to safely access the current
video frame in a multi-threaded environment.
"""

import threading
from typing import Tuple
import numpy as np
from src.models.data_models import Frame


class FrameBuffer:
    """
    Thread-safe buffer for storing and accessing the current video frame.
    
    The FrameBuffer uses a read-write lock (RLock) to ensure thread safety
    when multiple consumers need to access the current frame. It stores only
    the current frame to minimize memory overhead.
    
    Attributes:
        _lock: Reentrant lock for thread-safe access
        _current_frame: The currently stored frame (None if no frame set)
        _current_timestamp: Timestamp of the current frame in seconds
    """
    
    def __init__(self):
        """Initialize an empty FrameBuffer with thread safety."""
        self._lock = threading.RLock()
        self._current_frame: Frame | None = None
        self._current_timestamp: float = 0.0
    
    def update_frame(self, frame: Frame, timestamp: float) -> None:
        """
        Store a new frame in the buffer with thread safety.
        
        This method updates the buffer with a new frame and timestamp.
        The operation is atomic and thread-safe.
        
        Args:
            frame: The Frame object to store
            timestamp: The timestamp of the frame in seconds from video start
        """
        with self._lock:
            self._current_frame = frame
            self._current_timestamp = timestamp
    
    def get_current_frame(self) -> Tuple[Frame | None, float]:
        """
        Retrieve the current frame and timestamp.
        
        This method returns a reference to the current frame (not a copy).
        Consumers should not modify the returned frame data. For modifications,
        use get_frame_copy() instead.
        
        Returns:
            A tuple containing:
                - The current Frame object (or None if no frame has been set)
                - The timestamp in seconds
        """
        with self._lock:
            return self._current_frame, self._current_timestamp
    
    def get_frame_copy(self) -> Frame | None:
        """
        Create a deep copy of the current frame.
        
        This method is useful for consumers that need to modify the frame
        data without affecting other consumers. The numpy array is deep copied
        to ensure complete independence.
        
        Returns:
            A new Frame object with deep-copied data, or None if no frame is set
        """
        with self._lock:
            if self._current_frame is None:
                return None
            
            # Deep copy the numpy array
            frame_data_copy = np.copy(self._current_frame.data)
            
            # Create a new Frame object with the copied data
            return Frame(
                data=frame_data_copy,
                width=self._current_frame.width,
                height=self._current_frame.height,
                timestamp=self._current_frame.timestamp,
                frame_number=self._current_frame.frame_number
            )
