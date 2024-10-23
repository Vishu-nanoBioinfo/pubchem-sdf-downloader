# pubchem-sdf-downloader
Python script to fetch molecular data and SDF files from PubChem.
# PubChem SDF Downloader

This project is a Python script that fetches molecular properties and downloads SDF (Structure Data File) files for compounds from PubChem using their Compound ID (CID). It supports downloading both 2D and 3D SDF files, logs molecules that cannot be found, and tracks download progress for large batches of compounds.

## Features

- Fetches molecular properties such as:
  - Molecular Weight (MW)
  - XLogP
  - Hydrogen Bond Donor Count (nHD)
  - Hydrogen Bond Acceptor Count (nHA)
  - Topological Polar Surface Area (TPSA)
- Downloads 3D SDF files. If 3D is not available, falls back to 2D SDF.
- Logs compounds that are not found.
- Tracks download progress to resume later, avoiding redundant downloads.

## Requirements

The script uses the following Python libraries:

- `requests`: To send HTTP requests to PubChem API.
- `pandas`: To manage and save molecular data as CSV files.

You can install the required dependencies using the following command:

```bash
pip install requests pandas
