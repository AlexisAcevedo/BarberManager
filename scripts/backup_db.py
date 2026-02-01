"""
Script de respaldo automatizado para la base de datos de Barber Manager.
Crea copias de 'barber_manager.db' en el directorio 'backups/' con estampa de tiempo.
"""
import os
import shutil
import logging
from datetime import datetime

# Configuración
DB_FILE = "barber_manager.db"
BACKUP_DIR = "backups"
MAX_BACKUPS = 10  # Rotación: mantener los últimos 10 backups

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("backup_script")

def ensure_backup_dir():
    """Crea el directorio de backups si no existe."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logger.info(f"Directorio creado: {BACKUP_DIR}")

def create_backup():
    """Crea una copia de la base de datos actual."""
    if not os.path.exists(DB_FILE):
        logger.error(f"No se encontró la base de datos: {DB_FILE}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"barber_manager_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    try:
        shutil.copy2(DB_FILE, backup_path)
        logger.info(f"Backup creado exitosamente: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return None

def rotate_backups():
    """Mantiene solo los backups más recientes según MAX_BACKUPS."""
    try:
        backups = sorted(
            [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".db")],
            key=os.path.getmtime,
            reverse=True
        )

        if len(backups) > MAX_BACKUPS:
            to_delete = backups[MAX_BACKUPS:]
            for backup in to_delete:
                os.remove(backup)
                logger.info(f"Backup antiguo eliminado por rotación: {backup}")
    except Exception as e:
        logger.error(f"Error rotando backups: {e}")

def main():
    logger.info("Iniciando proceso de backup...")
    ensure_backup_dir()
    if create_backup():
        rotate_backups()
    logger.info("Proceso finalizado.")

if __name__ == "__main__":
    main()
