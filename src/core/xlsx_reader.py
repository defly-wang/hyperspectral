import os
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import openpyxl


@dataclass
class XLSXMetadata:
    filename: str = ""
    sheet_name: str = ""


@dataclass
class SpectrumData:
    wavelengths: np.ndarray
    intensities: np.ndarray
    metadata: XLSXMetadata


def parse_xlsx_file(filepath: str, wavelength_col: int = 0, intensity_col: int = 4) -> SpectrumData:
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    
    wavelengths = []
    intensities = []
    
    for row in ws.iter_rows(min_row=1, values_only=True):
        if row is None:
            continue
        
        try:
            wl = float(row[wavelength_col])
            intensity = float(row[intensity_col])
            if wl is not None and intensity is not None and not (np.isnan(wl) or np.isnan(intensity)):
                wavelengths.append(wl)
                intensities.append(intensity)
        except (ValueError, TypeError, IndexError):
            continue
    
    wb.close()
    
    metadata = XLSXMetadata(
        filename=os.path.basename(filepath),
        sheet_name=ws.title
    )
    
    return SpectrumData(
        wavelengths=np.array(wavelengths),
        intensities=np.array(intensities),
        metadata=metadata
    )


def load_xlsx_files(folder_path: str) -> List[Tuple[str, SpectrumData]]:
    results = []
    if not os.path.isdir(folder_path):
        return results
    
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(('.xlsx', '.xls')):
            filepath = os.path.join(folder_path, filename)
            try:
                data = parse_xlsx_file(filepath)
                results.append((filename, data))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return results
