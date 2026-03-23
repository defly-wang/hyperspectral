# Changelog

## [Unreleased]

### 2026-03-23

### New Features
- **USGS Spectral Library Support**
  - Preview module supports browsing USGS spectral library directly
  - Support category/sub-category filtering
  - Sub-category names displayed in bilingual format (Chinese/English)
  - Training module supports loading USGS spectral library directory directly as training data
  - Data cleaning module supports USGS .txt file validation and parsing
  - Recognition module supports USGS spectral file recognition

- **Wavelength Range Adjustment**
  - Minimum wavelength changed from 400nm to 350nm across all modules
  - USGS spectrum reading supports instrument-specific wavelength files (ASD/BECK/NIC4/AVIRIS)

### 2026-03-18

### New Features
- **Preview Module Pseudo-color Improvements**
  - Set subplot spacing to 0 for horizontal multi-image layout
  - Hide subplot borders for "fusion" effect
  - Click on image to display filename at top center

- **Recognition Module Improvements**
  - File list changed to table format (Filename, Recognition Result, Confidence)
  - Recognition results automatically filled into table after completion

### 2026-03-17

### New Features
- **Multi-language Support**
  - Supports Simplified Chinese and English
  - Language menu for easy switching
  - Real-time UI update when switching language

- **Data Cleaning Module**
  - Invalid data detection: NaN, Inf, negative values, out of range, length mismatch, low variance
  - Anomaly detection: IQR and Z-Score methods
  - Duplicate detection: Spectral similarity based on correlation coefficient
  - Outlier spectra detection: Detect anomalous spectra significantly different from overall trends
  - File format check: validation, header check, encoding detection
  - Invalid file check: read failure, empty data, no data after filter, insufficient points
  - Report export
  - Issue list click to preview spectrum

- **Data Split Module**
  - Two split modes: Train/Val/Test or Train/Test
  - Configurable ratios (percentage format, default 70%/15%/15%)
  - Progress bar display
  - Auto-clear old files before split (with confirmation)
  - Data shuffle with configurable random seed
  - Background thread execution to avoid UI freeze

- **Model Training Module Improvements**
  - Support loading pre-split data directories (train/val/test structure)
  - Automatic validation after training using validation set
  - Display validation accuracy and classification report

- **Recognition Module**
  - Load trained models for prediction
  - Batch recognition of multiple files
  - Display results with confidence

- **Application Name**
  - Renamed to "Hyperspectral Data Management System - HyperspectralDMS"

### Feature Improvements
- Wavelength filter changed from 500nm to 400nm, then to 350nm
- File list sorted by filename

### UI Improvements
- Tabs: Preview / Data Cleaning / Data Split / Model Training / Recognition
- New Data menu: Data Cleaning, Data Split
- New Model menu: Train Model, Load Model, Recognition
- New Language menu: 中文/English
- Refactored preview panel to separate PreviewPanel class
- Fixed max width for left panel in preview to prevent layout expansion
- Draggable legend for spectrum plot
- Spectrum curves support mouse click to select/deselect, selected curves highlighted in bold
- Pseudo-color images support multi-select display, horizontal layout with one image per column
- Data cleaning module spectrum preview uses SpectrumPlotWidget with shared curve selection
- Application icon

## [1.0.0] - 2026-03-11

### New Features
- **Data Viewing**
  - Support `.isf` format
  - Support `.xlsx/.xls` format
  - Spectrum curve visualization
  - Multi-file selection (Ctrl+multi, Shift+range)
  - Multiple spectrum comparison

- **Pseudo-color Image**
  - Convert spectral data to pseudo-color images

- **Data Preprocessing**
  - Smoothing: Savitzky-Golay, Moving Average
  - Normalization: Min-Max, Z-Score
  - Baseline Correction: AirPLS, Baseline Subtraction
  - Auto-filter below 500nm

- **Model Training**
  - Random Forest classifier
  - SVM classifier
  - Gradient Boosting classifier
  - Auto-load from directory (by subdirectory)
  - Accuracy display
  - Classification report (Precision, Recall, F1-Score)
  - Model save (.pkl)

### UI/UX Improvements
- Modern PyQt6 desktop interface
- Menu bar: File, View, Model, Help
- Tab switching: Preview / Model Training
- Status bar
- Keyboard shortcuts (Ctrl+O, Ctrl+T, Ctrl+Q)

### Project Initialization
- Project structure
- PyInstaller config
- requirements.txt
