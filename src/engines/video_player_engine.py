"""
Video Player Engine for the MP4 Zoom Viewer application.

This module provides the VideoPlayerEngine class that handles MP4 video loading,
decoding, playback control, and frame delivery using OpenCV's VideoCapture.
"""

import cv2
import threading
from typing import Callable, Optional
from pathlib import Path
from src.models.data_models import Frame, VideoMetadata, PlaybackState
from src.frame_buffer import FrameBuffer


class VideoPlayerError(Exception):
    """Base exception for video player errors."""
    pass


class VideoPlayerEngine:
    """
    Manages MP4 video loading, playback, and frame delivery.
    
    The VideoPlayerEngine uses OpenCV's VideoCapture for video decoding and
    provides methods for playback control (play, pause, stop, seek). It runs
    a playback loop in a separate thread to avoid blocking the UI and delivers
    frames to a FrameBuffer for consumption by other components.
    
    Attributes:
        _capture: OpenCV VideoCapture object
        _metadata: Video metadata information
        _playback_state: Current playback state
        _frame_buffer: FrameBuffer for storing current frame
        _playback_thread: Background thread for playback loop
        _frame_callbacks: List of callbacks to invoke for each frame
        _stop_event: Threading event to signal playback thread to stop
    """
    
    def __init__(self, frame_buffer: Optional[FrameBuffer] = None):
        """
        Initialize the VideoPlayerEngine.
        
        Args:
            frame_buffer: Optional FrameBuffer instance. If None, creates a new one.
        """
        self._capture: Optional[cv2.VideoCapture] = None
        self._metadata: Optional[VideoMetadata] = None
        self._playback_state: PlaybackState = PlaybackState.STOPPED
        self._frame_buffer: FrameBuffer = frame_buffer if frame_buffer else FrameBuffer()
        self._playback_thread: Optional[threading.Thread] = None
        self._frame_callbacks: list[Callable[[Frame], None]] = []
        self._stop_event: threading.Event = threading.Event()
        self._lock: threading.RLock = threading.RLock()
    
    def load_video(self, file_path: str) -> VideoMetadata:
        """
        Load an MP4 video file and extract metadata.
        
        This method opens the video file using OpenCV's VideoCapture, validates
        that it can be opened successfully, and extracts metadata including fps,
        dimensions, frame count, duration, and codec information.
        
        Args:
            file_path: Path to the MP4 video file
            
        Returns:
            VideoMetadata object containing video information
            
        Raises:
            VideoPlayerError: If the file cannot be loaded or is invalid
        """
        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            raise VideoPlayerError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise VideoPlayerError(f"Path is not a file: {file_path}")
        
        # Try to open the video file
        capture = cv2.VideoCapture(str(path))
        
        if not capture.isOpened():
            capture.release()
            raise VideoPlayerError(
                "File is corrupted or unreadable. Please ensure the file is a valid MP4 video."
            )
        
        # Extract video properties
        try:
            fps = capture.get(cv2.CAP_PROP_FPS)
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fourcc = int(capture.get(cv2.CAP_PROP_FOURCC))
            
            # Validate extracted properties
            if fps <= 0 or width <= 0 or height <= 0 or total_frames <= 0:
                capture.release()
                raise VideoPlayerError(
                    "Unsupported file format. Please select a valid MP4 file."
                )
            
            # Calculate duration
            duration = total_frames / fps if fps > 0 else 0.0
            
            # Convert fourcc code to string
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            # Create metadata object
            metadata = VideoMetadata(
                file_path=str(path.absolute()),
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                total_frames=total_frames,
                codec=codec
            )
            
            # Store the capture and metadata
            with self._lock:
                # Release old capture if exists
                if self._capture is not None:
                    self._capture.release()
                
                self._capture = capture
                self._metadata = metadata
                self._playback_state = PlaybackState.STOPPED
            
            return metadata
            
        except Exception as e:
            capture.release()
            if isinstance(e, VideoPlayerError):
                raise
            raise VideoPlayerError(f"Error reading video properties: {str(e)}")
    
    def get_video_metadata(self) -> Optional[VideoMetadata]:
        """
        Get the metadata of the currently loaded video.
        
        Returns:
            VideoMetadata object if a video is loaded, None otherwise
        """
        with self._lock:
            return self._metadata
    
    def get_playback_state(self) -> PlaybackState:
        """
        Get the current playback state.
        
        Returns:
            Current PlaybackState (STOPPED, PLAYING, or PAUSED)
        """
        with self._lock:
            return self._playback_state
    
    def get_current_frame(self) -> Optional[Frame]:
        """
        Get the current frame from the frame buffer.
        
        Returns:
            Current Frame object, or None if no frame is available
        """
        frame, _ = self._frame_buffer.get_current_frame()
        return frame
    
    def register_frame_callback(self, callback: Callable[[Frame], None]) -> None:
        """
        Register a callback to be invoked for each new frame.
        
        Callbacks are invoked in the playback thread, so they should be
        lightweight and non-blocking to avoid affecting playback performance.
        
        Args:
            callback: Function that takes a Frame object as argument
        """
        with self._lock:
            self._frame_callbacks.append(callback)
    
    def play(self) -> None:
        """
        Start or resume video playback.
        
        This method starts the playback thread if not already running.
        If the video is paused, it resumes from the current position.
        
        Raises:
            VideoPlayerError: If no video is loaded
        """
        with self._lock:
            if self._capture is None or self._metadata is None:
                raise VideoPlayerError("No video loaded. Please load a video first.")
            
            if self._playback_state == PlaybackState.PLAYING:
                return  # Already playing
            
            self._playback_state = PlaybackState.PLAYING
            
            # Start playback thread if not running
            if self._playback_thread is None or not self._playback_thread.is_alive():
                self._stop_event.clear()
                self._playback_thread = threading.Thread(
                    target=self._playback_loop,
                    daemon=True
                )
                self._playback_thread.start()
    
    def pause(self) -> None:
        """
        Pause video playback.
        
        The current frame position is maintained and can be resumed with play().
        """
        with self._lock:
            if self._playback_state == PlaybackState.PLAYING:
                self._playback_state = PlaybackState.PAUSED
    
    def stop(self) -> None:
        """
        Stop video playback and reset to the beginning.
        
        This method stops the playback thread and resets the video position
        to the first frame.
        """
        with self._lock:
            self._playback_state = PlaybackState.STOPPED
            self._stop_event.set()
            
            # Reset video position to beginning
            if self._capture is not None:
                self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Wait for playback thread to finish
        if self._playback_thread is not None and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=1.0)
    
    def seek(self, timestamp: float) -> None:
        """
        Seek to a specific timestamp in the video.
        
        Args:
            timestamp: Target timestamp in seconds from video start
            
        Raises:
            VideoPlayerError: If no video is loaded
        """
        with self._lock:
            if self._capture is None or self._metadata is None:
                raise VideoPlayerError("No video loaded. Cannot seek.")
            
            # Clamp timestamp to valid range
            timestamp = max(0.0, min(timestamp, self._metadata.duration))
            
            # Convert timestamp to frame number
            frame_number = int(timestamp * self._metadata.fps)
            
            # Seek to the frame
            self._capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    def _playback_loop(self) -> None:
        """
        Background thread that reads and delivers frames at the correct rate.
        
        This method runs in a separate thread and continuously reads frames
        from the video, updates the frame buffer, and invokes registered
        callbacks. It handles frame decode errors gracefully by skipping
        failed frames and continuing playback.
        """
        import time
        
        while not self._stop_event.is_set():
            with self._lock:
                if self._playback_state != PlaybackState.PLAYING:
                    time.sleep(0.01)  # Small sleep to avoid busy waiting
                    continue
                
                if self._capture is None or self._metadata is None:
                    break
                
                # Read next frame
                ret, frame_data = self._capture.read()
                
                if not ret:
                    # End of video or read error
                    if self._capture.get(cv2.CAP_PROP_POS_FRAMES) >= self._metadata.total_frames:
                        # End of video - stop playback
                        self._playback_state = PlaybackState.STOPPED
                        self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        # Frame decode error - skip and continue
                        print(f"Warning: Failed to decode frame at position "
                              f"{int(self._capture.get(cv2.CAP_PROP_POS_FRAMES))}")
                    continue
                
                # Get frame metadata
                frame_number = int(self._capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                timestamp = frame_number / self._metadata.fps
                height, width = frame_data.shape[:2]
                
                # Create Frame object
                frame = Frame(
                    data=frame_data,
                    width=width,
                    height=height,
                    timestamp=timestamp,
                    frame_number=frame_number
                )
                
                # Update frame buffer
                self._frame_buffer.update_frame(frame, timestamp)
                
                # Invoke callbacks
                callbacks = self._frame_callbacks.copy()
            
            # Invoke callbacks outside the lock to avoid blocking
            for callback in callbacks:
                try:
                    callback(frame)
                except Exception as e:
                    print(f"Error in frame callback: {e}")
            
            # Sleep to maintain correct frame rate
            if self._metadata is not None and self._metadata.fps > 0:
                frame_time = 1.0 / self._metadata.fps
                time.sleep(frame_time)
    
    def release(self) -> None:
        """
        Release video resources and stop playback.
        
        This method should be called when the engine is no longer needed
        to properly clean up resources.
        """
        self.stop()
        with self._lock:
            if self._capture is not None:
                self._capture.release()
                self._capture = None
            self._metadata = None
    
    def __del__(self):
        """Destructor to ensure resources are released."""
        self.release()
