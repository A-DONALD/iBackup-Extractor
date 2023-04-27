import argparse
import os
from backup_manager import BackupManager
from backup_extractor import BackupExtractor
from data_manager import DataManager


class UserInterface:
    def __init__(self):
        self.backup_manager = None
        self.backup_extractor = None
        self.data_manager = DataManager()
        self.commands = """Commands:
                                    \tsearch - Search for backups in the specified path
                                             -p --path : Path to the backup
                                             -l : include full path in listing output
                                    \tinfo - Get info and metadata from local iOS backups
                                            -p --path : Path to the backup
                                    \tlist - List files within an iOS backup
                                            -p --path : Path to the backup
                                            -c : Category of the wanted file
                                            -f --format : format of list. Print by set of "f"        
                                    \texport - Export data from an iOS backup to a destination folder
                                            -p --path : Path to the backup
                                            -d -dest-path : Path to the backup
                                            -c --category : Category of the files to export
                                    \t available categories : photos, videos, contacts, sms, calendar, call
                                    """

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
        list_parser.add_argument('-f', '--format', type=int, help='format of list. Print by set of "f"')
        list_parser.add_argument('-c', '--category', type=str, help='Category of the file to extract')

        # Backup export command
        export_parser = subparsers.add_parser('export', help='Export file to destination path')
        export_parser.add_argument('-p', '--path', type=str, help='path to the backup')
        export_parser.add_argument('-id', type=int, help='ID of the backup')
        export_parser.add_argument('-f', '--filename', type=str, help='File name')
        export_parser.add_argument('-fid', '--fileId', type=str, help='File Id')
        export_parser.add_argument('-d', '--dest-path', type=str, help='Destination path of the backup')
        export_parser.add_argument('-c', '--category', type=str, help='Category of the files to export')
        args = parser.parse_args()

        if args.command == 'search':
            if not args.path:
                print("Please provide the path for the search")
                print(self.commands)
                return
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
            if not args.path:
                print("Please provide the path to the backup")
                return
            elif args.path:
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
            if not args.path:
                print("Please provide the path to the backup")
                return
            print("Extracting...")
            files = []
            if args.path:
                self.backup_manager = BackupManager(args.path)
            elif args.id:
                pass
            if args.category:
                self.backup_extractor = BackupExtractor(args.path)
                match args.category:
                    case "photos":
                        files = [file[1] for file in self.backup_extractor.extract_photos(include_path=False)]
                    case "videos":
                        files = self.backup_extractor.extract_videos(include_path=False)
                    case "contacts":
                        files = self.backup_extractor.extract_contacts()[1]
                        print(files)
                        files = [f'Name : {file[0]} {file[1] if file[1] else ""}\n ' \
                                 f'Number : {file[11].split(" ")[0] if file[11] else (file[10] if file[10] else file[12])}, ' \
                                 f'Email : {file[13]}\n ' \
                                 f'Organization : {file[2]}\n Department : {file[3]}\n ' \
                                 f'Birthday : {file[4]}\n Created : {file[8]}, Last time modified : {file[9]}\n ' \
                                 f'Address : {file[14]}, City : {file[15]}\n'
                                 for file in files]
                    case "sms":
                        files = self.backup_extractor.extract_sms()
                        files = sorted(files, key=lambda s: s[0])
                        output = []
                        l = len(files)
                        i = 0
                        while i < l:
                            chat_id = files[i][0]
                            output.append(f"--------Messages for chat " + ("" if files[i][1] else "with ") +
                                           f"{files[i][1] if files[i][1] else files[i][4]}--------\n")
                            while i < l and files[i][0] == chat_id:
                                output[-1] += f" From {'owner' if files[i][3] else files[i][4]} on {files[i][2]}: {files[i][5]}\n"
                                i += 1
                            i += 1
                        files = output
                    case "calendar":
                        files = self.backup_extractor.extract_calendar()
                        files = [f'Event : {file[0]}\n' \
                                 f'  Description : {file[3]}\n' \
                                 f'  Start : {file[1]}, End : {file[2]}\n' \
                                 f'  Location : {file[4]}\n' \
                                 for file in files]
                    case "web_history":
                        pass
                    case "notes":
                        pass
                    case "call":
                        files = self.backup_extractor.extract_call_history()
                        files = [f"From {'owner' if file[0] else file[2]+'(' + file[-1] + ')'} " \
                                 f"to {'owner' if not file[0] else file[2]+' ('+file[-1]+ ')'}\n  " \
                                 f"Date : {file[4]}\n  " \
                                 f"Call answered : {'Yes'if file[1] else 'No'}, Duration : {file[5]}\n  " \
                                 f"Location : {file[3] if file[3] != '<<RecentsNumberLocationNotFound>>' else 'None'}" for file in files]
            else:
                files = self.backup_manager.list_backup_files(args.path)
                files = sorted(files, key=lambda s: s.split('.')[0])

            if files is None:
                l = 0
            else:
                l = len(files)

            print(f" There are {l} files " + (f"({'chat(s)' if args.category=='sms' else ('event(s)' if args.category =='calendar' else args.category)}) "
                                              if args.category else "") + "in the backup")
            batch_size = 5
            if args.format:
                batch_size = args.format
            try:
                for i in range(0, l, batch_size):
                    for j in range(i, min(i + batch_size, l)):
                        print(j, files[j])
                    if i + batch_size < l:
                        input('---Enter to show more---')
                    else:
                        break
            except KeyboardInterrupt:
                print('\nExiting the program...')
                return

        elif args.command == 'export':
            if not args.path:
                print("Please provide the path to the backup")
                print(self.commands)
                return
            if not args.dest_path:
                print("Please provide the destination path")
                print(self.commands)
                return
            elif not os.path.exists(args.dest_path):
                print("Please provide an existing path")
            elif args.category or args.category == 'all':
                self.backup_extractor = BackupExtractor(args.path)
                if args.category == 'photos' or args.category == 'all':
                    print("Extracting photos...")
                    data = self.backup_extractor.extract_photos()
                    if data is None:
                        print(f"There is no {args.category} data in this backup")
                        return
                    print("Done\n Exporting photos...")
                    self.data_manager.export_photos(data, args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")
                elif args.category == 'videos' or args.category == 'all':
                    print("Extracting videos...")
                    data = self.backup_extractor.extract_videos()
                    if data is None:
                        print(f"There is no {args.category} data in this backup")
                        return
                    print("Done\nExporting videos...")
                    self.data_manager.export_videos(data, args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")
                elif args.category == 'contacts' or args.category == 'all':
                    print("Extracting contacts...")
                    data = self.backup_extractor.extract_contacts()
                    if data is None:
                        print(f"There is no {args.category} data in this backup")
                        return
                    print(data)
                    print("Done\n Exporting contacts...")
                    self.data_manager.export_contacts(data, args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")
                elif args.category == 'sms' or args.category == 'all':
                    print("Extracting sms...")
                    data = self.backup_extractor.extract_sms()
                    if data is None:
                        print(f"There is no {args.category} data in this backup")
                        return
                    print(data)
                    print("Done\n Exporting sms...")
                    self.data_manager.export_sms(data,args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")
                elif args.category == 'calendar' or args.category == 'all':
                    print("Extracting calendar events...")
                    data = self.backup_extractor.extract_calendar()
                    if data is None:
                        print(f"There is no {args.category} data in this backup")
                        return
                    print("Done\n Exporting calendar events...")
                    self.data_manager.export_calendar(data, args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")
                elif args.category == 'web_history' or args.category == 'all':
                    pass
                    '''print("Extracting web history...")
                    data = self.backup_extractor.extract_web_history()
                    print("Done\n Exporting web history...")
                    self.data_manager.export_web_history(data, args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")'''
                elif args.category == 'notes' or args.category == 'all':
                    '''print("Extracting web history...")
                    data = self.backup_extractor.extract_notes()
                    print("Done\n Exporting web history...")
                    self.data_manager.export_notes(data,args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")'''
                elif args.category == 'call' or args.category == 'all':
                    print("Extracting call history...")
                    data = self.backup_extractor.extract_call_history()
                    if data is None:
                        print(f"There is no {args.category} data in this backup")
                        return
                    print("Done\n Exporting call history...")
                    self.data_manager.export_call_history(data, args.dest_path)
                    print(f"Done. Exported to {args.dest_path}")

        else:
            print(self.commands)


if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
