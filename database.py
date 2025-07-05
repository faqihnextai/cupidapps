import mysql.connector
from mysql.connector import errorcode

# Konfigurasi database MySQL
# Ganti dengan kredensial database MySQL kamu
DB_CONFIG = {
    'user': 'root',        # Ganti dengan username MySQL Anda
    'password': '',    # Ganti dengan password MySQL Anda
    'host': 'localhost',                  # Atau 'localhost', atau IP server MySQL Anda
    'database': 'cupit_series_db'         # Nama database yang akan digunakan
}

def get_db_connection():
    """Membuat dan mengembalikan koneksi ke database MySQL."""
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Ada yang salah dengan username atau password MySQL Anda.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database tidak ada. Pastikan database 'cupit_series_db' sudah dibuat.")
        else:
            print(err)
        return None

def create_tables():
    """Membuat tabel 'otps' dan 'users' di database."""
    cnx = get_db_connection()
    if not cnx:
        print("Tidak dapat terhubung ke database untuk membuat tabel.")
        return

    cursor = cnx.cursor()

    tables = {}
    tables['otps'] = (
        """
        CREATE TABLE IF NOT EXISTS otps (
            id INT AUTO_INCREMENT PRIMARY KEY,
            otp_code VARCHAR(6) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            is_used BOOLEAN DEFAULT FALSE
        );
        """
    )
    tables['users'] = (
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            instagram_username VARCHAR(255) NOT NULL,
            gender VARCHAR(50) NOT NULL,
            age_range VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    for table_name in tables:
        table_description = tables[table_name]
        try:
            print(f"Membuat tabel {table_name}: ", end='')
            cursor.execute(table_description)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("sudah ada.")
            else:
                print(err.msg)
    
    cursor.close()
    cnx.close()

if __name__ == '__main__':
    # Pastikan database 'cupit_series_db' sudah dibuat di MySQL Anda
    # Anda bisa membuatnya secara manual di phpMyAdmin atau MySQL Workbench,
    # atau dengan perintah SQL: CREATE DATABASE cupit_series_db;
    create_tables()
    print("Proses pembuatan tabel selesai.")