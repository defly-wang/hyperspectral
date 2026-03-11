import re
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
import os


@dataclass
class ISFMetadata:
    date: str = ""
    time: str = ""
    nrof_specs: int = 2
    meas_number: int = 1
    meas_start_time: float = 10.0
    meas_interval: float = 1.0
    wavelength_start: float = 0.0
    wavelength_end: float = 0.0
    int_time: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    azimuth_angle: float = 0.0
    elevation_angle: float = 0.0
    temperature: float = 0.0
    humidity: float = 0.0
    data_number: int = 0


@dataclass
class SpectrumData:
    wavelengths: np.ndarray
    intensities: np.ndarray
    metadata: ISFMetadata


def parse_isf_file(filepath: str) -> SpectrumData:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    metadata = ISFMetadata()

    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
    time_match = re.search(r'(\d{2}:\d{2}:\d{2})', content)
    if date_match:
        metadata.date = date_match.group(1)
    if time_match:
        metadata.time = time_match.group(1)

    nrof_specs_match = re.search(r'NrofSpecs=(\d+)', content)
    if nrof_specs_match:
        metadata.nrof_specs = int(nrof_specs_match.group(1))

    meas_number_match = re.search(r'MeasNumber=(\d+)', content)
    if meas_number_match:
        metadata.meas_number = int(meas_number_match.group(1))

    meas_start_time_match = re.search(r'StartTime\[min\]=(\d+\.?\d*)', content)
    if meas_start_time_match:
        metadata.meas_start_time = float(meas_start_time_match.group(1))

    meas_interval_match = re.search(r'Interval\[s\]=(\d+\.?\d*)', content)
    if meas_interval_match:
        metadata.meas_interval = float(meas_interval_match.group(1))

    int_time_match = re.search(r'IntTime\[ms\]=(\d+\.?\d*)', content)
    if int_time_match:
        metadata.int_time = float(int_time_match.group(1))

    lat_match = re.search(r'Latitude=([-\d.]+)', content)
    if lat_match:
        metadata.latitude = float(lat_match.group(1))

    lon_match = re.search(r'Longitude=([-\d.]+)', content)
    if lon_match:
        metadata.longitude = float(lon_match.group(1))

    azimuth_match = re.search(r'AzimuthAngle\[.*?\]=([-\d.]+)', content)
    if azimuth_match:
        metadata.azimuth_angle = float(azimuth_match.group(1))

    elevation_match = re.search(r'ElevationAngle\[.*?\]=([-\d.]+)', content)
    if elevation_match:
        metadata.elevation_angle = float(elevation_match.group(1))

    temp_match = re.search(r'Temperature1\[.*?\]=([-\d.]+)', content)
    if temp_match:
        metadata.temperature = float(temp_match.group(1))

    humidity_match = re.search(r'Humidity1\[%\]=([-\d.]+)', content)
    if humidity_match:
        metadata.humidity = float(humidity_match.group(1))

    data_number_match = re.search(r'dataNumber=(\d+)', content)
    if data_number_match:
        metadata.data_number = int(data_number_match.group(1))

    lines = content.split('\n')
    in_spectrum_section = False
    wavelengths = []
    intensities = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('[Spectrum]'):
            in_spectrum_section = True
            continue
        
        if in_spectrum_section:
            if line.startswith('*') or line.startswith('=') or line.startswith('['):
                if not line.startswith('[Spectrum]'):
                    continue
            
            parts = line.split(';')
            if len(parts) >= 5:
                try:
                    wl = float(parts[0])
                    sample = float(parts[4])
                    wavelengths.append(wl)
                    intensities.append(sample)
                except (ValueError, IndexError):
                    continue

    wavelengths = np.array(wavelengths)
    intensities = np.array(intensities)

    if len(wavelengths) > 0:
        metadata.wavelength_start = wavelengths[0]
        metadata.wavelength_end = wavelengths[-1]

    return SpectrumData(wavelengths, intensities, metadata)


def load_isf_files(folder_path: str) -> List[Tuple[str, SpectrumData]]:
    results = []
    if not os.path.isdir(folder_path):
        return results
    
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith('.isf'):
            filepath = os.path.join(folder_path, filename)
            try:
                data = parse_isf_file(filepath)
                results.append((filename, data))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return results
