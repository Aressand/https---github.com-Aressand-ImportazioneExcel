#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script per l'installazione e la configurazione dell'interfaccia web
"""

import os
import sys
import argparse
import shutil
import subprocess
import configparser

def parse_arguments():
    parser = argparse.ArgumentParser(description='Configura l\'interfaccia web per l\'importazione dei file Excel')
    parser.add_argument('--db-host', default='localhost', help='Host del database MySQL')
    parser.add_argument('--db-user', required=True, help='Nome utente MySQL')
    parser.add_argument('--db-password', required=True, help='Password MySQL')
    parser.add_argument('--db-name', required=True, help='Nome del database MySQL')
    parser.add_argument('--folder1', required=True, help='Percorso della prima cartella')
    parser.add_argument('--folder2', required=True, help='Percorso della seconda cartella')
    parser.add_argument('--folder3', required=True, help='Percorso della terza cartella')
    parser.add_argument('--port', type=int, default=5000, help='Porta su cui eseguire l\'applicazione web')
    
    return parser.parse_args()

def create_directory_structure():
    """Crea la struttura delle directory per l'applicazione web"""
    print("Creazione della struttura delle directory...")
    
    # Crea le cartelle necessarie
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Struttura delle directory creata con successo")

def install_dependencies():
    """Installa le dipendenze Python necessarie"""
    print("Installazione delle dipendenze...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask', 'mysql-connector-python', 'pandas', 'numpy', 'tqdm', 'openpyxl'], 
                       check=True)
        print("Dipendenze installate con successo")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'installazione delle dipendenze: {e}")
        sys.exit(1)

def create_configuration(args):
    """Crea il file di configurazione config.ini"""
    print("Creazione del file di configurazione...")
    
    config = configparser.ConfigParser()
    
    config['DATABASE'] = {
        'host': args.db_host,
        'user': args.db_user,
        'password': args.db_password,
        'database': args.db_name
    }
    
    config['FOLDERS'] = {
        'folder1': args.folder1,
        'folder2': args.folder2,
        'folder3': args.folder3
    }
    
    config['WEB'] = {
        'port': str(args.port),
        'debug': 'False'
    }
    
    with open('config.ini', 'w') as f:
        config.write(f)
    
    print("File di configurazione creato con successo")

def create_schema_file():
    """Crea il file schema.sql per il database"""
    print("Creazione del file schema.sql...")
    
    schema = """-- Schema per il database delle vendite
-- Tabella principale per i dati di vendita
CREATE TABLE IF NOT EXISTS vendite (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seq_id VARCHAR(255),
    period VARCHAR(10),
    natura VARCHAR(100),
    item_category VARCHAR(100),
    codice_dealer_agente VARCHAR(50),
    codice_negozio_cosy VARCHAR(50),
    cod_cliente VARCHAR(50),
    cliente VARCHAR(255),
    segmento_client VARCHAR(50),
    p_iva_cliente VARCHAR(50),
    fiscal_code VARCHAR(50),
    codice_contratto VARCHAR(50),
    dt_attivazione DATE,
    num_tel VARCHAR(50),
    imsi VARCHAR(50),
    piano_tariffario VARCHAR(50),
    descrizione_piano_tariffario VARCHAR(255),
    competenza VARCHAR(10),
    descrizione_evento VARCHAR(255),
    data_evento DATE,
    importo DECIMAL(10, 2),
    canale_vendita VARCHAR(100),
    codice_subagent VARCHAR(50),
    id_transazione VARCHAR(100),
    tipo_accesso VARCHAR(50),
    id_gara VARCHAR(50),
    numero_canali VARCHAR(50),
    causale_storno VARCHAR(255),
    tipo_linea VARCHAR(50),
    metodo_di_pagamento VARCHAR(100),
    mnp VARCHAR(5),
    mnp_interna VARCHAR(5),
    iccid VARCHAR(100),
    operatore_prov VARCHAR(50),
    operatore_recipient VARCHAR(50),
    nome_gara VARCHAR(255),
    id_opzione VARCHAR(50),
    brand VARCHAR(50),
    regola_di_calcolo VARCHAR(255),
    tipo_transazione VARCHAR(100),
    tipo_fonia VARCHAR(50),
    tipo_compenso VARCHAR(50),
    tipo_attivazione VARCHAR(50),
    descrizione_item VARCHAR(255),
    adjustment_comments TEXT,
    canone DECIMAL(10, 2),
    moltiplicatore DECIMAL(10, 2),
    tipo_gettone VARCHAR(50),
    flag_lineaattiva VARCHAR(5),
    flag_aggiuntivopiva VARCHAR(5),
    flag_safepayment VARCHAR(5),
    flag_convergenza VARCHAR(5),
    flag_windfamily VARCHAR(5),
    flag_presenzaopzioni VARCHAR(5),
    flag_soglia_fissa VARCHAR(50),
    flag_soglia_mobile VARCHAR(50),
    codice_pos_originario VARCHAR(50),
    flag_wind_security VARCHAR(5),
    cluster VARCHAR(100),
    numero_ultima_rata VARCHAR(50),
    id_contratto_sostituito VARCHAR(100),
    id_prodotto_sostituito VARCHAR(100),
    premio_mensilizzato_sostituito VARCHAR(100),
    churn_calcolato VARCHAR(50),
    data_firma DATE,
    flag_rinnovo VARCHAR(5),
    flag_silenzia VARCHAR(5),
    num_portato VARCHAR(50),
    cluster_cb VARCHAR(100),
    source_file VARCHAR(255),
    source_folder VARCHAR(255),
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_period (period),
    INDEX idx_codice_dealer (codice_dealer_agente),
    INDEX idx_cod_cliente (cod_cliente),
    INDEX idx_data_evento (data_evento),
    INDEX idx_natura (natura)
);

-- Tabella di log per tenere traccia delle importazioni
CREATE TABLE IF NOT EXISTS import_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    folder_path VARCHAR(255) NOT NULL,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_count INT DEFAULT 0,
    status ENUM('success', 'error', 'partial') NOT NULL,
    error_message TEXT,
    execution_time FLOAT
);
"""
    
    with open('schema.sql', 'w') as f:
        f.write(schema)
    
    print("File schema.sql creato con successo")

def create_startup_script():
    """Crea lo script di avvio per l'interfaccia web"""
    print("Creazione dello script di avvio...")
    
    if os.name == 'nt':  # Windows
        script = """@echo off
echo Avvio dell'interfaccia web per la gestione delle importazioni...
python web_interface.py
"""
        script_name = 'start.bat'
    else:  # Linux/Mac
        script = """#!/bin/bash
echo "Avvio dell'interfaccia web per la gestione delle importazioni..."
python3 web_interface.py
"""
        script_name = 'start.sh'
    
    with open(script_name, 'w') as f:
        f.write(script)
    
    # Rendi eseguibile lo script su Linux/Mac
    if os.name != 'nt':
        os.chmod(script_name, 0o755)
    
    print(f"Script di avvio '{script_name}' creato con successo")

def main():
    args = parse_arguments()
    
    print("=== Setup dell'interfaccia web per l'importazione dei file Excel ===")
    
    # Crea la struttura delle directory
    create_directory_structure()
    
    # Installa le dipendenze
    install_dependencies()
    
    # Crea il file di configurazione
    create_configuration(args)
    
    # Crea il file schema.sql
    create_schema_file()
    
    # Crea lo script di avvio
    create_startup_script()
    
    print("\nSetup completato con successo!")
    print("\nPer avviare l'interfaccia web, esegui:")
    if os.name == 'nt':
        print("  start.bat")
    else:
        print("  ./start.sh")
    
    print("\nPrima di utilizzare l'applicazione, assicurati di creare le tabelle nel database con:")
    print(f"  mysql -u {args.db_user} -p {args.db_name} < schema.sql")

if __name__ == "__main__":
    main()
