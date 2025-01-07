import shutil
import os
from datetime import datetime
import json
import logging
from pathlib import Path

class BackupService:
    def __init__(self, db_path: str, backup_dir: str):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.logger = logging.getLogger(__name__)
        
    def create_backup(self) -> str:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f'backup_{timestamp}')
            os.makedirs(backup_path, exist_ok=True)
            shutil.copy2(self.db_path, backup_path)
            metadata = {
                'timestamp': timestamp,
                'db_version': '1.0',
                'files': [os.path.basename(self.db_path)]
            }
            with open(os.path.join(backup_path, 'metadata.json'), 'w') as f:
                json.dump(metadata, f)
            self.logger.info(f'Backup created successfully at {backup_path}')
            return backup_path
        except Exception as e:
            self.logger.error(f'Backup creation failed: {str(e)}')
            raise

    def restore_from_backup(self, backup_path: str) -> bool:
        try:
            metadata_path = os.path.join(backup_path, 'metadata.json')
            if not os.path.exists(metadata_path):
                raise ValueError('Invalid backup: metadata.json not found')
            db_backup = os.path.join(backup_path, os.path.basename(self.db_path))
            shutil.copy2(db_backup, self.db_path)
            self.logger.info(f'Restore completed successfully from {backup_path}')
            return True
        except Exception as e:
            self.logger.error(f'Restore failed: {str(e)}')
            raise