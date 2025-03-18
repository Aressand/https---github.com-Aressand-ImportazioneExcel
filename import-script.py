#C:\Users\Utente\Desktop\ImportazioneExcel\venv\Scripts\python.exe
# -*- coding: utf-8 -*-

"""
Script per l'importazione di file Excel in un database MySQL.
Supporta l'importazione di tutti i file in una cartella o di un file specifico.
"""

import os
import sys
import glob
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
        logging.FileHandler('import_excel.log'),
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

def get_existing_files(cursor):
    """Recupera i file già importati dal log"""
    try:
        cursor.execute("SELECT filename FROM import_log WHERE status = 'success'")
        return {row[0] for row in cursor.fetchall()}
    except Error as e:
        logging.error(f"Errore durante il recupero dei file importati: {e}")
        return set()

def process_excel_file(file_path, conn, cursor, existing_files):
    """Elabora un singolo file Excel e importa i dati nel database"""
    filename = os.path.basename(file_path)
    folder_path = os.path.dirname(file_path)
    
    # Controlla se il file è già stato importato
    if filename in existing_files:
        logging.info(f"File {filename} già importato, lo salto")
        return 0
    
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
        insert_query = f"INSERT INTO vendite ({columns}) VALUES ({placeholders})"
        
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

def main():
    parser = argparse.ArgumentParser(description='Importa file Excel in un database MySQL')
    parser.add_argument('--host', default='localhost', help='Host MySQL')
    parser.add_argument('--user', required=True, help='Username MySQL')
    parser.add_argument('--password', required=True, help='Password MySQL')
    parser.add_argument('--database', required=True, help='Nome database MySQL')
    parser.add_argument('--folder', help='Percorso della cartella contenente i file Excel')
    parser.add_argument('--file', help='Percorso specifico a un file Excel')
    
    args = parser.parse_args()
    
    # Verifica che sia specificato almeno un argomento tra --folder e --file
    if not args.folder and not args.file:
        logging.error("Devi specificare almeno un argomento tra --folder e --file")
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
        existing_files = get_existing_files(cursor)
        
        total_processed = 0
        
        # Caso 1: Importazione di un'intera cartella
        if args.folder:
            folder_path = args.folder
            if not os.path.exists(folder_path):
                logging.error(f"La cartella {folder_path} non esiste")
                return
                
            logging.info(f"Elaborazione dei file nella cartella: {folder_path}")
            excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
            
            if not excel_files:
                logging.warning(f"Nessun file Excel trovato nella cartella {folder_path}")
                return
                
            logging.info(f"Trovati {len(excel_files)} file Excel")
            
            for file_path in excel_files:
                rows_imported = process_excel_file(file_path, conn, cursor, existing_files)
                total_processed += rows_imported
        
        # Caso 2: Importazione di un file specifico
        elif args.file:
            file_path = args.file
            if not os.path.exists(file_path):
                logging.error(f"Il file {file_path} non esiste")
                return
                
            if not file_path.endswith('.xlsx'):
                logging.error(f"Il file {file_path} non è un file Excel (.xlsx)")
                return
                
            rows_imported = process_excel_file(file_path, conn, cursor, existing_files)
            total_processed = rows_imported
        
        logging.info(f"Importazione completata. Totale righe elaborate: {total_processed}")
        
    except Exception as e:
        logging.error(f"Errore durante l'esecuzione dello script: {e}")
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logging.info("Connessione al database chiusa")

if __name__ == "__main__":
    main()