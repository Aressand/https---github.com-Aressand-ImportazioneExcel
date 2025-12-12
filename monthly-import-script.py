#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script per l'importazione mensile di 3 file Excel specifici in un database MySQL.
Questo script è progettato per essere eseguito una volta al mese per importare
i 3 nuovi file mensili, uno per ogni cartella specificata.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging
import argparse
from tqdm import tqdm

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monthly_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def connect_to_database(config):
    """Connessione al database MySQL"""
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            logging.info(f"Connesso al database MySQL: {config['database']}")
            return conn
    except Error as e:
        logging.error(f"Errore durante la connessione a MySQL: {e}")
        sys.exit(1)
    return None

def process_excel_file(file_path, folder_path, conn, cursor):
    """Elabora un singolo file Excel e importa i dati nel database"""
    filename = os.path.basename(file_path)
    
    start_time = time.time()
    row_count = 0
    status = 'error'
    error_message = ''
    
    try:
        logging.info(f"Elaborazione di {filename}...")
        
        # Leggi il file Excel
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Pulisci i nomi delle colonne (rimuovi spazi e caratteri speciali)
        df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Converti le date nel formato corretto
        date_columns = ['dt_attivazione', 'data_evento', 'data_firma']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        
        # Sostituisci i valori NaN con None per MySQL
        df = df.replace({np.nan: None})
        
        # Aggiungi colonne per il tracciamento
        df['source_file'] = filename
        df['source_folder'] = folder_path
        df['import_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Crea la query di inserimento
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO fatture_totali ({columns}) VALUES ({placeholders})"
        
        # Inserisci i dati nel database in batch
        batch_size = 1000
        total_rows = len(df)
        
        with tqdm(total=total_rows, desc=f"Importando {filename}") as pbar:
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i+batch_size].values.tolist()
                cursor.executemany(insert_query, batch)
                conn.commit()
                row_count += len(batch)
                pbar.update(len(batch))
        
        status = 'success'
        logging.info(f"Importazione completata per {filename}: {row_count} righe inserite")
        
    except Exception as e:
        conn.rollback()
        error_message = str(e)
        status = 'error'
        logging.error(f"Errore durante l'elaborazione di {filename}: {e}")
    
    finally:
        execution_time = time.time() - start_time
        
        # Registra l'importazione nel log
        log_query = """
        INSERT INTO import_log 
        (filename, folder_path, row_count, status, error_message, execution_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(log_query, (filename, folder_path, row_count, status, error_message, execution_time))
        conn.commit()
        
        return row_count

def get_latest_file(folder_path, pattern="*.xlsx"):
    """Ottiene il file più recente in base alla data di modifica"""
    try:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]
        if not files:
            logging.error(f"Nessun file Excel trovato nella cartella {folder_path}")
            return None
            
        latest_file = max(files, key=os.path.getmtime)
        logging.info(f"File più recente trovato: {latest_file}")
        return latest_file
    except Exception as e:
        logging.error(f"Errore nel trovare il file più recente in {folder_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Importa i file Excel mensili in un database MySQL')
    parser.add_argument('--host', default='localhost', help='Host MySQL')
    parser.add_argument('--user', required=True, help='Username MySQL')
    parser.add_argument('--password', required=True, help='Password MySQL')
    parser.add_argument('--database', required=True, help='Nome database MySQL')
    parser.add_argument('--folders', required=True, nargs='+', help='Percorsi delle 3 cartelle contenenti i file Excel mensili')
    parser.add_argument('--files', nargs='+', help='Percorsi specifici ai 3 file da importare (opzionale)')
    
    args = parser.parse_args()
    
    # Verifica che ci siano esattamente 3 cartelle o 3 file specifici
    if args.files and len(args.files) != 3:
        logging.error("È necessario specificare esattamente 3 file quando si usa l'opzione --files")
        sys.exit(1)
    
    if not args.files and len(args.folders) != 3:
        logging.error("È necessario specificare esattamente 3 cartelle quando non si specificano i file")
        sys.exit(1)
    
    db_config = {
        'host': args.host,
        'user': args.user,
        'password': args.password,
        'database': args.database
    }
    
    conn = connect_to_database(db_config)
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        total_processed = 0
        
        # Caso 1: File specifici forniti
        if args.files:
            for i, file_path in enumerate(args.files):
                if not os.path.exists(file_path):
                    logging.error(f"Il file {file_path} non esiste")
                    continue
                    
                folder_path = args.folders[i] if i < len(args.folders) else os.path.dirname(file_path)
                rows_imported = process_excel_file(file_path, folder_path, conn, cursor)
                total_processed += rows_imported
        
        # Caso 2: Trova automaticamente i file più recenti nelle cartelle
        else:
            for folder_path in args.folders:
                if not os.path.exists(folder_path):
                    logging.error(f"La cartella {folder_path} non esiste")
                    continue
                    
                latest_file = get_latest_file(folder_path)
                if latest_file:
                    rows_imported = process_excel_file(latest_file, folder_path, conn, cursor)
                    total_processed += rows_imported
        
        logging.info(f"Importazione mensile completata. Totale righe elaborate: {total_processed}")
        
    except Exception as e:
        logging.error(f"Errore durante l'esecuzione dello script: {e}")
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logging.info("Connessione al database chiusa")

if __name__ == "__main__":
    main()
