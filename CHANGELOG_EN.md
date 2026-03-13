# Changelog

## [Unreleased]

### New Features
- **Multi-language Support**
  - Supports Simplified Chinese and English
  - Language menu for easy switching
  - Real-time UI update when switching language

- **Data Cleaning Module**
  - Invalid data detection: NaN, Inf, negative values, out of range, length mismatch, low variance
  - Anomaly detection: IQR and Z-Score methods
  - Duplicate detection: Spectral similarity based on correlation coefficient
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
- Wavelength filter changed from 500nm to 400nm
- File list sorted by filename

### UI Improvements
- Tabs: Preview / Data Cleaning / Data Split / Model Training / Recognition
- New Model menu: Load model, Recognition
- New Language menu: 中文/English

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
