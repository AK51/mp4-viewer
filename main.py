"""
MP4 Zoom Viewer - Main Application Entry Point

This is a minimal demonstration of the MP4 Zoom Viewer application that
wires together the VideoPlayerEngine, ZoomEngine, and TemplateMatchingEngine
to provide basic video playback with zoom capabilities.

Usage:
    python main.py [video_file_path]
    
If no video file path is provided, the application will prompt for one.
"""

import sys
import argparse
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFileDialog, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
import cv2
import numpy as np

from src.engines import VideoPlayerEngine, ZoomEngine, TemplateMatchingEngine
from src.frame_buffer import FrameBuffer
from src.models import Frame, PlaybackState


# Matrix Theme Color Palette
MATRIX_GREEN = "#00FF41"
MATRIX_GREEN_DARK = "#003300"
MATRIX_GREEN_GLOW = "#00FF00"
MATRIX_BLACK = "#000000"
MATRIX_GRAY = "#0A0A0A"


class VideoDisplayWidget(QLabel):
    """Widget for displaying video frames with mouse click support."""
    
    # Signal emitted when user clicks on the video (x, y in video coordinates)
    clicked = pyqtSignal(int, int)
    
    def __init__(self, title="Video", clickable=False, matrix_theme=False):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setAlignment(Qt.AlignCenter)
        
        # Apply Matrix theme styling if requested
        if matrix_theme:
            self.setStyleSheet(f"""
                QLabel {{ 
                    background-color: {MATRIX_BLACK}; 
                    color: {MATRIX_GREEN};
                    border: 2px solid {MATRIX_GREEN_DARK};
                }}
            """)
        else:
            self.setStyleSheet("QLabel { background-color: black; }")
        
        self.setText(f"{title}\n(No video loaded)")
        
        self.clickable = clickable
        self.video_width = 0
        self.video_height = 0
        self.scaled_pixmap_rect = None
        
        if clickable:
            self.setCursor(Qt.CrossCursor)
    
    def display_frame(self, frame_data: np.ndarray):
        """Display a video frame (OpenCV BGR format)."""
        if frame_data is None or frame_data.size == 0:
            return
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        
        # Store video dimensions for coordinate mapping
        self.video_width = width
        self.video_height = height
        
        # Create QImage and scale to fit widget
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fit widget while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Calculate the position of the scaled pixmap within the widget
        x_offset = (self.width() - scaled_pixmap.width()) // 2
        y_offset = (self.height() - scaled_pixmap.height()) // 2
        self.scaled_pixmap_rect = (x_offset, y_offset, scaled_pixmap.width(), scaled_pixmap.height())
        
        self.setPixmap(scaled_pixmap)
    
    def mousePressEvent(self, event):
        """Handle mouse click events."""
        if not self.clickable or self.video_width == 0 or self.scaled_pixmap_rect is None:
            return
        
        # Get click position in widget coordinates
        click_x = event.x()
        click_y = event.y()
        
        # Get scaled pixmap position and size
        x_offset, y_offset, scaled_width, scaled_height = self.scaled_pixmap_rect
        
        # Check if click is within the scaled pixmap
        if (x_offset <= click_x < x_offset + scaled_width and
            y_offset <= click_y < y_offset + scaled_height):
            
            # Convert widget coordinates to video coordinates
            relative_x = click_x - x_offset
            relative_y = click_y - y_offset
            
            # Scale to video dimensions
            video_x = int((relative_x / scaled_width) * self.video_width)
            video_y = int((relative_y / scaled_height) * self.video_height)
            
            # Clamp to video bounds
            video_x = max(0, min(video_x, self.video_width - 1))
            video_y = max(0, min(video_y, self.video_height - 1))
            
            # Emit signal with video coordinates
            self.clicked.emit(video_x, video_y)


class FloatingZoomWindow(QDialog):
    """Floating zoom window with Matrix theme styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ZOOM WINDOW - ENHANCED VIEW")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(800, 600)
        
        # Apply Matrix theme
        self._setup_matrix_theme()
        self._setup_ui()
    
    def _setup_matrix_theme(self):
        """Apply Matrix movie-style theme to the window."""
        # Use monospace font for tech look
        matrix_font = QFont("Courier New", 10, QFont.Bold)
        self.setFont(matrix_font)
        
        # Matrix theme stylesheet
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MATRIX_BLACK};
                border: 3px solid {MATRIX_GREEN};
            }}
            QLabel {{
                color: {MATRIX_GREEN};
                background-color: {MATRIX_BLACK};
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {MATRIX_BLACK};
                color: {MATRIX_GREEN};
                border: 2px solid {MATRIX_GREEN_DARK};
                padding: 5px 15px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                border: 2px solid {MATRIX_GREEN};
                background-color: {MATRIX_GREEN_DARK};
            }}
            QPushButton:pressed {{
                background-color: {MATRIX_GREEN};
                color: {MATRIX_BLACK};
            }}
        """)
    
    def _setup_ui(self):
        """Setup the floating window UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header with status indicators
        header_layout = QHBoxLayout()
        
        # Status LED indicator
        self.status_led = QLabel("●")
        self.status_led.setStyleSheet(f"color: {MATRIX_GREEN_GLOW}; font-size: 20px;")
        header_layout.addWidget(self.status_led)
        
        # Title
        title_label = QLabel("[ ENHANCED ZOOM VIEW ]")
        title_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Zoom level display
        self.zoom_level_label = QLabel("ZOOM: 1.5x")
        self.zoom_level_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-size: 12px;")
        header_layout.addWidget(self.zoom_level_label)
        
        layout.addLayout(header_layout)
        
        # Video display with Matrix theme
        self.video_display = VideoDisplayWidget("ZOOM VIEW", clickable=False, matrix_theme=True)
        self.video_display.setMinimumSize(640, 480)
        layout.addWidget(self.video_display)
        
        # Footer with position info
        footer_layout = QHBoxLayout()
        
        self.position_label = QLabel("POSITION: (0, 0)")
        self.position_label.setStyleSheet(f"color: {MATRIX_GREEN_DARK}; font-size: 10px;")
        footer_layout.addWidget(self.position_label)
        
        footer_layout.addStretch()
        
        # Close button
        close_button = QPushButton("[ CLOSE ]")
        close_button.clicked.connect(self.close)
        footer_layout.addWidget(close_button)
        
        layout.addLayout(footer_layout)
    
    def update_frame(self, frame_data: np.ndarray):
        """Update the displayed frame."""
        self.video_display.display_frame(frame_data)
        # Pulse the status LED
        self.status_led.setStyleSheet(f"color: {MATRIX_GREEN_GLOW}; font-size: 20px;")
    
    def update_zoom_level(self, zoom_level: float):
        """Update the zoom level display."""
        self.zoom_level_label.setText(f"ZOOM: {zoom_level:.1f}x")
    
    def update_position(self, x: int, y: int):
        """Update the position display."""
        self.position_label.setText(f"POSITION: ({x}, {y})")


class MainPlayerWindow(QMainWindow):
    """Main application window with video player and zoom controls."""
    
    def __init__(self, video_path: str = None):
        super().__init__()
        self.setWindowTitle("MP4 ZOOM VIEWER - MATRIX INTERFACE")
        
        # Initialize components
        self.frame_buffer = FrameBuffer()
        self.video_player = VideoPlayerEngine(self.frame_buffer)
        self.zoom_engine = ZoomEngine()
        self.template_matcher = TemplateMatchingEngine()
        
        # Floating zoom window
        self.floating_zoom_window = None
        
        # State
        self.zoom_window_active = False
        self.current_frame = None
        self.template_tracking_active = False
        self.template_set = False
        
        # Apply Matrix theme to main window
        self._setup_matrix_theme()
        
        # Setup UI
        self._setup_ui()
        
        # Setup timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(33)  # ~30 fps UI update
        
        # Load video if provided
        if video_path:
            try:
                self._load_video(video_path)
            except Exception as e:
                # If default video fails to load, just show error in status
                self.status_label.setText(f"Failed to load default video: {str(e)}")
                print(f"Error loading video '{video_path}': {e}")
    
    def _setup_matrix_theme(self):
        """Apply Matrix theme to main window."""
        matrix_font = QFont("Courier New", 9, QFont.Bold)
        self.setFont(matrix_font)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {MATRIX_BLACK};
            }}
            QWidget {{
                background-color: {MATRIX_BLACK};
                color: {MATRIX_GREEN};
                font-family: 'Courier New', monospace;
            }}
            QLabel {{
                color: {MATRIX_GREEN};
                background-color: {MATRIX_BLACK};
                font-family: 'Courier New', monospace;
            }}
            QPushButton {{
                background-color: {MATRIX_BLACK};
                color: {MATRIX_GREEN};
                border: 2px solid {MATRIX_GREEN_DARK};
                padding: 8px 15px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                border: 2px solid {MATRIX_GREEN};
                background-color: {MATRIX_GREEN_DARK};
            }}
            QPushButton:pressed {{
                background-color: {MATRIX_GREEN};
                color: {MATRIX_BLACK};
            }}
            QPushButton:disabled {{
                color: {MATRIX_GREEN_DARK};
                border: 2px solid {MATRIX_GRAY};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {MATRIX_GREEN_DARK};
                height: 8px;
                background: {MATRIX_BLACK};
            }}
            QSlider::handle:horizontal {{
                background: {MATRIX_GREEN};
                border: 1px solid {MATRIX_GREEN};
                width: 18px;
                margin: -5px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background: {MATRIX_GREEN_GLOW};
            }}
        """)
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_label = QLabel("[ MP4 ZOOM VIEWER - MATRIX INTERFACE ]")
        header_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-size: 16px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Credit
        credit_label = QLabel("Created by Dr. Andy Kong")
        credit_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-size: 12px; font-weight: bold;")
        credit_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(credit_label)
        
        # Main player display (full width now, no side-by-side)
        main_video_container = QVBoxLayout()
        player_label = QLabel("[ MAIN PLAYER - CLICK TO PAN ZOOM ]")
        player_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-weight: bold;")
        main_video_container.addWidget(player_label)
        
        self.main_display = VideoDisplayWidget("Main Player", clickable=True, matrix_theme=True)
        self.main_display.clicked.connect(self._on_main_display_clicked)
        main_video_container.addWidget(self.main_display)
        
        main_layout.addLayout(main_video_container)
        
        # Control panel
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)
        
        # File controls
        file_controls = QHBoxLayout()
        self.load_button = QPushButton("[ LOAD VIDEO ]")
        self.load_button.clicked.connect(self._on_load_video)
        file_controls.addWidget(self.load_button)
        
        self.video_info_label = QLabel("NO VIDEO LOADED")
        self.video_info_label.setStyleSheet(f"color: {MATRIX_GREEN_DARK};")
        file_controls.addWidget(self.video_info_label)
        file_controls.addStretch()
        controls_layout.addLayout(file_controls)
        
        # Playback controls
        playback_controls = QHBoxLayout()
        playback_label = QLabel("PLAYBACK:")
        playback_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-weight: bold;")
        playback_controls.addWidget(playback_label)
        
        self.play_button = QPushButton("[ PLAY ]")
        self.play_button.clicked.connect(self._on_play)
        self.play_button.setEnabled(False)
        playback_controls.addWidget(self.play_button)
        
        self.pause_button = QPushButton("[ PAUSE ]")
        self.pause_button.clicked.connect(self._on_pause)
        self.pause_button.setEnabled(False)
        playback_controls.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("[ STOP ]")
        self.stop_button.clicked.connect(self._on_stop)
        self.stop_button.setEnabled(False)
        playback_controls.addWidget(self.stop_button)
        
        self.backward_button = QPushButton("[ BACKWARD ]")
        self.backward_button.clicked.connect(self._on_backward)
        self.backward_button.setEnabled(False)
        playback_controls.addWidget(self.backward_button)
        
        self.forward_button = QPushButton("[ FORWARD ]")
        self.forward_button.clicked.connect(self._on_forward)
        self.forward_button.setEnabled(False)
        playback_controls.addWidget(self.forward_button)
        
        playback_controls.addStretch()
        controls_layout.addLayout(playback_controls)
        
        # Zoom controls
        zoom_controls = QHBoxLayout()
        zoom_label = QLabel("ZOOM LEVEL:")
        zoom_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-weight: bold;")
        zoom_controls.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(15)  # 1.5x * 10
        self.zoom_slider.setMaximum(200)  # 20.0x * 10
        self.zoom_slider.setValue(15)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(20)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        zoom_controls.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("1.5x")
        self.zoom_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-weight: bold;")
        zoom_controls.addWidget(self.zoom_label)
        
        self.zoom_toggle_button = QPushButton("[ ACTIVATE ZOOM WINDOW ]")
        self.zoom_toggle_button.setCheckable(True)
        self.zoom_toggle_button.clicked.connect(self._on_zoom_toggle)
        zoom_controls.addWidget(self.zoom_toggle_button)
        
        controls_layout.addLayout(zoom_controls)
        
        # Template matching controls
        template_controls = QHBoxLayout()
        template_label = QLabel("TEMPLATE TRACKING:")
        template_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-weight: bold;")
        template_controls.addWidget(template_label)
        
        self.capture_template_button = QPushButton("[ CAPTURE TEMPLATE ]")
        self.capture_template_button.clicked.connect(self._on_capture_template)
        self.capture_template_button.setEnabled(False)
        template_controls.addWidget(self.capture_template_button)
        
        self.track_template_button = QPushButton("[ START TRACKING ]")
        self.track_template_button.setCheckable(True)
        self.track_template_button.clicked.connect(self._on_track_template_toggle)
        self.track_template_button.setEnabled(False)
        template_controls.addWidget(self.track_template_button)
        
        self.tracking_status_label = QLabel("NO TEMPLATE")
        self.tracking_status_label.setStyleSheet(f"color: {MATRIX_GREEN_DARK}; font-size: 10px;")
        template_controls.addWidget(self.tracking_status_label)
        
        template_controls.addStretch()
        controls_layout.addLayout(template_controls)
        
        # Status bar
        status_container = QHBoxLayout()
        status_led = QLabel("●")
        status_led.setStyleSheet(f"color: {MATRIX_GREEN_GLOW}; font-size: 16px;")
        status_container.addWidget(status_led)
        
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-weight: bold;")
        status_container.addWidget(self.status_label)
        status_container.addStretch()
        
        controls_layout.addLayout(status_container)
        
        main_layout.addLayout(controls_layout)
    
    def _load_video(self, file_path: str):
        """Load a video file."""
        try:
            metadata = self.video_player.load_video(file_path)
            
            # Read and display the first frame
            first_frame = self.video_player.get_current_frame()
            if first_frame is None:
                # Manually read the first frame if not available
                ret, frame_data = self.video_player._capture.read()
                if ret:
                    from src.models import Frame
                    first_frame = Frame(
                        data=frame_data,
                        width=metadata.width,
                        height=metadata.height,
                        timestamp=0.0,
                        frame_number=0
                    )
                    self.frame_buffer.update_frame(first_frame, 0.0)
                    self.current_frame = first_frame
                    # Reset to beginning
                    self.video_player._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Update UI
            self.video_info_label.setText(
                f"{Path(file_path).name} | "
                f"{metadata.width}x{metadata.height} | "
                f"{metadata.fps:.1f} FPS | "
                f"{metadata.duration:.1f}s"
            )
            self.video_info_label.setStyleSheet(f"color: {MATRIX_GREEN};")
            
            # Enable controls
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            # Frame navigation buttons start disabled (only enabled when paused)
            self.backward_button.setEnabled(False)
            self.forward_button.setEnabled(False)
            
            # Initialize zoom engine with frame dimensions
            self.zoom_engine.set_frame_dimensions(metadata.width, metadata.height)
            self.zoom_engine.set_tracking_position(metadata.width // 2, metadata.height // 2)
            
            self.status_label.setText(f"VIDEO LOADED: {Path(file_path).name}")
            
        except Exception as e:
            QMessageBox.critical(self, "ERROR LOADING VIDEO", str(e))
            self.status_label.setText(f"ERROR: {str(e)}")
    
    def _on_load_video(self):
        """Handle load video button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "SELECT VIDEO FILE",
            "",
            "Video Files (*.mp4 *.avi *.mov);;All Files (*.*)"
        )
        
        if file_path:
            self._load_video(file_path)
    
    def _on_play(self):
        """Handle play button click."""
        try:
            self.video_player.play()
            self.status_label.setText("PLAYING")
            # Disable frame navigation buttons while playing
            self.backward_button.setEnabled(False)
            self.forward_button.setEnabled(False)
        except Exception as e:
            QMessageBox.warning(self, "PLAYBACK ERROR", str(e))
    
    def _on_pause(self):
        """Handle pause button click."""
        self.video_player.pause()
        self.status_label.setText("PAUSED")
        # Enable frame navigation buttons when paused
        self.backward_button.setEnabled(True)
        self.forward_button.setEnabled(True)
    
    def _on_stop(self):
        """Handle stop button click."""
        self.video_player.stop()
        self.status_label.setText("STOPPED")
        # Disable frame navigation buttons when stopped
        self.backward_button.setEnabled(False)
        self.forward_button.setEnabled(False)
    
    def _on_backward(self):
        """Handle backward button click - step one frame backward."""
        try:
            # Get current video metadata
            metadata = self.video_player.get_video_metadata()
            if metadata is None:
                return
            
            # Get current frame from the video capture
            current_frame_number = self.video_player._capture.get(cv2.CAP_PROP_POS_FRAMES)
            
            # Calculate previous frame number
            previous_frame = max(0, int(current_frame_number) - 2)  # -2 because we need to go back before current
            
            # Seek to previous frame
            self.video_player._capture.set(cv2.CAP_PROP_POS_FRAMES, previous_frame)
            
            # Read the frame
            ret, frame_data = self.video_player._capture.read()
            if ret:
                # Create Frame object
                frame_number = int(self.video_player._capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                timestamp = frame_number / metadata.fps
                height, width = frame_data.shape[:2]
                
                from src.models import Frame
                frame = Frame(
                    data=frame_data,
                    width=width,
                    height=height,
                    timestamp=timestamp,
                    frame_number=frame_number
                )
                
                # Update frame buffer
                self.frame_buffer.update_frame(frame, timestamp)
                self.status_label.setText(f"FRAME: {frame_number} / {metadata.total_frames}")
            
        except Exception as e:
            QMessageBox.warning(self, "BACKWARD ERROR", str(e))
    
    def _on_forward(self):
        """Handle forward button click - step one frame forward."""
        try:
            # Get current video metadata
            metadata = self.video_player.get_video_metadata()
            if metadata is None:
                return
            
            # Read the next frame
            ret, frame_data = self.video_player._capture.read()
            if ret:
                # Create Frame object
                frame_number = int(self.video_player._capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                timestamp = frame_number / metadata.fps
                height, width = frame_data.shape[:2]
                
                from src.models import Frame
                frame = Frame(
                    data=frame_data,
                    width=width,
                    height=height,
                    timestamp=timestamp,
                    frame_number=frame_number
                )
                
                # Update frame buffer
                self.frame_buffer.update_frame(frame, timestamp)
                self.status_label.setText(f"FRAME: {frame_number} / {metadata.total_frames}")
            else:
                self.status_label.setText("END OF VIDEO")
            
        except Exception as e:
            QMessageBox.warning(self, "FORWARD ERROR", str(e))
    
    def _on_zoom_changed(self, value):
        """Handle zoom slider change."""
        zoom_level = value / 10.0
        self.zoom_engine.set_zoom_level(zoom_level)
        self.zoom_label.setText(f"{zoom_level:.1f}x")
        
        # Update floating window if active
        if self.floating_zoom_window and self.zoom_window_active:
            self.floating_zoom_window.update_zoom_level(zoom_level)
    
    def _on_zoom_toggle(self, checked):
        """Handle zoom window toggle - show/hide floating window."""
        self.zoom_window_active = checked
        
        if checked:
            # Create and show floating zoom window
            if self.floating_zoom_window is None:
                self.floating_zoom_window = FloatingZoomWindow(self)
            
            self.floating_zoom_window.show()
            self.floating_zoom_window.update_zoom_level(self.zoom_engine.get_zoom_level())
            
            self.zoom_toggle_button.setText("[ DEACTIVATE ZOOM WINDOW ]")
            self.status_label.setText("ZOOM WINDOW ACTIVATED - CLICK MAIN PLAYER TO PAN")
            
            # Enable template capture when zoom window is active
            self.capture_template_button.setEnabled(True)
        else:
            # Hide floating zoom window
            if self.floating_zoom_window:
                self.floating_zoom_window.hide()
            
            self.zoom_toggle_button.setText("[ ACTIVATE ZOOM WINDOW ]")
            self.status_label.setText("ZOOM WINDOW DEACTIVATED")
            
            # Disable template controls when zoom window is inactive
            self.capture_template_button.setEnabled(False)
            if self.template_tracking_active:
                self._on_track_template_toggle(False)
                self.track_template_button.setChecked(False)
    
    def _on_capture_template(self):
        """Capture the current zoom window content as a template for tracking."""
        if not self.zoom_window_active or self.current_frame is None:
            QMessageBox.warning(
                self,
                "CANNOT CAPTURE TEMPLATE",
                "Zoom window must be active and video must be loaded."
            )
            return
        
        try:
            # Get the current ROI from zoom engine
            roi = self.zoom_engine.get_roi_bounds()
            
            # Extract the ROI from current frame
            roi_data = self.current_frame.data[
                roi.y:roi.y + roi.height,
                roi.x:roi.x + roi.width
            ]
            
            # Take center 200x200 pixels as template (or smaller if ROI is smaller)
            template_size = 200
            roi_center_x = roi.width // 2
            roi_center_y = roi.height // 2
            
            # Calculate template bounds within the ROI
            half_template = template_size // 2
            template_x1 = max(0, roi_center_x - half_template)
            template_y1 = max(0, roi_center_y - half_template)
            template_x2 = min(roi.width, roi_center_x + half_template)
            template_y2 = min(roi.height, roi_center_y + half_template)
            
            # Extract template from center of ROI
            template_data = roi_data[template_y1:template_y2, template_x1:template_x2]
            
            # Get actual template dimensions
            template_height, template_width = template_data.shape[:2]
            
            # Create a Frame object for the template with all required arguments
            from src.models import Frame
            template_frame = Frame(
                data=template_data,
                width=template_width,
                height=template_height,
                timestamp=self.current_frame.timestamp,
                frame_number=self.current_frame.frame_number
            )
            
            # Get the center point of the ROI (tracking position in full frame coordinates)
            center_point = self.zoom_engine.get_tracking_position()
            
            # Set the template in the template matcher
            self.template_matcher.set_template(template_frame, center_point)
            
            self.template_set = True
            self.track_template_button.setEnabled(True)
            self.tracking_status_label.setText(f"TEMPLATE CAPTURED ({template_width}x{template_height})")
            self.tracking_status_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-size: 10px;")
            self.status_label.setText(f"TEMPLATE CAPTURED AT ({center_point.x}, {center_point.y})")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "ERROR CAPTURING TEMPLATE",
                f"Failed to capture template: {str(e)}"
            )
            self.status_label.setText(f"ERROR: {str(e)}")
    
    def _on_track_template_toggle(self, checked):
        """Toggle template tracking on/off."""
        if not self.template_set:
            QMessageBox.warning(
                self,
                "NO TEMPLATE",
                "Please capture a template first using the CAPTURE TEMPLATE button."
            )
            self.track_template_button.setChecked(False)
            return
        
        self.template_tracking_active = checked
        
        if checked:
            self.track_template_button.setText("[ STOP TRACKING ]")
            self.tracking_status_label.setText("TRACKING ACTIVE")
            self.tracking_status_label.setStyleSheet(f"color: {MATRIX_GREEN_GLOW}; font-size: 10px;")
            self.status_label.setText("TEMPLATE TRACKING STARTED")
        else:
            self.track_template_button.setText("[ START TRACKING ]")
            self.tracking_status_label.setText("TRACKING STOPPED")
            self.tracking_status_label.setStyleSheet(f"color: {MATRIX_GREEN}; font-size: 10px;")
            self.status_label.setText("TEMPLATE TRACKING STOPPED")
    
    def _on_main_display_clicked(self, video_x, video_y):
        """Handle click on main display - update zoom tracking position."""
        # Update zoom engine tracking position
        self.zoom_engine.set_tracking_position(video_x, video_y)
        
        # Update floating window position display if active
        if self.floating_zoom_window and self.zoom_window_active:
            self.floating_zoom_window.update_position(video_x, video_y)
        
        # Update status to show the clicked position
        self.status_label.setText(f"ZOOM CENTERED AT ({video_x}, {video_y})")
    
    def _update_display(self):
        """Update video displays (called by timer)."""
        # Get current frame from buffer
        frame, timestamp = self.frame_buffer.get_current_frame()
        
        if frame is None:
            return
        
        self.current_frame = frame
        
        # Update main display
        self.main_display.display_frame(frame.data)
        
        # Perform template tracking if active
        if self.template_tracking_active and self.template_set:
            try:
                match_result = self.template_matcher.match_template(frame)
                
                if match_result.found and match_result.location:
                    # Update zoom tracking position to follow the matched template
                    self.zoom_engine.set_tracking_position(
                        match_result.location.x,
                        match_result.location.y
                    )
                    
                    # Update floating window position display
                    if self.floating_zoom_window:
                        self.floating_zoom_window.update_position(
                            match_result.location.x,
                            match_result.location.y
                        )
                    
                    # Update tracking status
                    self.tracking_status_label.setText(
                        f"TRACKING: {match_result.confidence:.2f}"
                    )
                    self.tracking_status_label.setStyleSheet(
                        f"color: {MATRIX_GREEN_GLOW}; font-size: 10px;"
                    )
                else:
                    # Tracking lost or low confidence - maintain last position
                    if not self.template_matcher.is_tracking_active():
                        # Tracking lost after too many failures
                        self.tracking_status_label.setText("TRACKING LOST")
                        self.tracking_status_label.setStyleSheet(
                            f"color: #FF4444; font-size: 10px;"
                        )
                    else:
                        # Low confidence but still trying
                        self.tracking_status_label.setText(
                            f"LOW CONFIDENCE: {match_result.confidence:.2f}"
                        )
                        self.tracking_status_label.setStyleSheet(
                            f"color: #FFAA00; font-size: 10px;"
                        )
                        
            except Exception as e:
                # Template matching error - display but don't crash
                self.tracking_status_label.setText(f"ERROR: {str(e)[:20]}")
                self.tracking_status_label.setStyleSheet(
                    f"color: #FF4444; font-size: 10px;"
                )
        
        # Update floating zoom window if active
        if self.zoom_window_active and self.floating_zoom_window:
            zoomed_frame_data = self.zoom_engine.get_zoomed_frame(frame)
            self.floating_zoom_window.update_frame(zoomed_frame_data)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.update_timer.stop()
        self.video_player.stop()
        self.video_player.release()
        
        # Close floating zoom window if it exists
        if self.floating_zoom_window:
            self.floating_zoom_window.close()
        
        event.accept()


def main():
    """Main application entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="MP4 Zoom Viewer - Video player with zoom and tracking capabilities"
    )
    parser.add_argument(
        "video_path",
        nargs="?",
        default=r"video\nasa_solar_20260205_to_20260207_4096_0304.mp4",
        help="Path to the video file to load (optional)"
    )
    args = parser.parse_args()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MP4 Zoom Viewer")
    
    # Create and show main window maximized
    window = MainPlayerWindow(video_path=args.video_path)
    window.showMaximized()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
