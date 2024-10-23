import os
import requests
import pandas as pd
import time

# Create directories for 3D and 2D SDF files
os.makedirs('3dSDF', exist_ok=True)
os.makedirs('2dSDF', exist_ok=True)

# Create or open a log file for molecules not found
log_file_path = 'No_Molecule_Found.log'
with open(log_file_path, 'w') as log_file:
    log_file.write("Molecules Not Found\n")
    log_file.write("===================\n")

# Create a file to track progress
progress_file_path = 'Download_Progress.txt'
if not os.path.exists(progress_file_path):
    with open(progress_file_path, 'w') as progress_file:
        progress_file.write("Start_CID\n1\n")

# Function to fetch molecular features from PubChem by CID
def get_molecular_properties(cid):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularWeight,XLogP,HBondDonorCount,HBondAcceptorCount,TPSA/JSON"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            properties = response.json()['PropertyTable']['Properties'][0]
            return {
                'MW': properties.get('MolecularWeight', None),
                'LogP': properties.get('XLogP', None),
                'nHD': properties.get('HBondDonorCount', None),
                'nHA': properties.get('HBondAcceptorCount', None),
                'TPSA': properties.get('TPSA', None)
            }
        except (KeyError, IndexError):
            return None
    else:
        return None

# Function to download 3D SDF, fallback to 2D if 3D is not available
def download_sdf(cid):
    sdf_3d_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=3d"
    sdf_2d_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=2d"
    
    # Try downloading 3D SDF
    response = requests.get(sdf_3d_url)
    if response.status_code == 200:
        sdf_file_path = os.path.join('3dSDF', f"{cid}.sdf")
        with open(sdf_file_path, 'wb') as sdf_file:
            sdf_file.write(response.content)
        print(f"Downloaded 3D SDF for CID: {cid}")
    else:
        # Fallback to downloading 2D SDF
        response = requests.get(sdf_2d_url)
        if response.status_code == 200:
            sdf_file_path = os.path.join('2dSDF', f"{cid}.sdf")
            with open(sdf_file_path, 'wb') as sdf_file:
                sdf_file.write(response.content)
            print(f"Downloaded 2D SDF for CID: {cid}")
        else:
            # Log no molecule found
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"CID {cid} - No Molecule Found\n")
            print(f"No molecule found for CID: {cid}")

# Fetch data for compounds in batches, save to CSV, and download structures
def fetch_and_save_molecules(start_cid, molecules_per_day=10000):
    molecular_data = []
    current_cid = start_cid
    processed_molecules = 0
    
    while processed_molecules < molecules_per_day:
        print(f"Fetching molecular properties for CID: {current_cid}")
        properties = get_molecular_properties(current_cid)
        
        if properties:
            molecular_data.append([
                current_cid, properties['MW'], 
                properties['nHA'], properties['nHD'], 
                properties['LogP'], properties['TPSA']
            ])
            # Download SDF
            download_sdf(current_cid)
        else:
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"CID {current_cid} - No Molecular Data Found\n")
        
        current_cid += 1
        processed_molecules += 1
    
    # Save the molecular data to a CSV file for today
    if molecular_data:
        columns = ['CID', 'MW', 'nHA', 'nHD', 'LogP', 'TPSA']
        molecular_df = pd.DataFrame(molecular_data, columns=columns)
        molecular_df.to_csv(f'Molecules_{start_cid}_to_{current_cid-1}.csv', index=False)
        print(f"Molecular data for CIDs {start_cid} to {current_cid-1} saved.")
    
    # Update the progress file
    with open(progress_file_path, 'w') as progress_file:
        progress_file.write(f"Start_CID\n{current_cid}\n")
    print(f"Progress updated. Next starting CID: {current_cid}")

# Read the last processed CID from the progress file
with open(progress_file_path, 'r') as progress_file:
    lines = progress_file.readlines()
    start_cid = int(lines[1].strip())

# Fetch molecules for today (10,000 molecules)
fetch_and_save_molecules(start_cid, molecules_per_day=10000)
