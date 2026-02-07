# MP4 Zoom Viewer (Solar mp4 viewer)
<img width="1269" height="764" alt="mp4_main" src="https://github.com/user-attachments/assets/35a40d17-f9e3-439d-88eb-fb2e0105ff05" />


A professional video player application with advanced zoom and tracking capabilities using computer vision. Features a Matrix-inspired interface with floating zoom window and automatic template tracking.

**Created by Dr. Andy Kong**

## Features

- **High-Resolution Video Playback**: Supports MP4 videos with standard controls (play, pause, stop)
- **Frame-by-Frame Navigation**: Step forward/backward one frame at a time when paused
- **Floating Zoom Window**: Separate popup window with adjustable magnification (1.5x - 20x)
- **Interactive Panning**: Click anywhere on the main player to center the zoom window
- **Template-Based Tracking**: Automatic object tracking using OpenCV template matching
- **Real-Time Synchronization**: Zoom window updates in real-time with main player
- **Matrix Theme**: High-tech green-on-black interface inspired by The Matrix
- **Native Resolution**: Displays original video pixels without quality loss

## Screenshots

The application features:
- Main player window with maximized display
- Floating zoom window that stays on top
- Matrix-style green interface with monospace fonts
- Real-time tracking status indicators
- Frame-by-frame navigation controls

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows, macOS, or Linux

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mp4-zoom-viewer.git
cd mp4-zoom-viewer
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the application:
```bash
python main.py
```

Or load a video directly:
```bash
python main.py path/to/your/video.mp4
```

### Quick Start Guide

1. **Load Video**: Click `[ LOAD VIDEO ]` and select your MP4 file
2. **Play Video**: Click `[ PLAY ]` to start playback
3. **Activate Zoom**: Click `[ ACTIVATE ZOOM WINDOW ]` to open the floating zoom window
4. **Pan Zoom**: Click anywhere on the main player to center the zoom window
5. **Adjust Zoom**: Use the zoom slider to change magnification (1.5x - 20x)

### Frame-by-Frame Navigation

1. Click `[ PAUSE ]` to pause the video
2. Use `[ BACKWARD ]` to step one frame back
3. Use `[ FORWARD ]` to step one frame forward

### Template Tracking

1. Activate the zoom window and position it over the object you want to track
2. Click `[ CAPTURE TEMPLATE ]` to capture the current zoom view (center 200x200 pixels)
3. Click `[ START TRACKING ]` to begin automatic tracking
4. The zoom window will automatically follow the pattern in the video
5. Click `[ STOP TRACKING ]` to disable tracking

**Tracking Status Indicators:**
- **Green**: Successfully tracking with confidence score
- **Orange**: Low confidence warning
- **Red**: Tracking lost (maintains last known position)

## Technical Details

### Architecture

- **VideoPlayerEngine**: Handles video loading, playback, and frame delivery using OpenCV
- **ZoomEngine**: Manages zoom level, ROI calculation, and frame extraction
- **TemplateMatchingEngine**: Performs OpenCV template matching for object tracking
- **FrameBuffer**: Thread-safe buffer for frame synchronization

### Template Matching

- Algorithm: OpenCV normalized cross-correlation (TM_CCOEFF_NORMED)
- Confidence threshold: 0.6 (60%)
- Template size: 200x200 pixels (center of zoom window)
- Tracking loss: After 5 consecutive failed matches

### Performance

- Real-time playback at video frame rate
- ~30 fps UI refresh rate
- Native resolution display (no unnecessary scaling)
- Minimal performance impact from template matching

## Project Structure

```
mp4-zoom-viewer/
├── src/                          # Source code
│   ├── engines/                  # Core engines
│   │   ├── video_player_engine.py
│   │   ├── zoom_engine.py
│   │   └── template_matching_engine.py
│   ├── models/                   # Data models
│   │   └── data_models.py
│   ├── frame_buffer.py          # Thread-safe frame buffer
│   └── __init__.py
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   └── property/                # Property-based tests
├── .kiro/                       # Kiro AI specifications
│   └── specs/mp4-zoom-viewer/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pytest.ini                   # Test configuration
└── README.md                    # This file
```

## Requirements

- Python 3.10+
- OpenCV 4.8+
- PyQt5 5.15+
- NumPy 1.24+
- pytest 7.4+ (for testing)
- hypothesis 6.82+ (for property-based testing)

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test categories:
```bash
pytest -m unit          # Unit tests only
pytest -m property      # Property-based tests only
```

## Tips for Best Results

1. **Choose Distinctive Patterns**: Select regions with unique features for better tracking
2. **Appropriate Zoom Level**: Use 2x-5x zoom for most tracking scenarios
3. **Stable Lighting**: Tracking works best when lighting conditions are consistent
4. **Template Size**: The 200x200 pixel template is automatically captured from the center
5. **Re-capture When Needed**: If tracking degrades, pause and capture a new template

## Known Limitations

- Template matching works best with consistent lighting and minimal occlusion
- Very fast-moving objects may cause tracking loss
- Template size is fixed at 200x200 pixels
- Supports MP4 format (other formats may work but are not officially supported)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Author

**Dr. Andy Kong**

## Acknowledgments

- Built with OpenCV for computer vision capabilities
- PyQt5 for the graphical user interface
- Inspired by The Matrix movie aesthetic

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This application was developed with assistance from Kiro AI for rapid prototyping and implementation.

