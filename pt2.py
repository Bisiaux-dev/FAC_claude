import pandas as pd
import os
import warnings
import glob

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Define your directories
source_directory = r'C:\Users\Pierre\Desktop\FAC'
destination_directory = r'C:\Users\Pierre\Desktop\FAC\Données transformé'
os.makedirs(destination_directory, exist_ok=True)

# Define files to convert with their sheet names
files_to_convert = {
    'NOUVEAU FAC PERSPECTIVIA.xlsx': '2025',  # Update sheet name if needed
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
            print(f"[OK] Converted: {file} → {csv_file_name}")

        except Exception as e:
            print(f"[ERREUR] Error processing {file}: {e}")

    return converted_files


# =============================================================================
# STEP 3: SEGMENT DATA BY VAGUE AND ÉTAT
# =============================================================================

def segment_by_vague(csv_files, dest_dir, vague_column='Vague', etat_column='ÉTAT'):
    """
    Create separate CSV files per vague with all data intact
    Categorizes data using both Vague and État columns
    """

    for csv_file in csv_files:
        try:
            # Read the CSV file with semicolon separator
            df = pd.read_csv(csv_file, encoding='utf_8_sig', sep=';')

            # Check if required columns exist
            if vague_column not in df.columns:
                print(f"[WARN] Warning: '{vague_column}' column not found in {csv_file}")
                continue

            if etat_column not in df.columns:
                print(f"[WARN] Warning: '{etat_column}' column not found in {csv_file}")
                # Continue anyway if État is missing

            # Check for payment columns - USE PAIEMENT COLUMNS (OPTION A)
            payment_columns = ['PAIEMENT 1', 'PAIEMENT 2', 'PAIEMENT 3']
            available_payments = [col for col in payment_columns if col in df.columns]

            if not available_payments:
                print(f"[WARN] Warning: No payment columns found in {csv_file}")

            # Get base filename
            base_name = os.path.basename(csv_file).replace('.csv', '')

            # Get unique vagues (cycles)
            unique_vagues = df[vague_column].dropna().unique()

            print(f"\n[GRAPH] Processing: {base_name}")
            print(f"   Found {len(unique_vagues)} unique vagues/cycles")

            # Create a CSV for each vague
            for vague in unique_vagues:
                # Filter data for this vague
                df_vague = df[df[vague_column] == vague].copy()

                # Generate output filename
                vague_safe = str(vague).replace('/', '_').replace('\\', '_')
                output_filename = f"{base_name}_Vague_{vague_safe}.csv"
                output_path = os.path.join(dest_dir, output_filename)

                # Save to CSV (all data untransformed) with semicolon separator
                df_vague.to_csv(output_path, index=False, encoding='utf_8_sig', sep=';')

                # Show summary
                if etat_column in df.columns:
                    etat_counts = df_vague[etat_column].value_counts()
                    print(f"   [OK] Vague '{vague}': {len(df_vague)} rows")
                    print(f"      États: {dict(etat_counts)}")
                else:
                    print(f"   [OK] Vague '{vague}': {len(df_vague)} rows")

            # Define detailed status categories
            status_categories = {
                'Réél': ['PEC accordé', 'Facturé', 'Encaissé'],
                'Prévisionnel': ['ATT DE PEC', 'ATT DE PEC R1', 'ATT DE PEC R2', 'ATT DE PEC R3',
                                 'ATT DE PEC R4', 'ATT DE PEC R5', 'ATT DE PEC R6', 'ATT DE PEC R7',
                                 'ATT DE PEC R8', 'ATT DE PEC R9', 'ATT DE PEC R10', 'ATT DE PEC R11',
                                 'ATT DE PEC R12'],
                'Potentiel': ['Signature bi-parti à déposer', 'Dépôt brouillon', 'Manque info', 'Manque documents']
            }

            # Map main categories to their detail columns
            detail_columns = {
                'Réél': 'Réél',
                'Prévisionnel': 'Prévisionnel',
                'Potentiel': 'Potentiel'
            }

            # Create enhanced summary with payment totals - RENAMED FILE
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

                        # Add payment totals for each payment column
                        for payment_col in available_payments:
                            # Convert to numeric, handling errors
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

                        # Count occurrences of each detailed status from the appropriate column
                        if etat in detail_columns and detail_columns[etat] in df.columns:
                            detail_col = detail_columns[etat]
                            # Count the detailed statuses from the specific column
                            for detailed_status in df_subset[detail_col].value_counts().items():
                                status_name, count = detailed_status
                                # Only add if this status is in our predefined list
                                if status_name in row:
                                    row[status_name] = count

                        # Calculate CA based on ÉTAT
                        if etat in ['Réel', 'Réél']:
                            row['CA_Réél'] = total_all_payments
                            row['CA_Prévisionnel'] = 0
                            row['CA_Potentiel'] = 0
                        elif etat == 'Prévisionnel':
                            row['CA_Réél'] = 0
                            row['CA_Prévisionnel'] = len(df_subset) * 3100
                            row['CA_Potentiel'] = 0
                        elif etat == 'Potentiel':
                            row['CA_Réél'] = 0
                            row['CA_Prévisionnel'] = 0
                            row['CA_Potentiel'] = len(df_subset) * 3100
                        else:
                            row['CA_Réél'] = 0
                            row['CA_Prévisionnel'] = 0
                            row['CA_Potentiel'] = 0

                        summary_data.append(row)

                summary = pd.DataFrame(summary_data)

                # RENAMED: Save as "Données_Transformées" instead of "Summary_Vague_État"
                summary_path = os.path.join(dest_dir, f"Données_Transformées.csv")
                summary.to_csv(summary_path, index=False, encoding='utf_8_sig', sep=';')
                print(f"   [OK] Created summary: Données_Transformées.csv")

                # Create Intermediary Status CSV - only detailed status columns with values > 0
                intermediary_columns = ['Vague', 'ÉTAT', 'Count']

                # Add all detailed status columns
                for category, statuses in status_categories.items():
                    for status in statuses:
                        intermediary_columns.append(status)

                # Filter to only include these columns and rows where at least one status > 0
                intermediary_df = summary[intermediary_columns].copy()

                # Create a mask for rows where any detailed status column > 0
                status_cols = [col for col in intermediary_columns if col not in ['Vague', 'ÉTAT', 'Count']]
                mask = (intermediary_df[status_cols] > 0).any(axis=1)
                intermediary_df_filtered = intermediary_df[mask]

                # Save intermediary status CSV
                intermediary_path = os.path.join(dest_dir, f"Statuts_Intermédiaires.csv")
                intermediary_df_filtered.to_csv(intermediary_path, index=False, encoding='utf_8_sig', sep=';')
                print(f"   [OK] Created intermediary status file: Statuts_Intermédiaires.csv")

                # Create PROMO breakdown CSV - only Réél category with PROMO counts
                promo_data = []

                for vague in unique_vagues:
                    df_vague = df[df[vague_column] == vague]

                    # Only for Réél category
                    df_reel = df_vague[df_vague[etat_column] == 'Réél']

                    if not df_reel.empty and 'PROMO' in df.columns:
                        # Clean PROMO names: strip whitespace and normalize
                        df_reel_clean = df_reel.copy()
                        df_reel_clean['PROMO'] = df_reel_clean['PROMO'].astype(str).str.strip().str.upper()

                        # Count formations per PROMO
                        promo_counts = df_reel_clean['PROMO'].value_counts()

                        for promo, count in promo_counts.items():
                            if pd.notna(promo) and promo != 'NAN':  # Skip NaN values
                                promo_data.append({
                                    'Vague': vague,
                                    'PROMO': promo,
                                    'Count': count
                                })

                if promo_data:
                    promo_df = pd.DataFrame(promo_data)
                    promo_path = os.path.join(dest_dir, f"PROMO_Réél_par_Vague.csv")
                    promo_df.to_csv(promo_path, index=False, encoding='utf_8_sig', sep=';')
                    print(f"   [OK] Created PROMO breakdown file (Réél only): PROMO_Réél_par_Vague.csv")

                    # Display PROMO summary
                    print(f"\n[PROMO] PROMO Summary (Réél):")
                    for vague in unique_vagues:
                        df_vague_promo = promo_df[promo_df['Vague'] == vague]
                        total = df_vague_promo['Count'].sum()
                        if total > 0:
                            print(f"{vague}: {total} formations réelles")
                            promos = df_vague_promo.nlargest(5, 'Count')
                            for _, row in promos.iterrows():
                                print(f"  - {row['PROMO']}: {row['Count']}")
                else:
                    print(f"   [WARN] Warning: No PROMO data found or PROMO column missing")

                # Display summary table
                print(f"\n[DATA] Payment Summary by Vague and État:")
                print(summary.to_string(index=False))

                # Display CA summary
                print(f"\n[CA] CA Summary:")
                print(f"Total CA Réél: {summary['CA_Réél'].sum():,.2f}€")
                print(f"Total CA Prévisionnel: {summary['CA_Prévisionnel'].sum():,.2f}€")
                print(f"Total CA Potentiel: {summary['CA_Potentiel'].sum():,.2f}€")
                print(
                    f"Total CA Global: {(summary['CA_Réél'].sum() + summary['CA_Prévisionnel'].sum() + summary['CA_Potentiel'].sum()):,.2f}€")

                # Check for Potentiel/Prévisionnel with payments (should be zero)
                non_reel_states = ['Potentiel', 'Prévisionnel']
                for state in non_reel_states:
                    state_data = summary[summary[etat_column] == state]
                    if not state_data.empty and 'Total_All_Payments' in state_data.columns:
                        total = state_data['Total_All_Payments'].sum()
                        if total > 0:
                            print(f"\n[WARN] WARNING: Found {total}€ in payments for '{state}' (expected 0)")
                        else:
                            print(f"\n[OK] Confirmed: No payments for '{state}' (as expected)")

                # =============================================================================
                # CREATE CHECKLISTS
                # =============================================================================

                print(f"\n[LIST] Creating checklists...")

                # Create checklist directory
                checklist_dir = r'C:\Users\Pierre\Desktop\FAC\Checklist'
                os.makedirs(checklist_dir, exist_ok=True)

                # Checklist 1: Cindy - PEC accordé (from Réél column)
                if 'Réél' in df.columns:
                    df_cindy = df[df['Réél'] == 'PEC accordé'].copy()
                    if not df_cindy.empty:
                        cindy_path = os.path.join(checklist_dir, 'checklist_cindy.csv')
                        df_cindy.to_csv(cindy_path, index=False, encoding='utf_8_sig', sep=';')
                        print(f"   [OK] Checklist Cindy: {len(df_cindy)} formations (PEC accordé)")
                    else:
                        print(f"   [WARN] No formations found with 'PEC accordé' status")

                # Checklist 2: Admin dépôt initial - Signature bi-parti à déposer (from Potentiel column)
                if 'Potentiel' in df.columns:
                    df_depot_initial = df[df['Potentiel'] == 'Signature bi-parti à déposer'].copy()
                    if not df_depot_initial.empty:
                        depot_initial_path = os.path.join(checklist_dir, 'checklist_admin_dépôt_initial.csv')
                        df_depot_initial.to_csv(depot_initial_path, index=False, encoding='utf_8_sig', sep=';')
                        print(
                            f"   [OK] Checklist Admin Dépôt Initial: {len(df_depot_initial)} formations (Signature bi-parti à déposer)")
                    else:
                        print(f"   [WARN] No formations found with 'Signature bi-parti à déposer' status")

                # Checklist 3: Admin vérifier dépôt - Dépôt brouillon (from Potentiel column)
                if 'Potentiel' in df.columns:
                    df_verifier_depot = df[df['Potentiel'] == 'Dépôt brouillon'].copy()
                    if not df_verifier_depot.empty:
                        verifier_depot_path = os.path.join(checklist_dir, 'checklist_admin_vérifier_dépôt.csv')
                        df_verifier_depot.to_csv(verifier_depot_path, index=False, encoding='utf_8_sig', sep=';')
                        print(
                            f"   [OK] Checklist Admin Vérifier Dépôt: {len(df_verifier_depot)} formations (Dépôt brouillon)")
                    else:
                        print(f"   [WARN] No formations found with 'Dépôt brouillon' status")

                # Checklist 4: Équipe commercial - Manque signatures (from Potentiel column)
                if 'Potentiel' in df.columns:
                    df_manque_signatures = df[df['Potentiel'] == 'Manque signatures'].copy()
                    if not df_manque_signatures.empty:
                        manque_signatures_path = os.path.join(checklist_dir, 'checklist_équipe_commercial.csv')
                        df_manque_signatures.to_csv(manque_signatures_path, index=False, encoding='utf_8_sig', sep=';')
                        print(
                            f"   [OK] Checklist Équipe Commercial: {len(df_manque_signatures)} formations (Manque signatures)")
                    else:
                        print(f"   [WARN] No formations found with 'Manque signatures' status")

                # Checklist 5: Dépôt que le client doit effectuer - Dépôt irréalisable faute de mandat (from Potentiel column)
                if 'Potentiel' in df.columns:
                    df_depot_client = df[df['Potentiel'] == 'Dépôt irréalisable faute de mandat'].copy()
                    if not df_depot_client.empty:
                        depot_client_path = os.path.join(checklist_dir, 'dépôt_que_le_client_doit_effectuer.csv')
                        df_depot_client.to_csv(depot_client_path, index=False, encoding='utf_8_sig', sep=';')
                        print(
                            f"   [OK] Checklist Dépôt Client: {len(df_depot_client)} formations (Dépôt irréalisable faute de mandat)")
                    else:
                        print(f"   [WARN] No formations found with 'Dépôt irréalisable faute de mandat' status")

                # Checklist 6: Prochaine facturation - Facturations en retard
                if 'Prochaine facturation' in df.columns:
                    from datetime import datetime

                    # Convert 'Prochaine facturation' to datetime
                    df['Prochaine facturation'] = pd.to_datetime(df['Prochaine facturation'], errors='coerce')

                    # Get today's date (without time)
                    today = pd.Timestamp.now().normalize()

                    # Filter rows where 'Prochaine facturation' is before today (and not NaT)
                    df_facturation_retard = df[
                        (df['Prochaine facturation'].notna()) &
                        (df['Prochaine facturation'] < today)
                    ].copy()

                    if not df_facturation_retard.empty:
                        facturation_retard_path = os.path.join(checklist_dir, 'checklist_facturation_en_retard.csv')
                        df_facturation_retard.to_csv(facturation_retard_path, index=False, encoding='utf_8_sig', sep=';')
                        print(
                            f"   [OK] Checklist Facturation en Retard: {len(df_facturation_retard)} formations (Date de facturation dépassée)")

                        # Show some details
                        oldest_date = df_facturation_retard['Prochaine facturation'].min()
                        print(f"      Date la plus ancienne: {oldest_date.strftime('%Y-%m-%d')}")
                    else:
                        print(f"   [OK] No overdue invoices - all up to date!")

                # Checklist 7: Trésorerie en retard - Facturé depuis plus de 2 mois
                if 'Réél' in df.columns and 'DATE DE DEBUT FORMATION' in df.columns:
                    from datetime import datetime, timedelta

                    # Convert 'DATE DE DEBUT FORMATION' to datetime
                    df['DATE DE DEBUT FORMATION'] = pd.to_datetime(df['DATE DE DEBUT FORMATION'], errors='coerce')

                    # Get today's date (without time)
                    today = pd.Timestamp.now().normalize()

                    # Calculate date 2 months ago (60 days)
                    two_months_ago = today - timedelta(days=90)

                    # Filter rows where 'Réél' is 'Facturé' AND 'DATE DE DEBUT FORMATION' is more than 3 months old
                    df_tresorerie_retard = df[
                        (df['Réél'] == 'Facturé') &
                        (df['DATE DE DEBUT FORMATION'].notna()) &
                        (df['DATE DE DEBUT FORMATION'] < two_months_ago)
                    ].copy()

                    if not df_tresorerie_retard.empty:
                        tresorerie_retard_path = os.path.join(checklist_dir, 'tresorerie_en_retard.csv')
                        df_tresorerie_retard.to_csv(tresorerie_retard_path, index=False, encoding='utf_8_sig', sep=';')
                        print(
                            f"   [OK] Checklist Trésorerie en Retard: {len(df_tresorerie_retard)} formations (Facturé depuis plus de 2 mois)")

                        # Show some details
                        oldest_date = df_tresorerie_retard['DATE DE DEBUT FORMATION'].min()
                        print(f"      Date de début la plus ancienne: {oldest_date.strftime('%Y-%m-%d')}")
                    else:
                        print(f"   [OK] No overdue treasury items - all up to date!")

                # =============================================================================
                # CREATE CHECKLIST RECAP
                # =============================================================================

                print(f"\n[RECAP] Creating checklist recap...")

                # Get all CSV files in checklist directory (excluding recap file)
                all_checklist_files = glob.glob(os.path.join(checklist_dir, '*.csv'))
                checklist_files = [f for f in all_checklist_files if not f.endswith('checklist_recap.csv')]

                if checklist_files:
                    recap_data = []

                    for checklist_file in checklist_files:
                        try:
                            # Read CSV to count rows
                            df_checklist = pd.read_csv(checklist_file, encoding='utf_8_sig', sep=';')

                            # Get filename without path and convert to XLSX without accents
                            filename = os.path.basename(checklist_file).replace('.csv', '.xlsx')
                            filename = filename.replace('é', 'e').replace('è', 'e').replace('ô', 'o')

                            # Count rows (excluding header)
                            row_count = len(df_checklist)

                            recap_data.append({
                                'Fichier': filename,
                                'Nombre de lignes': row_count
                            })

                        except Exception as e:
                            print(f"   [WARN] Error reading {os.path.basename(checklist_file)}: {e}")

                    # Create recap DataFrame
                    if recap_data:
                        df_recap = pd.DataFrame(recap_data)

                        # Sort by number of lines descending
                        df_recap = df_recap.sort_values('Nombre de lignes', ascending=False)

                        # Add total row
                        total_row = pd.DataFrame({
                            'Fichier': ['TOTAL'],
                            'Nombre de lignes': [df_recap['Nombre de lignes'].sum()]
                        })
                        df_recap = pd.concat([df_recap, total_row], ignore_index=True)

                        # Save recap CSV
                        recap_path = os.path.join(checklist_dir, 'checklist_recap.csv')
                        df_recap.to_csv(recap_path, index=False, encoding='utf_8_sig', sep=';')

                        print(f"   [OK] Checklist recap created: {len(checklist_files)} checklists analyzed")
                        print(f"   [OK] Total formations across all checklists: {df_recap['Nombre de lignes'].iloc[-1]}")

                        # Display recap
                        print(f"\n   Recap:")
                        for _, row in df_recap.iterrows():
                            print(f"   {row['Fichier']}: {int(row['Nombre de lignes'])} ligne(s)")

        except Exception as e:
            print(f"[ERREUR] Error segmenting {csv_file}: {e}")
            import traceback
            traceback.print_exc()


# =============================================================================
# STEP 4: CREATE VISUALIZATIONS
# =============================================================================

def create_payment_visualization(dest_dir, graph_dir):
    """
    Create a bar chart showing payment totals by Vague for Réel status only
    """
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        # Read the transformed data
        summary_path = os.path.join(dest_dir, 'Données_Transformées.csv')
        if not os.path.exists(summary_path):
            print("[WARN] Warning: Données_Transformées.csv not found. Skipping visualization.")
            return

        df_summary = pd.read_csv(summary_path, encoding='utf_8_sig', sep=';')

        # Debug: Print column names to verify correct parsing
        print(f"Debug - Columns in summary: {df_summary.columns.tolist()[:5]}")  # Print first 5 columns

        # Filter only 'Réel' or 'Réél' status (handle accent variations)
        df_reel = df_summary[df_summary['ÉTAT'].isin(['Réel', 'Réél'])].copy()

        if df_reel.empty:
            print("[WARN] Warning: No 'Réel' or 'Réél' data found for visualization.")
            return

        # Get unique vagues
        vagues = df_reel['Vague'].unique()

        # Prepare data for plotting - USE PAIEMENT COLUMNS (OPTION A)
        payment_columns = ['Total_PAIEMENT 1', 'Total_PAIEMENT 2', 'Total_PAIEMENT 3']

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 7))

        # Set the width of bars and positions
        x = np.arange(len(payment_columns))
        width = 0.25

        # Define colors for each vague
        colors = ['#2E86AB', '#A23B72', '#F18F01']  # Blue, Purple, Orange

        # Collect payment data for totals
        payment_totals = [0, 0, 0]

        # Plot bars for each vague
        for i, vague in enumerate(vagues):
            vague_data = df_reel[df_reel['Vague'] == vague]

            if not vague_data.empty:
                values = [
                    vague_data['Total_PAIEMENT 1'].sum(),
                    vague_data['Total_PAIEMENT 2'].sum(),
                    vague_data['Total_PAIEMENT 3'].sum()
                ]

                # Add to totals
                for j in range(3):
                    payment_totals[j] += values[j]

                offset = width * (i - len(vagues) / 2 + 0.5)
                bars = ax.bar(x + offset, values, width, label=f'Vague {vague}',
                              color=colors[i % len(colors)])

                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width() / 2., height,
                                f'{height:,.0f}€',
                                ha='center', va='bottom', fontsize=9, rotation=0)

        # Customize the plot
        ax.set_xlabel('Type de Paiement', fontsize=12, fontweight='bold')
        ax.set_ylabel('Montant Total (€)', fontsize=12, fontweight='bold')
        ax.set_title('Paiements Réels par Vague et Type de Paiement',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(['Paiement 1', 'Paiement 2', 'Paiement 3'])
        ax.legend(title='Cycles', fontsize=10, title_fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Format y-axis to show currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}€'))

        # Calculate and display totals
        total_global = sum(payment_totals)
        fig.text(0.5, 0.02,
                 f'TOTAL: Paiement 1: {payment_totals[0]:,.0f}€ | Paiement 2: {payment_totals[1]:,.0f}€ | Paiement 3: {payment_totals[2]:,.0f}€ | Global: {total_global:,.0f}€',
                 ha='center', fontsize=11, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))

        plt.tight_layout(rect=[0, 0.04, 1, 1])  # Add space at bottom for text

        # Create graph directory if it doesn't exist
        os.makedirs(graph_dir, exist_ok=True)

        # Save the figure
        output_path = os.path.join(graph_dir, 'Paiements_par_Vague.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n[GRAPH] Visualization created: {output_path}")

    except Exception as e:
        print(f"[ERREUR] Error creating visualization: {e}")
        import traceback
        traceback.print_exc()


def create_status_count_visualization(dest_dir, graph_dir):
    """
    Create a 3x3 grid showing Count by ÉTAT and Vague
    """
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        # Read the transformed data
        summary_path = os.path.join(dest_dir, 'Données_Transformées.csv')
        if not os.path.exists(summary_path):
            print("[WARN] Warning: Données_Transformées.csv not found. Skipping visualization.")
            return

        df_summary = pd.read_csv(summary_path, encoding='utf_8_sig', sep=';')

        # Get unique vagues and états
        vagues = sorted(df_summary['Vague'].unique())
        etats = ['Réél', 'Prévisionnel', 'Potentiel']  # Fixed order

        # Create pivot table for the data
        pivot_data = []
        for vague in vagues:
            row = []
            for etat in etats:
                mask = (df_summary['Vague'] == vague) & (df_summary['ÉTAT'] == etat)
                count = df_summary[mask]['Count'].sum() if mask.any() else 0
                row.append(count)
            pivot_data.append(row)

        pivot_data = np.array(pivot_data)

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create heatmap-style bar chart
        x = np.arange(len(etats))
        width = 0.25
        colors = ['#2E86AB', '#A23B72', '#F18F01']  # Blue, Purple, Orange

        for i, vague in enumerate(vagues):
            offset = width * (i - len(vagues) / 2 + 0.5)
            bars = ax.bar(x + offset, pivot_data[i], width,
                          label=f'{vague}', color=colors[i % len(colors)])

            # Add value labels on bars
            for j, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Customize the plot
        ax.set_xlabel('État de Facturation', fontsize=13, fontweight='bold')
        ax.set_ylabel('Nombre de Formations', fontsize=13, fontweight='bold')
        ax.set_title('Répartition des Formations par Vague et État',
                     fontsize=15, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(etats, fontsize=11)

        # Set y-axis limit to add space for legend (30% higher than max value)
        max_value = pivot_data.max()
        ax.set_ylim(0, max_value * 1.3)

        ax.legend(title='Cycles', fontsize=11, title_fontsize=12, loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Calculate totals for each état across all vagues
        total_reel = int(pivot_data[:, 0].sum())
        total_previsionnel = int(pivot_data[:, 1].sum())
        total_potentiel = int(pivot_data[:, 2].sum())
        total_global = total_reel + total_previsionnel + total_potentiel

        # Add total recap at the bottom
        fig.text(0.5, 0.02,
                 f'TOTAL: Réél: {total_reel} | Prévisionnel: {total_previsionnel} | Potentiel: {total_potentiel} | Global: {total_global}',
                 ha='center', fontsize=11, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))

        plt.tight_layout(rect=[0, 0.04, 1, 1])  # Add space at bottom for text

        # Create graph directory if it doesn't exist
        os.makedirs(graph_dir, exist_ok=True)

        # Save the figure
        output_path = os.path.join(graph_dir, 'Statut_Formations_par_Vague.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[GRAPH] Status visualization created: {output_path}")

        # Print summary table
        print("\n[LIST] Summary Table:")
        print(f"{'Vague':<12} {'Réél':<12} {'Prévisionnel':<15} {'Potentiel':<12} {'Total':<10}")
        print("-" * 65)
        for i, vague in enumerate(vagues):
            total = pivot_data[i].sum()
            print(
                f"{vague:<12} {int(pivot_data[i][0]):<12} {int(pivot_data[i][1]):<15} {int(pivot_data[i][2]):<12} {int(total):<10}")
        print("-" * 65)
        grand_total = pivot_data.sum()
        print(
            f"{'TOTAL':<12} {int(pivot_data[:, 0].sum()):<12} {int(pivot_data[:, 1].sum()):<15} {int(pivot_data[:, 2].sum()):<12} {int(pivot_data.sum()):<10}")

    except Exception as e:
        print(f"[ERREUR] Error creating status visualization: {e}")
        import traceback
        traceback.print_exc()


def create_ca_visualization_by_vague(dest_dir, graph_dir):
    """
    Create a single bar chart showing CA Réél, CA Prévisionnel, and CA Potentiel for all Vagues
    3 categories (x-axis) x 3 vagues (color-coded bars)
    """
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        # Read the transformed data
        summary_path = os.path.join(dest_dir, 'Données_Transformées.csv')
        if not os.path.exists(summary_path):
            print("[WARN] Warning: Données_Transformées.csv not found. Skipping visualization.")
            return

        df_summary = pd.read_csv(summary_path, encoding='utf_8_sig', sep=';')

        # Get unique vagues
        vagues = sorted(df_summary['Vague'].unique())

        # Create graph directory if it doesn't exist
        os.makedirs(graph_dir, exist_ok=True)

        # Prepare data: 3 CA categories
        categories = ['CA Réél', 'CA Prévisionnel', 'CA Potentiel']

        # Create pivot data structure
        ca_data = []
        for vague in vagues:
            df_vague = df_summary[df_summary['Vague'] == vague]
            ca_reel = df_vague['CA_Réél'].sum()
            ca_previsionnel = df_vague['CA_Prévisionnel'].sum()
            ca_potentiel = df_vague['CA_Potentiel'].sum()
            ca_data.append([ca_reel, ca_previsionnel, ca_potentiel])

        ca_data = np.array(ca_data)

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Set the width of bars and positions
        x = np.arange(len(categories))
        width = 0.25

        # Define colors for each vague
        colors = ['#2E86AB', '#A23B72', '#F18F01']  # Blue, Purple, Orange

        # Plot bars for each vague
        for i, vague in enumerate(vagues):
            offset = width * (i - len(vagues) / 2 + 0.5)
            bars = ax.bar(x + offset, ca_data[i], width,
                          label=f'{vague}', color=colors[i % len(colors)])

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{height:,.0f}€',
                            ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Customize the plot
        ax.set_xlabel('Catégorie de Chiffre d\'Affaires', fontsize=13, fontweight='bold')
        ax.set_ylabel('Montant (€)', fontsize=13, fontweight='bold')
        ax.set_title('Chiffre d\'Affaires par Catégorie et par Vague',
                     fontsize=15, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)

        # Set y-axis limit to add space for legend
        max_value = ca_data.max()
        ax.set_ylim(0, max_value * 1.25)

        ax.legend(title='Cycles', fontsize=11, title_fontsize=12, loc='upper left')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Format y-axis to show currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}€'))

        # Add total CA at the bottom
        total_ca_reel = ca_data[:, 0].sum()
        total_ca_previsionnel = ca_data[:, 1].sum()
        total_ca_potentiel = ca_data[:, 2].sum()
        total_global = total_ca_reel + total_ca_previsionnel + total_ca_potentiel

        # Add text below the chart with proper spacing
        fig.text(0.5, 0.01,
                 f'Total Global: {total_global:,.0f}€',
                 ha='center', fontsize=11, fontweight='bold')
        fig.text(0.5, -0.02,
                 f'(Réél: {total_ca_reel:,.0f}€  |  Prévisionnel: {total_ca_previsionnel:,.0f}€  |  Potentiel: {total_ca_potentiel:,.0f}€)',
                 ha='center', fontsize=9)

        plt.tight_layout(rect=[0, 0.03, 1, 1])  # Add space at bottom for text

        # Save the figure
        output_path = os.path.join(graph_dir, 'CA_par_Catégorie_Toutes_Vagues.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[GRAPH] CA visualization created: {output_path}")

    except Exception as e:
        print(f"[ERREUR] Error creating CA visualization: {e}")
        import traceback
        traceback.print_exc()


def create_intermediary_status_visualization(dest_dir, graph_dir):
    """
    Create visualizations for intermediary statuses per vague and per category
    """
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        # Read the intermediary status data
        intermediary_path = os.path.join(dest_dir, 'Statuts_Intermédiaires.csv')
        if not os.path.exists(intermediary_path):
            print("[WARN] Warning: Statuts_Intermédiaires.csv not found. Skipping visualization.")
            return

        df_inter = pd.read_csv(intermediary_path, encoding='utf_8_sig', sep=';')

        # Create graph directory if it doesn't exist
        os.makedirs(graph_dir, exist_ok=True)

        # Define status categories
        status_categories = {
            'Réél': ['PEC accordé', 'Facturé', 'Encaissé'],
            'Prévisionnel': ['ATT DE PEC', 'ATT DE PEC R1', 'ATT DE PEC R2', 'ATT DE PEC R3',
                             'ATT DE PEC R4', 'ATT DE PEC R5', 'ATT DE PEC R6', 'ATT DE PEC R7',
                             'ATT DE PEC R8', 'ATT DE PEC R9', 'ATT DE PEC R10', 'ATT DE PEC R11',
                             'ATT DE PEC R12'],
            'Potentiel': ['Signature bi-parti à déposer', 'Dépôt brouillon', 'Manque info', 'Manque documents']
        }

        # Get unique vagues
        vagues = sorted(df_inter['Vague'].unique())
        colors = ['#2E86AB', '#A23B72', '#F18F01']  # Blue, Purple, Orange

        # Create one visualization per category
        for category, statuses in status_categories.items():
            # Filter data for this category
            df_category = df_inter[df_inter['ÉTAT'] == category]

            if df_category.empty:
                continue

            # Get statuses that have values > 0
            active_statuses = []
            for status in statuses:
                if status in df_category.columns and df_category[status].sum() > 0:
                    active_statuses.append(status)

            if not active_statuses:
                continue

            # Create the plot
            fig, ax = plt.subplots(figsize=(14, 8))

            # Set the width of bars and positions
            x = np.arange(len(active_statuses))
            width = 0.25

            # Calculate totals for each status
            status_totals = {status: 0 for status in active_statuses}

            # Plot bars for each vague
            for i, vague in enumerate(vagues):
                df_vague = df_category[df_category['Vague'] == vague]

                if not df_vague.empty:
                    values = [df_vague[status].sum() for status in active_statuses]

                    # Add to totals
                    for j, status in enumerate(active_statuses):
                        status_totals[status] += values[j]

                    offset = width * (i - len(vagues) / 2 + 0.5)
                    bars = ax.bar(x + offset, values, width,
                                  label=f'{vague}', color=colors[i % len(colors)])

                    # Add value labels on bars
                    for bar in bars:
                        height = bar.get_height()
                        if height > 0:
                            ax.text(bar.get_x() + bar.get_width() / 2., height,
                                    f'{int(height)}',
                                    ha='center', va='bottom', fontsize=9, fontweight='bold')

            # Customize the plot
            ax.set_xlabel('Statut Intermédiaire', fontsize=12, fontweight='bold')
            ax.set_ylabel('Nombre de Formations', fontsize=12, fontweight='bold')
            ax.set_title(f'Statuts Intermédiaires - {category}',
                         fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(active_statuses, rotation=45, ha='right', fontsize=9)
            ax.legend(title='Cycles', fontsize=10, title_fontsize=11)
            ax.grid(axis='y', alpha=0.3, linestyle='--')

            # Add totals at the bottom
            total_global = sum(status_totals.values())
            totals_text = " | ".join([f"{status}: {int(count)}" for status, count in status_totals.items()])
            fig.text(0.5, 0.02,
                     f'TOTAL ({category}): {totals_text} | Global: {int(total_global)}',
                     ha='center', fontsize=10, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))

            plt.tight_layout(rect=[0, 0.04, 1, 1])  # Add space at bottom for text

            # Save the figure
            category_safe = category.replace('é', 'e').replace(' ', '_')
            output_path = os.path.join(graph_dir, f'Statuts_Intermédiaires_{category_safe}.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"[GRAPH] Intermediary status visualization created for {category}: {output_path}")

    except Exception as e:
        print(f"[ERREUR] Error creating intermediary status visualization: {e}")
        import traceback
        traceback.print_exc()


def create_promo_visualization(dest_dir, graph_dir):
    """
    Create single visualization with 3 bars (one per Vague) showing PROMO breakdown
    """
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        # Read the PROMO data
        promo_path = os.path.join(dest_dir, 'PROMO_Réél_par_Vague.csv')
        if not os.path.exists(promo_path):
            print("[WARN] Warning: PROMO_Réél_par_Vague.csv not found. Skipping visualization.")
            return

        df_promo = pd.read_csv(promo_path, encoding='utf_8_sig', sep=';')

        # Create graph directory if it doesn't exist
        os.makedirs(graph_dir, exist_ok=True)

        # Get unique vagues and promos
        vagues = sorted(df_promo['Vague'].unique())
        all_promos = sorted(df_promo['PROMO'].unique())

        # Calculate totals per vague
        vague_totals = {vague: df_promo[df_promo['Vague'] == vague]['Count'].sum()
                        for vague in vagues}

        # Create pivot data structure: rows=vagues, columns=promos
        promo_data = []
        for vague in vagues:
            row = []
            for promo in all_promos:
                df_subset = df_promo[(df_promo['Vague'] == vague) & (df_promo['PROMO'] == promo)]
                count = df_subset['Count'].sum() if not df_subset.empty else 0
                row.append(count)
            promo_data.append(row)

        promo_data = np.array(promo_data)

        # Calculate global total and percentage for each PROMO (across all vagues)
        global_total = promo_data.sum()
        promo_global_totals = {promo: promo_data[:, i].sum() for i, promo in enumerate(all_promos)}
        promo_percentages = {promo: (count / global_total * 100) if global_total > 0 else 0
                            for promo, count in promo_global_totals.items()}

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Set positions for the 3 vague bars
        x = np.arange(len(vagues))
        width = 0.6

        # Define colors for each PROMO (will be used in stacked bars and legend)
        promo_colors = plt.cm.Set3(np.linspace(0, 1, len(all_promos)))

        # Create stacked bars
        bottom = np.zeros(len(vagues))

        for i, promo in enumerate(all_promos):
            values = promo_data[:, i]
            # Create label with percentage for legend
            promo_label = f'{promo} ({promo_percentages[promo]:.1f}%)'
            bars = ax.bar(x, values, width, label=promo_label, bottom=bottom, color=promo_colors[i])

            # Add value labels on bars (only if value > 0)
            for j, (bar, val) in enumerate(zip(bars, values)):
                if val > 0:
                    height = bar.get_height()
                    y_pos = bottom[j] + height / 2

                    # Calculate percentage
                    percentage = (val / vague_totals[vagues[j]]) * 100

                    # For EPR and EC, show count and percentage
                    if promo in ['EPR', 'EC']:
                        label_text = f'{int(val)}\n({percentage:.1f}%)'
                        fontsize = 9
                    else:
                        label_text = f'{int(val)}'
                        fontsize = 9

                    ax.text(bar.get_x() + bar.get_width() / 2., y_pos,
                            label_text,
                            ha='center', va='center', fontsize=fontsize, fontweight='bold')

            bottom += values

        # Customize the plot
        ax.set_xlabel('Vague', fontsize=13, fontweight='bold')
        ax.set_ylabel('Nombre de Formations Réelles', fontsize=13, fontweight='bold')
        ax.set_title('Répartition des Formations Réelles par PROMO et par Vague',
                     fontsize=15, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(vagues, fontsize=12)

        # Add legend with percentages (% across all vagues)
        ax.legend(title='PROMO (% global sur 3 vagues)', fontsize=8, title_fontsize=9,
                 loc='upper right', ncol=2, framealpha=0.95)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add totals for each vague at the bottom
        totals_text = "  |  ".join([f"{vague}: {int(promo_data[i].sum())} formations"
                                    for i, vague in enumerate(vagues)])
        fig.text(0.5, 0.01, totals_text,
                 ha='center', fontsize=10, fontweight='bold')

        plt.tight_layout(rect=[0, 0.03, 1, 1])

        # Save the figure
        output_path = os.path.join(graph_dir, 'PROMO_Reel_par_Vague.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[GRAPH] PROMO visualization created: {output_path}")

    except Exception as e:
        print(f"[ERREUR] Error creating PROMO visualization: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("XLSX TO CSV CONVERTER - VAGUE SEGMENTATION")
    print("=" * 70)

    # Step 1 & 2: Convert Excel to CSV with encoding
    print("\n[STEP 1-2] Converting XLSX to CSV with proper encoding...")
    converted_files = convert_xlsx_to_csv(
        files_to_convert,
        source_directory,
        destination_directory
    )

    # Step 3: Segment by Vague
    print("\n[STEP 3] Segmenting data by Vague (cycles)...")
    segment_by_vague(converted_files, destination_directory)

    # Step 4: Create visualizations
    print("\n[STEP 4] Creating visualizations...")
    graph_directory = r'C:\Users\Pierre\Desktop\FAC\Graphiques'
    create_payment_visualization(destination_directory, graph_directory)
    create_status_count_visualization(destination_directory, graph_directory)
    create_ca_visualization_by_vague(destination_directory, graph_directory)
    create_intermediary_status_visualization(destination_directory, graph_directory)
    create_promo_visualization(destination_directory, graph_directory)

    # Step 5: Convert checklist CSV to XLSX for email sending
    print("\n[STEP 5] Converting checklist CSV to XLSX for email...")
    checklist_dir = r'C:\Users\Pierre\Desktop\FAC\Checklist'
    csv_files = glob.glob(os.path.join(checklist_dir, '*.csv'))

    for csv_file in csv_files:
        try:
            # Read CSV
            df = pd.read_csv(csv_file, sep=';', encoding='utf_8_sig')
            # Generate XLSX filename (without accents)
            xlsx_filename = os.path.basename(csv_file).replace('.csv', '.xlsx')
            # Remove accents from filename
            xlsx_filename = xlsx_filename.replace('é', 'e').replace('è', 'e').replace('ô', 'o')
            xlsx_path = os.path.join(checklist_dir, xlsx_filename)
            # Save to Excel
            df.to_excel(xlsx_path, index=False, engine='openpyxl')
            print(f"   [OK] Converted: {os.path.basename(csv_file)} -> {xlsx_filename}")
        except Exception as e:
            print(f"   [ERROR] Failed to convert {os.path.basename(csv_file)}: {e}")

    print("\n" + "=" * 70)
    print("[OK] PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Output location: {destination_directory}")
    print(f"Graph location: {graph_directory}")
    print(f"Checklist location: {checklist_dir} (CSV + XLSX)")
