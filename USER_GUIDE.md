# MP4 Zoom Viewer - User Guide

**Created by Dr. Andy Kong**

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Playback Controls](#basic-playback-controls)
3. [Zoom Window](#zoom-window)
4. [Frame-by-Frame Navigation](#frame-by-frame-navigation)
5. [Template Tracking](#template-tracking)
6. [Tips and Best Practices](#tips-and-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Launching the Application

Run the application from the command line:

```bash
python main.py
```

Or load a video directly:

```bash
python main.py path/to/your/video.mp4
```

### Loading a Video

1. Click **[ LOAD VIDEO ]** button
2. Select your MP4 video file from the file dialog
3. The video information will display (filename, resolution, fps, duration)

---

## Basic Playback Controls

### Play/Pause/Stop

- **[ PLAY ]**: Start or resume video playback
- **[ PAUSE ]**: Pause the video at the current frame
- **[ STOP ]**: Stop playback and return to the beginning

### Status Display

The status bar at the bottom shows:
- Current playback state (PLAYING, PAUSED, STOPPED)
- Current frame number when using frame navigation
- Zoom position coordinates
- Tracking status when template tracking is active

---

## Zoom Window

### Activating the Zoom Window

1. Click **[ ACTIVATE ZOOM WINDOW ]** button
2. A floating window appears showing a magnified view
3. The zoom window stays on top of other windows

### Adjusting Zoom Level

- Use the **ZOOM LEVEL** slider to adjust magnification
- Range: 1.5x to 20.0x
- Current zoom level is displayed next to the slider

### Panning the Zoom Window

- Click anywhere on the main player video
- The zoom window centers on the clicked location
- Position coordinates are displayed in the zoom window

### Deactivating the Zoom Window

- Click **[ DEACTIVATE ZOOM WINDOW ]** to close the floating window
- Main player continues normal playback

---

## Frame-by-Frame Navigation

### Using Frame Navigation

1. Click **[ PAUSE ]** to pause the video
2. Use **[ BACKWARD ]** to step one frame backward
3. Use **[ FORWARD ]** to step one frame forward
4. Status bar shows current frame number

**Note**: Frame navigation buttons are only enabled when the video is paused.

### Use Cases

- Examining specific frames in detail
- Finding the perfect frame for template capture
- Analyzing frame-by-frame motion
- Precise positioning for tracking setup

---

## Template Tracking

### Overview

Template tracking allows the zoom window to automatically follow a specific pattern or object in the video.

### Step-by-Step Guide

#### 1. Position the Zoom Window

- Activate the zoom window
- Click on the main player to center the zoom on your target object
- Adjust zoom level for optimal view (2x-5x recommended)

#### 2. Capture Template

- Click **[ CAPTURE TEMPLATE ]** button
- The system captures the center 200x200 pixels of the zoom window
- Status shows "TEMPLATE CAPTURED (WxH)"

#### 3. Start Tracking

- Click **[ START TRACKING ]** button
- The zoom window now automatically follows the pattern
- Tracking status displays confidence score

#### 4. Monitor Tracking

**Tracking Status Indicators:**

- **Green "TRACKING: 0.XX"**: Successfully tracking (confidence score)
- **Orange "LOW CONFIDENCE: 0.XX"**: Tracking but with reduced confidence
- **Red "TRACKING LOST"**: Pattern not found for 5+ consecutive frames

#### 5. Stop Tracking

- Click **[ STOP TRACKING ]** to disable automatic tracking
- Resume manual panning by clicking on the main player

### Template Tracking Features

**Automatic Position Updates**
- Zoom window centers on matched pattern in real-time
- Updates at video frame rate

**Tracking Loss Handling**
- Maintains last known position when pattern not found
- Shows "TRACKING LOST" after 5 consecutive failures
- Zoom window stays at last successful match location

**Template Re-capture**
- Capture new template at any time
- New template replaces previous one
- Useful when object appearance changes

### Technical Details

- **Algorithm**: OpenCV normalized cross-correlation (TM_CCOEFF_NORMED)
- **Confidence Threshold**: 0.6 (60%)
- **Template Size**: 200x200 pixels (center of zoom window)
- **Tracking Loss**: After 5 consecutive failed matches
- **Performance**: Real-time at video frame rate

---

## Tips and Best Practices

### For Best Tracking Results

1. **Choose Distinctive Patterns**
   - Select regions with unique features
   - Avoid uniform or repetitive patterns
   - High contrast areas work best

2. **Optimal Zoom Level**
   - Use 2x-5x zoom for most scenarios
   - Higher zoom for small objects
   - Lower zoom for larger objects

3. **Lighting Conditions**
   - Tracking works best with consistent lighting
   - Avoid scenes with dramatic lighting changes
   - Re-capture template if lighting changes significantly

4. **Template Size**
   - 200x200 pixel template is automatically captured
   - Ensure the object fits within this size
   - Larger objects may require lower zoom levels

5. **Re-capture Strategy**
   - Pause video when tracking degrades
   - Position zoom on current object location
   - Capture new template with updated appearance

### For High-Resolution Videos

- The application preserves native video resolution
- 4096x4096 videos display at full quality
- Zoom window shows original pixels without upscaling
- No quality loss from unnecessary scaling operations

### Performance Optimization

- Close other applications for smoother playback
- Use SSD storage for large video files
- Reduce zoom level if performance is slow
- Disable tracking when not needed

---

## Troubleshooting

### Video Won't Load

**Problem**: Error message when loading video

**Solutions**:
- Ensure file is a valid MP4 format
- Check file is not corrupted
- Verify file path is correct
- Try re-encoding the video with standard codecs

### Zoom Window is Blurry

**Problem**: Zoomed image appears blurry

**Solutions**:
- This should not occur - zoom uses native resolution
- Check video source quality
- Try different zoom levels
- Ensure video is high resolution

### Cannot Capture Template

**Problem**: Error when clicking CAPTURE TEMPLATE

**Solutions**:
- Ensure zoom window is activated
- Ensure video is loaded
- Verify video is playing or paused (not stopped)
- Check zoom window is positioned on valid video area

### Tracking Not Working

**Problem**: Template captured but tracking doesn't follow object

**Solutions**:
- Verify tracking is enabled (button shows "[ STOP TRACKING ]")
- Check tracking status for confidence scores
- Try capturing a more distinctive template
- Ensure object is visible in current frame
- Re-capture template if object appearance changed

### Low Confidence Warnings

**Problem**: Tracking shows low confidence frequently

**Solutions**:
- Object may be partially occluded
- Lighting conditions may have changed
- Object appearance may have changed
- Try re-capturing template with current frame
- Select a more distinctive pattern

### Tracking Lost

**Problem**: Status shows "TRACKING LOST"

**Solutions**:
- Object may have moved out of frame
- Object appearance changed significantly
- Lighting changed dramatically
- Pause video and re-capture template
- Position zoom manually and capture new template

### Frame Navigation Not Working

**Problem**: BACKWARD/FORWARD buttons are disabled

**Solutions**:
- Buttons only work when video is paused
- Click **[ PAUSE ]** first
- Ensure video is loaded
- Check video is not at beginning (BACKWARD) or end (FORWARD)

---

## Example Workflows

### Workflow 1: Basic Zoom Viewing

```
1. Load video
2. Click [ PLAY ]
3. Click [ ACTIVATE ZOOM WINDOW ]
4. Adjust zoom slider to 3.0x
5. Click on areas of interest in main player
6. Zoom window follows your clicks
```

### Workflow 2: Frame-by-Frame Analysis

```
1. Load video
2. Click [ PLAY ] to find interesting section
3. Click [ PAUSE ] when you find it
4. Use [ BACKWARD ] and [ FORWARD ] to examine frames
5. Activate zoom window for detailed inspection
6. Click on specific areas to examine closely
```

### Workflow 3: Object Tracking

```
1. Load video (e.g., solar observation video)
2. Click [ PLAY ]
3. Click [ ACTIVATE ZOOM WINDOW ]
4. Set zoom to 3.0x
5. Click on object to track (e.g., solar flare)
6. Click [ CAPTURE TEMPLATE ]
7. Click [ START TRACKING ]
8. Watch zoom window automatically follow the object
9. If tracking is lost, pause and re-capture template
```

### Workflow 4: High-Resolution Detail Examination

```
1. Load high-resolution video (e.g., 4096x4096)
2. Click [ ACTIVATE ZOOM WINDOW ]
3. Set zoom to 10.0x or higher
4. Click [ PAUSE ]
5. Use [ FORWARD ] to advance frame by frame
6. Click on different areas to examine details
7. Native resolution ensures maximum quality
```

---

## Keyboard Shortcuts

Currently, all controls are accessed via buttons. Keyboard shortcuts are planned for future releases:

- **Space**: Play/Pause (planned)
- **Arrow Keys**: Frame navigation (planned)
- **+/-**: Zoom in/out (planned)

---

## Matrix Theme Interface

The application features a Matrix movie-inspired aesthetic:

- **Colors**: Green text on black background
- **Font**: Monospace (Courier New) for tech look
- **Status Indicators**: Glowing green LEDs
- **Floating Window**: Stays on top with Matrix styling
- **High-Tech Feel**: Terminal-style interface

---

## Additional Resources

- **README.md**: Installation and setup instructions
- **GitHub Repository**: Source code and issue tracking
- **Requirements Specification**: `.kiro/specs/mp4-zoom-viewer/requirements.md`
- **Design Document**: `.kiro/specs/mp4-zoom-viewer/design.md`

---

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing issues for solutions
- Provide video details and error messages when reporting bugs

---

**Created by Dr. Andy Kong**

*Developed with assistance from Kiro AI*
