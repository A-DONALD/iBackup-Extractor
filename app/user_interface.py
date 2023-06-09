import argparse
import os
from app.backup_manager import BackupManager
from app.backup_extractor import BackupExtractor
from app.data_manager import DataManager


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
                                    \t available categories : camera, photos, videos, contacts, sms, whatsapp ,calendar,web_history, notes, call, all
                                    """

    def run(self):
        global backup_id
        parser = argparse.ArgumentParser(prog='ibe')
        subparsers = parser.add_subparsers(dest='command')

        # Backup search command
        search_parser = subparsers.add_parser('search', help='Search for backups in the specified path')
        search_parser.add_argument('-p', '--path', type=str, help='Path to search for backups')
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
            elif not os.path.exists(args.path):
                print("Please provide a valid path for the search")
                return
            self.backup_manager = BackupManager(args.path)
            self.backup_manager.search_backups()
            backups = self.backup_manager.list_backups()

            if not backups:
                print(f"There are no backup files in {args.path}")
                return

            l = max(len(s) for s in backups) + len(args.path) if args.l else max(len(s) for s in backups)
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
            if not metadata:
                print(f"There is no backup files in the specified path : {args.path}")
                return
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

        elif args.command == 'list' or args.command == 'export':

            if not args.path:
                print("Please provide the path to the backup")
                return
            elif not os.path.exists(args.path):
                print(f"The path doesn't exist. PLease check it : {args.path}")
                return
            manifest = os.path.join(args.path, "Manifest.plist")
            if not os.path.exists(manifest):
                print(f"There is no backup files in the path : {args.path}")
                return

            if args.command == 'list':
                print("Extracting...")
                files = []
                if args.path:
                    self.backup_manager = BackupManager(args.path)
                elif args.id:
                    pass
                if args.category:
                    self.backup_extractor = BackupExtractor(args.path)
                    match args.category:
                        case "camera":
                            files = [file[1] for file in self.backup_extractor.extract_photos(include_path=False)]
                        case "photos":
                            camera = self.backup_extractor.extract_photos(include_path=False)
                            files = []
                            for file in camera:
                                if file[1].casefold().endswith(".mp4"):
                                    continue
                                files.append(file[1])
                        case "videos":
                            files = self.backup_extractor.extract_videos(include_path=False)
                        case "contacts":
                            files = self.backup_extractor.extract_contacts()[1]
                            if files:
                                files = [f'Name : {file[0]} {file[1] if file[1] else ""}\n ' \
                                         f'Number : {file[11] if file[11] else (file[10] if file[10] else file[12])}, ' \
                                         f'Email : {file[13]}\n ' \
                                         f'Organization : {file[2]}\n Department : {file[3]}\n ' \
                                         f'Birthday : {file[4]}\n Created : {file[8]}, Last time modified : {file[9]}\n ' \
                                         f'Address : {file[14]}, City : {file[15]}\n'
                                         for file in files]
                        case "sms":
                            files = self.backup_extractor.extract_sms()
                            if files:
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
                            if files:
                                files = [f'Event : {file[0]}\n' \
                                         f'  Description : {file[3]}\n' \
                                         f'  Start : {file[1]}, End : {file[2]}\n' \
                                         f'  Location : {file[4]}\n' \
                                         for file in files]
                        case "web_history":
                            files = self.backup_extractor.extract_web_history()
                            if files:
                                files = [f"Title : {file[0]}" \
                                         f"Visit time : {file[1]}" for file in files]
                        case "notes":
                            files = self.backup_extractor.extract_notes()
                            if files:
                                files = [f"Title : {file[0]}\n"
                                         f"  Last time modified : {file[1]}\n" 
                                         f"  Content : {file[2]}\n" for file in files]
                        case "call":
                            files = self.backup_extractor.extract_call_history()
                            if files:
                                files = [f"From {'owner' if file[0] else file[2]+'(' + file[-1] + ')'} " \
                                         f"to {'owner' if not file[0] else file[2]+' ('+file[-1]+ ')'}\n  " \
                                         f"Date : {file[4]}\n  " \
                                         f"Call answered : {'Yes'if file[1] else 'No'}, Duration : {file[5]}\n  " \
                                         f"Location : {file[3] if file[3] != '<<RecentsNumberLocationNotFound>>' else 'None'}" for file in files]

                        case "whatsapp":
                            files = self.backup_extractor.extract_whatsapp_messages()
                            if files:
                                files = sorted(files, key=lambda s: s[0])
                                output = []
                                l = len(files)
                                i = 0
                                while i < l:
                                    chat_id = files[i][0]
                                    output.append(f"--------Messages for " + ("chat with " if files[i][1] else "group chat ") +
                                                  f"{files[i][1] if files[i][1] else files[i][2]}--------\n")
                                    while i < l and files[i][0] == chat_id:
                                        output[
                                            -1] += f" From {'owner' if files[i][3] else files[i][1]} on {files[i][4]}: {files[i][5]}\n"
                                        i += 1
                                    i += 1
                                files = output

                        case "all":
                            files = self.backup_manager.list_backup_files(args.path)
                            files = sorted(files, key=lambda s: s.split('.')[0])

                        case _:
                            print(f"Sorry we can't recognize the category {args.category}\n Available categories : "
                                  f"camera, photos, videos, contacts, sms, calendar,web_history, notes, call, all")
                            return
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
                            print("------------------------------------")
                        if i + batch_size < l:
                            input(f'---Enter to show more ({l-(i+batch_size)} left)---')
                        else:
                            break
                except KeyboardInterrupt:
                    print('\nExiting the program...')
                    return

            elif args.command == 'export':
                if not args.dest_path:
                    print("Please provide the destination path")
                    print(self.commands)
                    return
                elif not os.path.exists(args.dest_path):
                    print("Please provide an existing path")
                    return
                elif args.category:
                    self.backup_extractor = BackupExtractor(args.path)
                    if args.category == 'camera' or args.category == 'all':
                        print("Extracting camera...")
                        camera = self.backup_extractor.extract_photos()
                        if camera is None:
                            print(f"There is no photos data in this backup")
                            return
                        photos = []
                        videos = []
                        for file in camera:
                            if file[1].casefold().endswith(".mp4"):
                                videos.append(file)
                                continue
                            photos.append(file)
                        print("Done\n Exporting photos...")
                        self.data_manager.export_photos(photos, args.dest_path)
                        print("Done\n Exporting videos...")
                        self.data_manager.export_videos(videos, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")

                    if args.category == 'photos':
                        print("Extracting photos...")
                        data = self.backup_extractor.extract_photos()
                        if data is None:
                            print(f"There is no photos data in this backup")
                            return
                        print("Done\n Exporting photos...")
                        self.data_manager.export_photos(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'videos':
                        print("Extracting videos...")
                        data = self.backup_extractor.extract_videos()
                        if data is None:
                            print(f"There is no videos data in this backup")
                            return
                        print("Done\nExporting videos...")
                        self.data_manager.export_videos(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'contacts' or args.category == 'all':
                        print("Extracting contacts...")
                        data = self.backup_extractor.extract_contacts()
                        if data is None:
                            print(f"There is no contacts data in this backup")
                            return
                        print("Done\n Exporting contacts...")
                        self.data_manager.export_contacts(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'sms' or args.category == 'all':
                        print("Extracting sms...")
                        data = self.backup_extractor.extract_sms()
                        if data is None:
                            print(f"There is no sms data in this backup")
                            return
                        print("Done\n Exporting sms...")
                        self.data_manager.export_sms(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'whatsapp' or args.category == 'all':
                        print("Extracting whatsapp messages...")
                        data = self.backup_extractor.extract_whatsapp_messages()
                        if data is None:
                            print(f"There is no whatsapp chat data in this backup")
                            return
                        print("Done\n Exporting whatsapp messages...")
                        self.data_manager.export_whatsapp(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'calendar' or args.category == 'all':
                        print("Extracting calendar events...")
                        data = self.backup_extractor.extract_calendar()
                        if data is None:
                            print(f"There is no calendar data in this backup")
                            return
                        print("Done\n Exporting calendar events...")
                        self.data_manager.export_calendar(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'web_history' or args.category == 'all':
                        print("Extracting web history...")
                        data = self.backup_extractor.extract_web_history()
                        if data is None:
                            print(f"There is no web history data in this backup")
                            return
                        print("Done\n Exporting web history...")
                        self.data_manager.export_web_history(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'notes' or args.category == 'all':
                        print("Extracting notes...")
                        data = self.backup_extractor.extract_notes()
                        if data is None:
                            print(f"There is no web history data in this backup")
                            return
                        print("Done\n Exporting notes...")
                        self.data_manager.export_notes(data,args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category == 'call' or args.category == 'all':
                        print("Extracting call history...")
                        data = self.backup_extractor.extract_call_history()
                        if data is None:
                            print(f"There is no {args.category} data in this backup")
                            return
                        print("Done\n Exporting call history...")
                        self.data_manager.export_call_history(data, args.dest_path)
                        print(f"Done. Exported to {args.dest_path}")
                    if args.category not in ["camera", "photos", "videos", "contacts", "sms", "calendar", "whatsapp", "web_history", "notes", "call"]:
                        print(f"Sorry we can't recognize the category {args.category}\n Available categories : "
                              f"camera, photos, videos, contacts, sms, calendar,web_history, notes, call, all")

        else:
            print(self.commands)
