#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interfaccia web per la gestione delle importazioni dei file Excel nel database MySQL.
"""

import os
import sys
import subprocess
import threading
import json
import logging
import configparser
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_interface.log'),
        logging.StreamHandler()
    ]
)

# Percorso del file di configurazione
CONFIG_FILE = 'config.ini'

# Dizionario per tenere traccia dei processi in esecuzione
running_processes = {}

def load_config():
    """Carica la configurazione dal file config.ini"""
    config = configparser.ConfigParser()
    
    # Se il file di configurazione non esiste, crea uno con valori predefiniti
    if not os.path.exists(CONFIG_FILE):
        config['DATABASE'] = {
            'host': 'localhost',
            'user': '',
            'password': '',
            'database': ''
        }
        config['FOLDERS'] = {
            'import_folder': ''
        }
        config['WEB'] = {
            'port': '5000',
            'debug': 'False'
        }
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    else:
        config.read(CONFIG_FILE)
    
    # Assicurati che tutte le sezioni esistano
    if 'DATABASE' not in config:
        config['DATABASE'] = {}
    if 'FOLDERS' not in config:
        config['FOLDERS'] = {}
    if 'WEB' not in config:
        config['WEB'] = {}
    
    # Assicurati che tutti i parametri esistano con valori predefiniti
    if 'host' not in config['DATABASE']:
        config['DATABASE']['host'] = 'localhost'
    if 'user' not in config['DATABASE']:
        config['DATABASE']['user'] = ''
    if 'password' not in config['DATABASE']:
        config['DATABASE']['password'] = ''
    if 'database' not in config['DATABASE']:
        config['DATABASE']['database'] = ''
    
    if 'import_folder' not in config['FOLDERS']:
        config['FOLDERS']['import_folder'] = ''
    
    if 'port' not in config['WEB']:
        config['WEB']['port'] = '5000'
    if 'debug' not in config['WEB']:
        config['WEB']['debug'] = 'False'
    
    return config

def save_config(config_data):
    """Salva la configurazione nel file config.ini"""
    config = configparser.ConfigParser()
    
    # Leggi il file di configurazione esistente per mantenere le sezioni non modificate
    config.read(CONFIG_FILE)
    
    # Aggiorna la sezione DATABASE
    if 'DATABASE' not in config:
        config['DATABASE'] = {}
    config['DATABASE']['host'] = config_data.get('db_host', 'localhost')
    config['DATABASE']['user'] = config_data.get('db_user', '')
    config['DATABASE']['password'] = config_data.get('db_password', '')
    config['DATABASE']['database'] = config_data.get('db_name', '')
    
    # Aggiorna la sezione FOLDERS
    if 'FOLDERS' not in config:
        config['FOLDERS'] = {}
    config['FOLDERS']['import_folder'] = config_data.get('import_folder', '')
    
    # Mantieni la sezione WEB se esiste
    if 'WEB' not in config:
        config['WEB'] = {}
        config['WEB']['port'] = '5000'
        config['WEB']['debug'] = 'False'
    
    # Salva il file
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

def get_db_connection():
    """Crea una connessione al database MySQL"""
    config = load_config()
    
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=config['DATABASE']['host'],
            user=config['DATABASE']['user'],
            password=config['DATABASE']['password'],
            database=config['DATABASE']['database']
        )
        return conn
    except Exception as e:
        logging.error(f"Errore di connessione al database: {e}")
        return None

def run_import_script(process_id, import_type, command):
    """Esegue lo script di importazione in un thread separato"""
    # Inizializza lo stato del processo
    running_processes[process_id] = {
        'status': 'running',
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': import_type,
        'command': ' '.join(command),
        'output': []
    }
    
    # Funzione che verrà eseguita in un thread separato
    def run_process():
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Leggi l'output in tempo reale
            while True:
                output_line = process.stdout.readline()
                if output_line == '' and process.poll() is not None:
                    break
                if output_line:
                    running_processes[process_id]['output'].append(output_line.strip())
            
            # Leggi eventuali errori
            stderr = process.stderr.read()
            if stderr:
                running_processes[process_id]['output'].append(f"ERRORI: {stderr}")
            
            # Aggiorna lo stato finale
            return_code = process.poll()
            if return_code == 0:
                running_processes[process_id]['status'] = 'completed'
            else:
                running_processes[process_id]['status'] = 'failed'
            
            running_processes[process_id]['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            running_processes[process_id]['return_code'] = return_code
            
        except Exception as e:
            running_processes[process_id]['status'] = 'failed'
            running_processes[process_id]['output'].append(f"ERRORE: {str(e)}")
            running_processes[process_id]['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Avvia il thread
    thread = threading.Thread(target=run_process)
    thread.daemon = True
    thread.start()

def get_database_stats():
    """Recupera statistiche dal database"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    stats = {}
    
    try:
        cursor = conn.cursor()
        
        # Conteggio totale delle righe
        cursor.execute("SELECT COUNT(*) FROM fatture_totali")
        stats['total_rows'] = cursor.fetchone()[0]
        
        # Importo totale
        cursor.execute("SELECT SUM(importo) FROM fatture_totali")
        stats['total_amount'] = cursor.fetchone()[0] or 0
        
        return stats
    except Exception as e:
        logging.error(f"Errore nel recupero delle statistiche: {e}")
        return {'total_rows': 0, 'total_amount': 0}
    finally:
        if conn:
            conn.close()

def get_import_history(limit=100):
    """Recupera lo storico delle importazioni dal database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT id, filename, folder_path, import_date, row_count, status, error_message, execution_time
        FROM import_log
        ORDER BY import_date DESC
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        logging.error(f"Errore nel recupero dello storico importazioni: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Inizializzazione dell'app Flask
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Cambia questa chiave in produzione

@app.route('/')
def index():
    """Pagina principale (dashboard)"""
    stats = get_database_stats()
    return render_template('index.html', stats=stats)

@app.route('/nuova-importazione', methods=['GET', 'POST'])
def new_import():
    """Pagina per avviare una nuova importazione"""
    if request.method == 'POST':
        import_type = request.form.get('import_type')
        
        # Genera un ID univoco per questo processo
        process_id = f"{import_type}_{int(time.time())}"
        
        # Carica la configurazione
        config = load_config()
        
        if import_type == 'folder':
            # Importazione dalla cartella completa
            folder = config['FOLDERS']['import_folder']
            command = [ sys.executable, 'import-script.py', 
                      '--user', config['DATABASE']['user'], 
                      '--password', config['DATABASE']['password'], 
                      '--database', config['DATABASE']['database'], 
                      '--folder', folder]
            
            run_import_script(process_id, import_type, command)
            flash('Importazione dalla cartella avviata con successo', 'success')
            
        elif import_type == 'file':
            # Importazione di un file specifico
            file_path = request.form.get('file_path', '')
            
            if not file_path:
                flash('Devi specificare un file', 'error')
                return render_template('new_import.html')
            
            command = [ sys.executable, 'import-script.py', 
                      '--user', config['DATABASE']['user'], 
                      '--password', config['DATABASE']['password'], 
                      '--database', config['DATABASE']['database'], 
                      '--file', file_path]
            
            run_import_script(process_id, import_type, command)
            flash('Importazione del file specifico avviata con successo', 'success')
        
        # Reindirizza alla pagina di stato del processo
        return redirect(url_for('process_status', process_id=process_id))
        
    # Se è una richiesta GET, mostra il template
    return render_template('new_import.html')

@app.route('/importazioni')
def import_history():
    """Pagina per visualizzare lo storico delle importazioni"""
    history = get_import_history()
    return render_template('import_history.html', history=history)

@app.route('/stato-processi')
def processes():
    """Pagina per visualizzare i processi attivi"""
    return render_template('processes.html', processes=running_processes)

@app.route('/stato-processo/<process_id>')
def process_status(process_id):
    """Pagina per visualizzare lo stato di un processo specifico"""
    if process_id not in running_processes:
        flash(f'Processo {process_id} non trovato', 'error')
        return redirect(url_for('processes'))
    
    return render_template('process_status.html', 
                           process=running_processes[process_id], 
                           process_id=process_id)

@app.route('/configurazione', methods=['GET', 'POST'])
def configuration():
    """Pagina di configurazione"""
    if request.method == 'POST':
        config_data = {
            'db_host': request.form.get('db_host'),
            'db_user': request.form.get('db_user'),
            'db_password': request.form.get('db_password'),
            'db_name': request.form.get('db_name'),
            'import_folder': request.form.get('import_folder')
        }
        save_config(config_data)
        flash('Configurazione salvata con successo', 'success')
        return redirect(url_for('configuration'))
    
    config = load_config()
    return render_template('configuration.html', config=config)

@app.route('/api/processi')
def api_processes():
    """API per ottenere lo stato di tutti i processi"""
    return jsonify(running_processes)

@app.route('/api/processo/<process_id>')
def api_process_status(process_id):
    """API per ottenere lo stato di un processo specifico"""
    if process_id not in running_processes:
        return jsonify({'error': 'Processo non trovato'}), 404
    
    return jsonify(running_processes[process_id])

@app.route('/api/stats')
def api_stats():
    """API per ottenere le statistiche del database"""
    return jsonify(get_database_stats())

@app.route('/api/history')
def api_history():
    """API per ottenere lo storico delle importazioni"""
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_import_history(limit))

if __name__ == '__main__':
    # Carica la configurazione
    config = load_config()
    
    # Avvia l'applicazione Flask
    port = int(config['WEB'].get('port', 5000))
    debug = config['WEB'].get('debug', 'False').lower() == 'true'
    
    app.run(debug=debug, host='0.0.0.0', port=port)