# Hyperspectral Data Management System - HyperspectralDMS

A PyQt6-based desktop application for hyperspectral data processing and visualization.

## Features

### Multi-language Support
- **Chinese/English**: Supports Simplified Chinese and English
- Language menu for easy switching

### Data Viewing
- **Multi-format Support**: Supports `.isf` and `.xlsx/.xls` hyperspectral data files
- **Spectrum Curve Display**: Visualize wavelength vs reflectance/transmittance
- **Multi-file Viewing**: Single or multiple file selection, multiple curves in one chart
- **Pseudo-color Image**: Convert spectral data to pseudo-color images
- **File Sorting**: File list sorted by filename

### Data Cleaning
- **Invalid Data Detection**: NaN, Inf, negative values, out of range, length mismatch, low variance
- **Anomaly Detection**: IQR and Z-Score methods with adjustable threshold
- **Duplicate Detection**: Spectral similarity detection based on correlation coefficient
- **Outlier Spectra Detection**: Detect anomalous spectra significantly different from overall trends
- **File Format Check**: Format validation, header check, encoding detection
- **Issue List Checkboxes**: Each row has a checkbox for batch selection
- **Report Export**: Export cleaning reports
- **Data Preview**: Click issue list to view spectrum curves

### Data Split
- **Train/Val/Test Split**: Support two split modes (Train/Val/Test or Train/Test)
- **Ratio Configuration**: Customizable train, validation, test ratios
- **Progress Display**: Progress bar during split
- **Auto-clear**: Automatically clear old files before split
- **Shuffle**: Support data shuffle with configurable random seed

### Data Preprocessing
- Smoothing (Savitzky-Golay / Moving Average)
- Normalization (Min-Max / Z-Score)
- Baseline Correction (AirPLS / Baseline Subtraction)
- Auto-filter wavelengths below 400nm

### Model Training
- Three ML models: Random Forest, SVM, Gradient Boosting
- Auto-load training data from directories (categorized by subdirectories)
- Training results with accuracy and classification report
- Model save/load functionality

### Recognition
- Load trained models for prediction
- Batch recognition of multiple files
- Display recognition results with confidence

## Requirements

- Python 3.8+
- PyQt6
- NumPy
- Matplotlib
- SciPy
- openpyxl
- scikit-learn
- joblib

## Installation

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Activate virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Building

```bash
./build.sh
```

The executable will be in `dist/HyperspectralDMS/`.

## Data Format

### ISF Files
- Wavelength column: `Wave[nm]`
- Data column: `Refl/Tran[%]`

### XLSX Files
- Wavelength column: First column (Wave[nm])
- Data column: Fifth column (Refl/Tran[%])

### Training Data Directory Structure
```
training_data/
├── category1/
│   ├── sample1.xlsx
│   └── sample2.xlsx
├── category2/
│   └── sample1.xlsx
└── category3/
    └── sample1.xlsx
```

## Usage

### Data Viewing
1. Click "Open Folder" to select data folder
2. Click to select files (Ctrl+multi-select / Shift+range-select)
3. Use preprocessing panel to adjust data
4. Switch between "Spectrum" and "Image" tabs

### Data Cleaning
1. Switch to "Data Cleaning" tab
2. Click "Select Folder..." to select data folder
3. Configure detection options
4. Click "Start Analysis"
5. Review issue list, click to preview spectrum
6. Export cleaning report

### Data Split
1. Switch to "Data Split" tab
2. Click "Select Folder" to select source data folder (with category subdirectories)
3. Click "Select Folder" to select output directory
4. Configure split type (Train/Val/Test or Train/Test)
5. Configure ratios for each dataset
6. Optionally enable shuffle and set random seed
7. Click "Start Split" to begin
8. View results after completion

### Model Training
1. Switch to "Model Training" tab
2. Click "Select..." to choose training data directory
3. Select model type and test set ratio
4. Click "Start Training"
5. Save model after training

### Recognition
1. Switch to "Recognition" tab
2. Click "Load Model..." to load trained model
3. Click "Select Files..." to choose files
4. Click "Start Recognition"
5. View results with confidence

## Project Structure

```
hyperspectral/
├── main.py                      # Entry point
├── requirements.txt              # Python dependencies
├── build.sh                     # Build script
├── build.bat                    # Windows build script
├── hyperspectral.spec           # PyInstaller config
└── src/
    ├── core/
    │   ├── isf_reader.py       # ISF file parser
    │   ├── xlsx_reader.py       # XLSX file parser
    │   ├── preprocessing.py     # Data preprocessing
│   ├── model_trainer.py    # ML models
│   ├── data_cleaner.py     # Data cleaning
│   ├── data_split.py       # Data split
│   └── i18n.py            # Internationalization
│   └── ui/
│       ├── main_window.py       # Main window
│       ├── file_browser.py      # File browser
│       ├── spectrum_plot.py     # Spectrum chart
│       ├── image_view.py        # Pseudo-color image
│       ├── preprocessing_panel.py  # Preprocessing panel
│       ├── training_panel.py    # Training panel
│       ├── recognition_panel.py # Recognition panel
│       ├── data_cleaning_panel.py # Data cleaning panel
│       └── data_split_panel.py  # Data split panel
```

## Keyboard Shortcuts

- `Ctrl+O`: Open folder
- `Ctrl+T`: Open model training panel
- `Ctrl+M`: Load model
- `Ctrl+R`: Open recognition panel
- `Ctrl+Q`: Exit

## License

MIT License
