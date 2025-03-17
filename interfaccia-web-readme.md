# Interfaccia Web per Importazione File Excel

Questa applicazione fornisce un'interfaccia web completa per gestire l'importazione di file Excel in un database MySQL centralizzato. L'interfaccia permette di eseguire, monitorare e tenere traccia di tutte le operazioni di importazione.

## Caratteristiche principali

- **Dashboard**: Visualizzazione delle statistiche principali e grafici
- **Importazione facilitata**: Interfaccia grafica per l'importazione iniziale e mensile
- **Monitoraggio in tempo reale**: Visualizzazione dello stato dei processi in esecuzione
- **Storico importazioni**: Elenco completo di tutte le importazioni effettuate
- **Configurazione semplice**: Gestione delle impostazioni di database e cartelle

## Requisiti di sistema

- Python 3.6 o superiore
- MySQL Server
- Web browser moderno

## Installazione

### 1. Clona o scarica il progetto

```bash
git clone [url-repository]
cd [directory-progetto]
```

### 2. Esegui lo script di setup

```bash
python setup-web-interface.py --db-user nome_utente --db-password password_mysql --db-name nome_database --folder1 /percorso/cartella1 --folder2 /percorso/cartella2 --folder3 /percorso/cartella3
```

Parametri disponibili:
- `--db-host`: Host del database MySQL (default: localhost)
- `--db-user`: Nome utente MySQL
- `--db-password`: Password MySQL
- `--db-name`: Nome del database MySQL
- `--folder1`: Percorso della prima cartella
- `--folder2`: Percorso della seconda cartella
- `--folder3`: Percorso della terza cartella
- `--port`: Porta su cui eseguire l'applicazione web (default: 5000)

### 3. Crea le tabelle nel database

```bash
mysql -u nome_utente -p nome_database < schema.sql
```

### 4. Avvia l'applicazione

Su Windows:
```
start.bat
```

Su Linux/macOS:
```
./start.sh
```

L'interfaccia web sarà disponibile all'indirizzo `http://localhost:5000`

## Struttura dell'interfaccia

### Dashboard
La dashboard fornisce una panoramica delle statistiche principali:
- Numero totale di righe nel database
- Importo totale
- Grafici di distribuzione per periodo e natura
- Pulsanti per azioni rapide

### Nuova Importazione
Permette di avviare nuove importazioni con tre modalità:
- **Importazione Iniziale**: Importa tutti i file Excel presenti nelle 3 cartelle configurate
- **Importazione Mensile**: Importa automaticamente i 3 file più recenti (uno per cartella)
- **File Specifici**: Permette di specificare manualmente i 3 file da importare

### Storico Importazioni
Visualizza un elenco completo di tutte le importazioni effettuate con:
- Nome file e cartella
- Data e ora di importazione
- Numero di righe importate
- Stato (successo, errore, parziale)
- Tempo di esecuzione
- Dettagli degli errori (se presenti)

### Processi Attivi
Mostra lo stato di tutti i processi di importazione in esecuzione o completati:
- Tipo di importazione
- Stato attuale
- Orario di inizio e fine
- Link alla pagina di dettaglio con output in tempo reale

### Configurazione
Permette di gestire:
- Impostazioni di connessione al database MySQL
- Percorsi delle cartelle contenenti i file Excel
- Test di connessione al database e accessibilità delle cartelle

## Personalizzazione
È possibile personalizzare l'interfaccia web modificando i seguenti file:
- `config.ini`: Configurazione generale dell'applicazione
- `templates/`: File HTML per le pagine dell'interfaccia
- `static/`: File CSS e JavaScript per lo stile e le funzionalità aggiuntive

## Risoluzione problemi

### Errori di connessione al database
1. Verifica che il server MySQL sia in esecuzione
2. Controlla le credenziali nel file `config.ini`
3. Assicurati che il database esista e che l'utente abbia i permessi necessari

### Errori di importazione
1. Verifica che le cartelle configurate siano accessibili
2. Controlla che i file Excel abbiano l'estensione `.xlsx`
3. Assicurati che la struttura dei file sia compatibile con lo schema del database

### Problemi con l'interfaccia web
1. Controlla i log dell'applicazione in `web_interface.log`
2. Verifica che la porta configurata (default: 5000) sia disponibile
3. Assicurati di utilizzare un browser web aggiornato

## Supporto
Per assistenza o segnalazione di problemi, contatta l'amministratore di sistema.
