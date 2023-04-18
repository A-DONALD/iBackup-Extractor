from app.backup_manager import BackupManager

class Backupmanagertest :
    # Create a BackupManager object
    def test1 (self):
        test1 = BackupManager('C:\\Users\\kamde\\OneDrive\\Bureau\\Erasmus Course\\ZSWIE')

        # List all backups
        backups = test1.list_backups()
        print('Backups:', backups)

        # List all files in the first backup
        if backups:
            backup_id = 0
            backup_files = test1.list_backup_files(backup_id)
            print(f'Files in backup {backup_id}:', backup_files)

            # Get the path of a file in the backup
            if backup_files:
                file_id = 0
                file_path = test1.get_file_path(backup_id, backup_files[file_id])
                print(f'Path of file {backup_files[file_id]}:', file_path)

test = Backupmanagertest()
test.test1()
