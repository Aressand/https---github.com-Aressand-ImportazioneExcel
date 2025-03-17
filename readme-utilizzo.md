# Sistema di Importazione Vendite

Questo progetto consente di importare dati di vendita da file Excel in un database MySQL centralizzato. Il sistema è progettato per:
1. Importare inizialmente tutti i file Excel presenti in 3 cartelle specifiche
2. Importare mensilmente i 3 nuovi file Excel (uno per cartella)

## Requisiti

- Python 3.6 o superiore
- MySQL Server
- Librerie Python (installabili con pip):
  ```
  pip install pandas numpy mysql-connector-python tqdm openpyxl
  ```

## Configurazione del Database

Prima di utilizzare gli script, è necessario creare il database e le tabelle necessarie. Esegui il file SQL `database-schema.sql` sul tuo server MySQL:

```bash
mysql -u username -p database_name < database-schema.sql
```

## Struttura del Progetto

- `database-schema.sql` - Schema del database MySQL
- `import-script.py` - Script per l'importazione iniziale di tutti i file
- `monthly-import-script.py` - Script per l'importazione mensile dei nuovi file
- `import_excel.log` - Log delle importazioni iniziali
- `monthly_import.log` - Log delle importazioni mensili

## Utilizzo

### Importazione Iniziale

Per importare tutti i file Excel presenti nelle tre cartelle:

```bash
python import-script.py --user nome_utente --password password_mysql --database nome_database --folders /percorso/cartella1 /percorso/cartella2 /percorso/cartella3
```

Opzioni:
- `--host`: Host MySQL (default: localhost)
- `--user`: Nome utente MySQL
- `--password`: Password MySQL
- `--database`: Nome del database MySQL
- `--folders`: Elenco dei percorsi delle cartelle contenenti i file Excel (possono essere più di tre)

### Importazione Mensile

Per l'importazione mensile dei tre nuovi file (uno per cartella):

```bash
python monthly-import-script.py --user nome_utente --password password_mysql --database nome_database --folders /percorso/cartella1 /percorso/cartella2 /percorso/cartella3
```

Lo script selezionerà automaticamente il file più recente in ogni cartella.

In alternativa, è possibile specificare direttamente i file da importare:

```bash
python monthly-import-script.py --user nome_utente --password password_mysql --database nome_database --folders /percorso/cartella1 /percorso/cartella2 /percorso/cartella3 --files /percorso/file1.xlsx /percorso/file2.xlsx /percorso/file3.xlsx
```

## Automatizzazione

### Windows - Task Scheduler

Per eseguire automaticamente lo script ogni mese:

1. Crea un file batch (.bat) con il comando:
   ```batch
   @echo off
   cd /d C:\percorso\al\progetto
   python monthly-import-script.py --user nome_utente --password password_mysql --database nome_database --folders C:\percorso\cartella1 C:\percorso\cartella2 C:\percorso\cartella3
   ```

2. Apri Task Scheduler
3. Crea un nuovo task pianificato per eseguire il file batch mensilmente

### Linux/macOS - Crontab

Per eseguire automaticamente lo script ogni mese:

1. Modifica il crontab:
   ```bash
   crontab -e
   ```

2. Aggiungi una riga per eseguire lo script il primo giorno di ogni mese:
   ```
   0 0 1 * * /usr/bin/python3 /percorso/al/monthly-import-script.py --user nome_utente --password password_mysql --database nome_database --folders /percorso/cartella1 /percorso/cartella2 /percorso/cartella3
   ```

## Monitoraggio

Per verificare lo stato delle importazioni, puoi consultare la tabella `import_log` nel database:

```sql
SELECT * FROM import_log ORDER BY import_date DESC LIMIT 10;
```

I file di log `import_excel.log` e `monthly_import.log` contengono informazioni dettagliate sulle operazioni di importazione.

## Note Importanti

- Lo script importa solo file con estensione `.xlsx`
- La struttura del file Excel deve corrispondere allo schema di tabella definito
- È consigliabile eseguire prima un backup del database prima di importazioni di grandi dimensioni
- La tabella `vendite` è indicizzata per migliorare le prestazioni delle query
