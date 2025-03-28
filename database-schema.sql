-- Schema per il database delle vendite
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
