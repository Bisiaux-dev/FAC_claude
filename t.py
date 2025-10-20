import pandas as pd
import os
import warnings
import glob
import sys

# Force UTF-8 encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Adapté pour l'environnement Desktop\FAC
base_directory = os.path.dirname(os.path.abspath(__file__))
source_directory = base_directory
destination_directory = os.path.join(base_directory, 'Données transformé')
os.makedirs(destination_directory, exist_ok=True)

# Define files to convert with their sheet names
files_to_convert = {
    'NOUVEAU FAC PERSPECTIVIA.xlsx': '2025',
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def replace_unsupported_characters(text):
    """Replace unsupported Unicode characters with standard equivalents"""
    if not isinstance(text, str):
        return text
    return text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2026', '...')


def cleanse_data(df):
    """Clean DataFrame by replacing Excel errors with NA and cleaning text"""
    # Replace Excel error values
    df.replace(['#N/A', '#VALUE!', '#REF!', '#DIV/0!', '#NUM!', '#NAME?', '#NULL!'],
               pd.NA, inplace=True)

    # Apply character replacement to all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(replace_unsupported_characters)

    return df


# =============================================================================
# STEP 1 & 2: CONVERT XLSX TO CSV WITH PROPER ENCODING
# =============================================================================

def convert_xlsx_to_csv(files_dict, source_dir, dest_dir, encoding='utf_8_sig'):
    """Convert Excel files to CSV with proper encoding"""
    converted_files = []

    for file, sheet in files_dict.items():
        file_path = os.path.join(source_dir, file)

        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=sheet)

            # Clean the data
            df_clean = cleanse_data(df)

            # Generate output filename
            csv_file_name = file.replace('.xlsx', '.csv')
            output_file_path = os.path.join(dest_dir, csv_file_name)

            # Save to CSV with proper encoding and semicolon separator
            df_clean.to_csv(output_file_path, index=False, encoding=encoding, sep=';')

            converted_files.append(output_file_path)
            print(f"OK Converted: {file} -> {csv_file_name}")

        except Exception as e:
            print(f"ERROR processing {file}: {e}")

    return converted_files


# =============================================================================
# STEP 3: SEGMENT DATA BY VAGUE AND ÉTAT
# =============================================================================

def segment_by_vague(csv_files, dest_dir, vague_column='Vague', etat_column='�TAT'):
    """Create separate CSV files per vague with all data intact"""

    for csv_file in csv_files:
        try:
            # Read the CSV file with semicolon separator
            df = pd.read_csv(csv_file, encoding='utf_8_sig', sep=';')

            # Check if required columns exist
            if vague_column not in df.columns:
                print(f"WARNING: '{vague_column}' column not found in {csv_file}")
                continue

            # Flexible column matching for ETAT (encoding issues)
            etat_col_found = None
            for col in df.columns:
                if 'TAT' in col or col == etat_column:
                    etat_col_found = col
                    etat_column = col
                    break

            if not etat_col_found:
                print(f"WARNING: 'ETAT' column not found in {csv_file}")

            # Find detail columns with flexible matching for encoding issues
            reel_col = None
            prev_col = None
            pot_col = None
            for col in df.columns:
                if 'R' in col and 'l' in col and len(col) < 10:  # R��l or similar
                    reel_col = col
                elif 'Pr' in col and 'v' in col:  # Pr�visionnel
                    prev_col = col
                elif col == 'Potentiel':
                    pot_col = col

            # Check for payment columns
            payment_columns = ['PAIEMENT 1', 'PAIEMENT 2', 'PAIEMENT 3']
            available_payments = [col for col in payment_columns if col in df.columns]

            # Get base filename
            base_name = os.path.basename(csv_file).replace('.csv', '')

            # Get unique vagues (cycles)
            unique_vagues = df[vague_column].dropna().unique()

            print(f"\nProcessing: {base_name}")
            print(f"   Found {len(unique_vagues)} unique vagues/cycles")

            # Create a CSV for each vague
            for vague in unique_vagues:
                # Filter data for this vague
                df_vague = df[df[vague_column] == vague].copy()

                # Generate output filename
                vague_safe = str(vague).replace('/', '_').replace('\\', '_')
                output_filename = f"{base_name}_Vague_{vague_safe}.csv"
                output_path = os.path.join(dest_dir, output_filename)

                # Save to CSV
                df_vague.to_csv(output_path, index=False, encoding='utf_8_sig', sep=';')

                # Show summary
                if etat_column in df.columns:
                    etat_counts = df_vague[etat_column].value_counts()
                    print(f"   OK Vague '{vague}': {len(df_vague)} rows")
                    print(f"      Etats: {dict(etat_counts)}")

            # Define detailed status categories
            status_categories = {
                'R��l': ['PEC accord�', 'Factur�', 'Encaiss�'],
                'Pr�visionnel': ['ATT DE PEC', 'ATT DE PEC R1', 'ATT DE PEC R2', 'ATT DE PEC R3',
                                 'ATT DE PEC R4', 'ATT DE PEC R5', 'ATT DE PEC R6', 'ATT DE PEC R7',
                                 'ATT DE PEC R8', 'ATT DE PEC R9', 'ATT DE PEC R10', 'ATT DE PEC R11',
                                 'ATT DE PEC R12'],
                'Potentiel': ['Signature bi-parti � d�poser', 'D�p�t brouillon', 'Manque info', 'Manque documents']
            }

            # Map main categories to their detail columns
            detail_columns = {
                'R��l': 'R��l',
                'Pr�visionnel': 'Pr�visionnel',
                'Potentiel': 'Potentiel'
            }

            # Create enhanced summary with payment totals
            if etat_column in df.columns:
                summary_data = []

                for vague in unique_vagues:
                    df_vague = df[df[vague_column] == vague]

                    for etat in df_vague[etat_column].dropna().unique():
                        df_subset = df_vague[df_vague[etat_column] == etat]

                        row = {
                            vague_column: vague,
                            etat_column: etat,
                            'Count': len(df_subset)
                        }

                        # Add payment totals
                        for payment_col in available_payments:
                            payment_values = pd.to_numeric(df_subset[payment_col], errors='coerce')
                            total = payment_values.sum()
                            row[f'Total_{payment_col}'] = total

                        # Calculate total across all payments
                        if available_payments:
                            total_all_payments = sum(
                                pd.to_numeric(df_subset[col], errors='coerce').sum()
                                for col in available_payments
                            )
                            row['Total_All_Payments'] = total_all_payments

                        # Initialize all detailed status columns to 0
                        for category, statuses in status_categories.items():
                            for status in statuses:
                                row[status] = 0

                        # Count occurrences of each detailed status
                        if etat in detail_columns and detail_columns[etat] in df.columns:
                            detail_col = detail_columns[etat]
                            for detailed_status in df_subset[detail_col].value_counts().items():
                                status_name, count = detailed_status
                                if status_name in row:
                                    row[status_name] = count

                        # Calculate CA based on ÉTAT
                        if etat in ['Reel', 'R��l']:
                            row['CA_Reel'] = total_all_payments
                            row['CA_Previsionnel'] = 0
                            row['CA_Potentiel'] = 0
                        elif etat == 'Pr�visionnel':
                            row['CA_Reel'] = 0
                            row['CA_Previsionnel'] = len(df_subset) * 3100
                            row['CA_Potentiel'] = 0
                        elif etat == 'Potentiel':
                            row['CA_Reel'] = 0
                            row['CA_Previsionnel'] = 0
                            row['CA_Potentiel'] = len(df_subset) * 3100
                        else:
                            row['CA_Reel'] = 0
                            row['CA_Previsionnel'] = 0
                            row['CA_Potentiel'] = 0

                        summary_data.append(row)

                summary = pd.DataFrame(summary_data)

                # Save as "Données_Transformées"
                summary_path = os.path.join(dest_dir, f"Donnees_Transformees.csv")
                summary.to_csv(summary_path, index=False, encoding='utf_8_sig', sep=';')
                print(f"   OK Created summary: Donnees_Transformees.csv")

                # Create Intermediary Status CSV
                intermediary_columns = ['Vague', 'ÉTAT', 'Count']
                for category, statuses in status_categories.items():
                    for status in statuses:
                        intermediary_columns.append(status)

                intermediary_df = summary[intermediary_columns].copy()
                status_cols = [col for col in intermediary_columns if col not in ['Vague', 'ÉTAT', 'Count']]
                mask = (intermediary_df[status_cols] > 0).any(axis=1)
                intermediary_df_filtered = intermediary_df[mask]

                intermediary_path = os.path.join(dest_dir, f"Statuts_Intermediaires.csv")
                intermediary_df_filtered.to_csv(intermediary_path, index=False, encoding='utf_8_sig', sep=';')
                print(f"   OK Created intermediary status file: Statuts_Intermediaires.csv")

                # Create PROMO breakdown CSV
                promo_data = []
                for vague in unique_vagues:
                    df_vague = df[df[vague_column] == vague]
                    df_reel = df_vague[df_vague[etat_column] == 'R��l']

                    if not df_reel.empty and 'PROMO' in df.columns:
                        df_reel_clean = df_reel.copy()
                        df_reel_clean['PROMO'] = df_reel_clean['PROMO'].astype(str).str.strip().str.upper()
                        promo_counts = df_reel_clean['PROMO'].value_counts()

                        for promo, count in promo_counts.items():
                            if pd.notna(promo) and promo != 'NAN':
                                promo_data.append({
                                    'Vague': vague,
                                    'PROMO': promo,
                                    'Count': count
                                })

                if promo_data:
                    promo_df = pd.DataFrame(promo_data)
                    promo_path = os.path.join(dest_dir, f"PROMO_Reel_par_Vague.csv")
                    promo_df.to_csv(promo_path, index=False, encoding='utf_8_sig', sep=';')
                    print(f"   OK Created PROMO breakdown file: PROMO_Reel_par_Vague.csv")

                # =============================================================================
                # CREATE CHECKLISTS
                # =============================================================================

                print(f"\nCreating checklists...")

                # Create checklist directory
                checklist_dir = os.path.join(base_directory, 'Checklist')
                os.makedirs(checklist_dir, exist_ok=True)

                # Checklist 1: Cindy - PEC accordé
                if reel_col and reel_col in df.columns:
                    # Find the correct value for PEC accordé
                    pec_values = df[reel_col].unique()
                    pec_accorde_val = None
                    for val in pec_values:
                        if isinstance(val, str) and 'PEC' in val and 'accord' in val:
                            pec_accorde_val = val
                            break

                    if pec_accorde_val:
                        df_cindy = df[df[reel_col] == pec_accorde_val].copy()
                        if not df_cindy.empty:
                            cindy_path = os.path.join(checklist_dir, 'checklist_cindy.csv')
                            df_cindy.to_csv(cindy_path, index=False, encoding='utf_8_sig', sep=';')
                            print(f"   OK Checklist Cindy: {len(df_cindy)} formations")

                # Checklist 2: Admin dépôt initial
                if pot_col and pot_col in df.columns:
                    # Find the correct value
                    pot_values = df[pot_col].unique()
                    depot_val = None
                    for val in pot_values:
                        if isinstance(val, str) and 'Signature' in val and 'd' in val and 'poser' in val:
                            depot_val = val
                            break

                    if depot_val:
                        df_depot_initial = df[df[pot_col] == depot_val].copy()
                        if not df_depot_initial.empty:
                            depot_initial_path = os.path.join(checklist_dir, 'checklist_admin_depot_initial.csv')
                            df_depot_initial.to_csv(depot_initial_path, index=False, encoding='utf_8_sig', sep=';')
                            print(f"   OK Checklist Admin Depot Initial: {len(df_depot_initial)} formations")

                # Checklist 3: Admin vérifier dépôt
                if pot_col and pot_col in df.columns:
                    # Find the correct value
                    pot_values = df[pot_col].unique()
                    brouillon_val = None
                    for val in pot_values:
                        if isinstance(val, str) and 'D' in val and 'p' in val and 'brouillon' in val:
                            brouillon_val = val
                            break

                    if brouillon_val:
                        df_verifier_depot = df[df[pot_col] == brouillon_val].copy()
                        if not df_verifier_depot.empty:
                            verifier_depot_path = os.path.join(checklist_dir, 'checklist_admin_verifier_depot.csv')
                            df_verifier_depot.to_csv(verifier_depot_path, index=False, encoding='utf_8_sig', sep=';')
                            print(f"   OK Checklist Admin Verifier Depot: {len(df_verifier_depot)} formations")

                # Checklist 4: Équipe commercial
                if pot_col and pot_col in df.columns:
                    df_manque_signatures = df[df[pot_col] == 'Manque signatures'].copy()
                    if not df_manque_signatures.empty:
                        manque_signatures_path = os.path.join(checklist_dir, 'checklist_equipe_commercial.csv')
                        df_manque_signatures.to_csv(manque_signatures_path, index=False, encoding='utf_8_sig', sep=';')
                        print(f"   OK Checklist Equipe Commercial: {len(df_manque_signatures)} formations")

                # Checklist 5: Facturation en retard
                if 'Prochaine facturation' in df.columns:
                    from datetime import datetime
                    df['Prochaine facturation'] = pd.to_datetime(df['Prochaine facturation'], errors='coerce')
                    today = pd.Timestamp.now().normalize()

                    df_facturation_retard = df[
                        (df['Prochaine facturation'].notna()) &
                        (df['Prochaine facturation'] < today)
                    ].copy()

                    if not df_facturation_retard.empty:
                        facturation_retard_path = os.path.join(checklist_dir, 'checklist_facturation_en_retard.csv')
                        df_facturation_retard.to_csv(facturation_retard_path, index=False, encoding='utf_8_sig', sep=';')
                        print(f"   OK Checklist Facturation en Retard: {len(df_facturation_retard)} formations")

                # =============================================================================
                # CREATE CHECKLIST RECAP
                # =============================================================================

                print(f"\n[RECAP] Creating checklist recap...")

                all_checklist_files = glob.glob(os.path.join(checklist_dir, '*.csv'))
                checklist_files = [f for f in all_checklist_files if not f.endswith('checklist_recap.csv')]

                if checklist_files:
                    recap_data = []

                    for checklist_file in checklist_files:
                        try:
                            df_checklist = pd.read_csv(checklist_file, encoding='utf_8_sig', sep=';')
                            filename = os.path.basename(checklist_file)
                            row_count = len(df_checklist)

                            recap_data.append({
                                'Fichier': filename,
                                'Nombre de lignes': row_count
                            })

                        except Exception as e:
                            print(f"   WARNING Error reading {filename}: {e}")

                    if recap_data:
                        df_recap = pd.DataFrame(recap_data)
                        df_recap = df_recap.sort_values('Nombre de lignes', ascending=False)

                        total_row = pd.DataFrame({
                            'Fichier': ['TOTAL'],
                            'Nombre de lignes': [df_recap['Nombre de lignes'].sum()]
                        })
                        df_recap = pd.concat([df_recap, total_row], ignore_index=True)

                        recap_path = os.path.join(checklist_dir, 'checklist_recap.csv')
                        df_recap.to_csv(recap_path, index=False, encoding='utf_8_sig', sep=';')

                        print(f"   OK Checklist recap created: {len(checklist_files)} checklists")
                        print(f"   OK Total formations: {df_recap['Nombre de lignes'].iloc[-1]}")

        except Exception as e:
            print(f"ERROR segmenting {csv_file}: {e}")
            import traceback
            traceback.print_exc()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FAC PERSPECTIVIA - DATA PROCESSING")
    print("=" * 70)

    # Step 1 & 2: Convert Excel to CSV
    print("\n[STEP 1-2] Converting XLSX to CSV...")
    converted_files = convert_xlsx_to_csv(
        files_to_convert,
        source_directory,
        destination_directory
    )

    # Step 3: Segment by Vague and create checklists
    print("\n[STEP 3] Segmenting data and creating checklists...")
    segment_by_vague(converted_files, destination_directory)

    print("\n" + "=" * 70)
    print("OK PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Output location: {destination_directory}")
    print(f"Checklist location: {os.path.join(base_directory, 'Checklist')}")
