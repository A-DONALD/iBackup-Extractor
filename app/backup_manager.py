import os
import sqlite3

class BackupManager:
    """This class is responsible for managing the backup files and directories."""
    def __init__(self, backup_dir):
        self.__backup_dir = backup_dir
        self.__all_backups = []
        self.search_backups()
        # under array that we use for each backup file to save the information
        self.backups_files = [[None]] * len(self.__all_backups)

    def search_backups(self):
        if os.path.exists(self.__backup_dir):
            # search folder by folder in the localisation of backup and verify that we have a file manifest.plist
            self.__all_backups = [folder for folder in os.listdir(self.__backup_dir) if os.path.exists(
                os.path.join(self.__backup_dir, folder, 'Manifest.plist'))]
        return None

    def list_backups(self):
        if not self.__all_backups:
            return None
        else:
            return self.__all_backups

    def list_backup_files(self, backup_id):
        if isinstance(backup_id, int):
            if not self.__all_backups[backup_id]:
                return None
            path = os.path.join(self.__backup_dir, self.__all_backups[backup_id])
        elif isinstance(backup_id, str):
            path = backup_id
        # Connect to the Manifest.db file
        conn = sqlite3.connect(os.path.join(path, "Manifest.db"))

        # Get a cursor object
        cursor = conn.cursor()

        # Execute a query to get information about the files in the backup
        cursor.execute('SELECT * FROM Files')

        # Store all information about files for further usage
        result = cursor.fetchall()

        # Iterate over the results and get out information about each file
        files = [f"{row[1]}/{row[2]}" for row in result]

        if isinstance(backup_id, int):
            self.backups_files[backup_id] = result

        return files

    def get_file_path(self, backup_id, file):
        file_id = None
        if isinstance(file, str):
            for i in range(len(self.backups_files[backup_id])):
                if f"{self.backups_files[backup_id][i][1]}/{self.backups_files[backup_id][i][2]}" == file:
                    file_id = i
                    break
                elif f"{self.backups_files[backup_id][i][2]}" == file:
                    file_id = i
        elif isinstance(file, int):
            file_id = file
        else:
            return None
        if file_id: return os.path.join(self.__backup_dir, self.__all_backups[backup_id],
                            self.backups_files[backup_id][file_id][0][:2], self.backups_files[backup_id][file_id][0])
        return None