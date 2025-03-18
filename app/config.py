import pyodbc

# Configuração do SQL Server
DB_CONFIG = {
    'server': 'DESKTOP-TOMAS',
    'database': 'BCMMANAGER_DB',
    'username': 'sa',
    'password': 'coruja30',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def conectar_banco():
    conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"
    return pyodbc.connect(conn_str)