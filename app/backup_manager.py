import os
import sqlite3

class BackupManager:
    """This class is responsible for managing the backup files and directories."""
    def __init__(self, backup_dir):
        self.__backup_dir = backup_dir
        self.__all_backups = []
        self.search_backups()
        # under array that we use for each backup file to save the information
        self.backups_files = [[] * len(self.__all_backups)]

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
        files = [f"{row[1]}/{row[2]}" for row in self.backups_files[backup_id]]

        return files

    def get_file_path(self, backup_id, file):
        file_id = None
        if isinstance(file, str):
            for i in range(len(self.backups_files[backup_id])):
                if f"{self.backups_files[backup_id][i][1]}/{self.backups_files[backup_id][i][2]}" == file:
                    file_id = i
                    break
        elif isinstance(file, int):
            file_id = file
        return os.path.join(self.__backup_dir, self.__all_backups[backup_id],
                            self.backups_files[backup_id][file_id][0][:2], self.backups_files[backup_id][file_id][0])