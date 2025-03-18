# Sistema di Importazione Dati Excel in MySQL

Un'applicazione web Python per importare, gestire e monitorare dati da file Excel in un database MySQL centralizzato.

## 📋 Caratteristiche

- Importazione di file Excel singoli o di intere cartelle
- Importazione mensile di nuovi file
- Dashboard interattiva per visualizzare statistiche
- Monitoraggio in tempo reale dei processi di importazione
- Storico completo delle importazioni effettuate
- Configurazione facile tramite interfaccia web

## 🔧 Prerequisiti

- Python 3.6 o superiore
- MySQL Server
- Browser web moderno

## 📦 Librerie Python richieste

```
pandas
numpy
mysql-connector-python
tqdm
openpyxl
flask
```

## 🚀 Installazione

1. Clona il repository:
   ```bash
   git clone https://github.com/tuousername/excel-import-system.git
   cd excel-import-system
   ```

2. Crea e attiva un ambiente virtuale:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

4. Crea il database MySQL:
   ```bash
   mysql -u root -p
   ```
   ```sql
   CREATE DATABASE importazioni_excel;
   ```

5. Crea le tabelle necessarie:
   ```bash
   mysql -u root -p importazioni_excel < database-schema.sql
   ```

6. Configura l'applicazione modificando il file `config.ini` con i tuoi dati:
   ```ini
   [DATABASE]
   host = localhost
   user = tuousername
   password = tuapassword
   database = importazioni_excel

   [FOLDERS]
   import_folder = /percorso/alla/tua/cartella

   [WEB]
   port = 5000
   debug = False
   ```

## 💻 Utilizzo

### Avviare l'interfaccia web

```bash
python web-interface.py
```

Poi apri un browser e vai a `http://localhost:5000`

### Importazione iniziale di tutti i file

Per importare tutti i file Excel presenti in una cartella:

1. Vai alla pagina "Nuova Importazione"
2. Seleziona "Importazione Cartella"
3. Fai clic su "Avvia Importazione"

### Importazione di un file specifico

1. Vai alla pagina "Nuova Importazione"
2. Seleziona "File Specifico"
3. Inserisci il percorso completo del file
4. Fai clic su "Avvia Importazione"

### Importazione mensile

Per importare i nuovi file mensili:

1. Vai alla pagina "Nuova Importazione"
2. Seleziona "Importazione Cartella" (assicurati che la cartella configurata contenga i nuovi file mensili)
3. Fai clic su "Avvia Importazione"

## 📊 Struttura del progetto

```
excel-import-system/
├── database-schema.sql        # Schema del database
├── import-script.py           # Script per l'importazione singola
├── monthly-import-script.py   # Script per l'importazione mensile
├── web-interface.py           # Interfaccia web per la gestione
├── config.ini                 # File di configurazione
├── templates/                 # Template HTML per l'interfaccia web
├── requirements.txt           # Dipendenze Python
└── README.md                  # Questo file
```

## ⚠️ Note importanti

- L'importazione di grandi volumi di file (>10) potrebbe richiedere molto tempo e risorse
- Si consiglia di importare file in batch più piccoli per evitare problemi di memoria
- Assicurati di avere backup regolari del database
- I file di log possono essere eliminati periodicamente senza problemi

## 🔍 Risoluzione dei problemi

### Errore "No module named 'pandas'"

Assicurati che:
1. L'ambiente virtuale sia attivato
2. Le dipendenze siano installate: `pip install -r requirements.txt`
3. Se usi l'interfaccia web, modificare `web-interface.py` per utilizzare `sys.executable` invece di `python`

### Errore "Table doesn't exist"

Esegui lo script SQL per creare le tabelle:
```bash
mysql -u root -p importazioni_excel < database-schema.sql
```

### L'importazione si blocca dopo alcuni file

1. Prova a importare meno file alla volta
2. Assicurati di avere sufficiente memoria disponibile
3. Verifica che i file Excel siano validi e non corrotti

## 📝 Licenza

[MIT](LICENSE)

## 👤 Autori

- Il tuo nome

## 🙏 Ringraziamenti

Questo progetto è stato creato per semplificare il flusso di lavoro di importazione dati ed è in continua evoluzione.
