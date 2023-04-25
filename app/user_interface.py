import argparse

from backup_manager import BackupManager
from backup_extractor import BackupExtractor
from data_manager import DataManager


class UserInterface:
    def __init__(self):
        self.backup_manager = None
        self.backup_extractor = None
        self.data_manager = DataManager()

    def run(self):
        global backup_id
        parser = argparse.ArgumentParser(prog='ibe')
        subparsers = parser.add_subparsers(dest='command')

        # Backup search command
        search_parser = subparsers.add_parser('search', help='Search for backups in the specified path')
        search_parser.add_argument('-p', '--search-path', type=str, help='Path to search for backups')
        search_parser.add_argument('-l', action='store_true', help='include full path in listing output')

        # Backup info command
        info_parser = subparsers.add_parser('info', help='Get info on a specific backup')
        info_parser.add_argument('-p', '--path', type=str, help='Path to the backup')
        info_parser.add_argument('-id', type=int, help='ID of the backup')

        # Backup list command
        list_parser = subparsers.add_parser('list', help='List files in a specific backup')
        list_parser.add_argument('-p', '--path', type=str, help='path to the backup')
        list_parser.add_argument('-id', type=int, help='ID of the backup')

        # Backup export command
        export_parser = subparsers.add_parser('export', help='Export file to destination path')
        export_parser.add_argument('-p', '--path', type=str, help='path to the backup')
        export_parser.add_argument('-id', type=int, help='ID of the backup')
        export_parser.add_argument('-f', '--filename', type=str, help='File name')
        export_parser.add_argument('-fid', '--fileId', type=str, help='File Id')
        export_parser.add_argument('-d', '--dest-path', type=str, help='Destination path of the backup')

        # Backup export all command
        export_all_parser = subparsers.add_parser('export all',
                                                  help='Export all files of a category to destination path')
        export_all_parser.add_argument('-p', '--path', type=str, help='path to the backup')
        export_all_parser.add_argument('-id', type=int, help='ID of the backup')
        export_all_parser.add_argument('-d', '--dest-path', type=str, help='Destination path of the backup')
        export_all_parser.add_argument('-photos', action='store_true', help='Export all photos from Camera Roll')
        export_all_parser.add_argument('-videos', action='store_true', help='Export all videos from Camera Roll')
        export_all_parser.add_argument('-contacts', action='store_true', help='Export all contacts')
        export_all_parser.add_argument('-sms', action='store_true', help='Export all sms')
        export_all_parser.add_argument('-calendar', action='store_true', help='Export all calendar events')
        export_all_parser.add_argument('-web', '--web-history', action='store_true', help='Export web history')
        export_all_parser.add_argument('-notes', action='store_true', help='Export all notes')
        export_all_parser.add_argument('-call', '--call-history', action='store_true', help='Export call history')

        args = parser.parse_args()

        if args.command == 'search':
            self.backup_manager = BackupManager(args.search_path)
            self.backup_manager.search_backups()
            backups = self.backup_manager.list_backups()

            l = max(len(s) for s in backups) + len(args.search_path) if args.l else max(len(s) for s in backups)
            print(f"Number of backups found: {len(backups)}")
            print("-----" + "-" * l)
            print("ID |   ", "Full path" if args.l else "FolderName")
            print("-----" + "-" * l)

            if args.l:
                for i, backup in enumerate(backups):
                    print(f"{i} : {args.search_path}\{backup}")
                    print("-----" + "-" * l)
            else:
                for i, backup in enumerate(backups):
                    print(f"{i} : {backup}")
                    print("-----" + "-" * l)

        elif args.command == 'info':
            if args.path:
                self.backup_extractor = BackupExtractor(args.path)
            elif args.id:
                pass
            metadata = self.backup_extractor.get_metadata()
            unnecessary = ['Lockdown', 'BackupKeyBag', 'Applications', 'iTunes Files',
                           'iTunes Settings', 'Target Type', 'iBooks Data 2']
            for i in metadata.keys():
                for j in metadata[i]:
                    if j in unnecessary:
                        continue
                    elif j == 'Installed Applications':
                        print(j, end=": ")
                        for app in metadata[i][j]:
                            print(app.split(".")[-1], end=", ")
                        print()
                    else:
                        print(j, ": ", metadata[i][j])

        elif args.command == 'list':
            if args.path:
                self.backup_manager = BackupManager(args.path)
            elif args.id:
                pass
            files = self.backup_manager.list_backup_files(args.path)
            for file in files:
                print(file)

        '''elif args.command == 'backup export':
            self.backup_manager.init(args.search_path)
            backup_id = self.backup_manager.select_backup()
        if backup_id:
            self.backup_extractor.init(self.backup_manager.get_file_path(backup_id))
            self.data_manager.export_photos(args.d)
            self.data_manager.export_videos(args.d)
            self.data_manager.export_contacts(args.d)
            self.data_manager.export_sms(args.d)
            self.data_manager.export_calendar(args.d)
            self.data_manager.export_web_history(args.d)
            self.data_manager.export_notes(args.d)
            self.data_manager.export_call_history(args.d)

        else:
            parser.print_help()

    def help(self):
        print('Commands:')
        print('list - List files within an iOS backup')
        print('get_info - Get info and metadata from local iOS backups')
        print('export - Export data from an iOS backup to a destination folder')

    def list(self):
        self.backup_extractor.list_files()

    def get_info(self):
        self.backup_extractor.get_backup_info()

    def export(self):
        destination = input('Enter destination folder: ')
        self.data_manager.export_backup(destination)'''


if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
