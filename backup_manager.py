import os
import sqlite3

class BackupManager:
    """This class is responsible for managing the backup files and directories."""
    def __init__(self, backup_dir):
        self.__backup_dir = backup_dir
        self.__all_backups = []
        self.search_backups()
        self.backups_files = [[] * len(self.__all_backups)]

    def search_backups(self):
        if os.path.exists(self.__backup_dir):
            self.__all_backups = [folder for folder in os.listdir(self.__backup_dir) if os.path.exists(
                os.path.join(self.__backup_dir, folder, 'Manifest.plist'))]

    def list_backups(self):
        if not self.__all_backups:
            return None
        else:
            return self.__all_backups

    def list_backup_files(self, backup_id):
        if not self.__all_backups[backup_id]:
            return None
        # Connect to the Manifest.db file
        conn = sqlite3.connect(os.path.join(self.__backup_dir, self.__all_backups[backup_id], "Manifest.db"))

        # Get a cursor object
        cursor = conn.cursor()

        # Execute a query to get information about the files in the backup
        cursor.execute('SELECT * FROM Files')

        # Store all information about files for further usage
        self.backups_files[backup_id] = cursor.fetchall()

        # Iterate over the results and get out information about each file
        files = [f"{row[2]}" for row in self.backups_files[backup_id]]

        return files

    def get_file_path(self, backup_id, file_id: int):
        return os.path.join(self.__backup_dir, self.__all_backups[backup_id],
                            self.backups_files[backup_id][file_id][0][:2], self.backups_files[backup_id][file_id][0])