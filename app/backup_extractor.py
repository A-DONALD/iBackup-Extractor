import os
import plistlib
import sqlite3
import shutil

from backup_manager import BackupManager


class BackupExtractor:
    """This class is responsible for extracting the data from the backup files."""

    def __init__(self, backup_path=None):
        self.backup_path = backup_path
        self.backup_metadata = {}
        self.extracted_data = {}

    def get_metadata(self):
        manifest = os.path.join(self.backup_path, "Manifest.plist")
        with open(manifest, 'rb') as fp:
            self.backup_metadata['Manifest'] = plistlib.load(fp)
            self.backup_metadata['Manifest']['Starting date'] = self.backup_metadata['Manifest'].pop('Date')

        info = os.path.join(self.backup_path, "Info.plist")
        with open(info, 'rb') as fp:
            self.backup_metadata['Info'] = plistlib.load(fp)

        status = os.path.join(self.backup_path, "Status.plist")
        with open(status, 'rb') as fp:
            self.backup_metadata['Status'] = plistlib.load(fp)
            self.backup_metadata['Status']['Ending date'] = self.backup_metadata['Status'].pop('Date')
        return self.backup_metadata

    def extract_photos(self,backup_manger=None, backup_id=None, include_path=True):
        # Temp
        source_file = os.path.join(self.backup_path, "12", "12b144c0bd44f2b3dffd9186d3f9c05b917cee25")
        if not os.path.exists(source_file):
            return None
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "Photos.sqlite")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT
                  ZDIRECTORY,
                  ZFILENAME, -- On-Disk filename
                  DATETIME(ZDATECREATED + STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime'), -- Creation Timestamp
                  ZLATITUDE,  -- Latitude
                  ZLONGITUDE -- Longitude
                  FROM ZGENERICASSET
                  ORDER BY ZDATECREATED ASC
                        """)
        except:
            cursor.execute("""
                        SELECT
                              ZDIRECTORY,
                              ZFILENAME, -- On-Disk filename
                              DATETIME(ZDATECREATED + STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime'), -- Creation Timestamp
                              ZLATITUDE,  -- Latitude
                              ZLONGITUDE -- Longitude
                              FROM ZASSET
                              ORDER BY ZDATECREATED ASC
                                    """)
        result = cursor.fetchall()
        self.extracted_data['photos'] = []


        self.extracted_data['photos'] = result

        if include_path:
            backup_manger.list_backup_files(backup_id)
            for file in result:
                file = list(file)
                file.insert(2, backup_manger.get_file_path(backup_id, "Media/"+file[0]+"/"+file[1]))
                self.extracted_data['photos'].append(tuple(file))
        return self.extracted_data['photos']

    def extract_videos(self, backup_manger=None, backup_id=None, include_path=True):

        if backup_manger is None or backup_id is None:
            # Connect to the Manifest.db file
            conn = sqlite3.connect(os.path.join(self.backup_path, "Manifest.db"))

            # Get a cursor object
            cursor = conn.cursor()

            # Execute a query to get information about the files in the backup
            cursor.execute('SELECT * FROM Files')

            # Store all information about files for further usage
            result = cursor.fetchall()
            files = [f"{row[1]}/{row[2]}" for row in result]

        else:
            files = backup_manger.list_backup_files(backup_id)
        videos = []
        for file in files:
            if file.startswith("CameraRollDomain") and file.casefold().endswith("mp4"):
                if backup_manger and include_path:
                    videos.append((file.split("/")[-1], backup_manger.get_file_path(backup_id, file)))
                else:
                    videos.append(file.split("/")[-1])
        self.extracted_data['videos'] = videos
        return self.extracted_data['videos']

    def extract_contacts(self):
        # Temp
        source_file = os.path.join(self.backup_path, "31", "31bb7ba8914766d4ba40d6dfb6113c8b614be442")
        if not os.path.exists(source_file):
            return None
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "AddressBook.sqlitedb")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()

        # Execute a query to get information about the files in the backup
        cursor.execute("SELECT ABPerson.first,ABPerson.last   ,"
                       "ABPerson.Organization AS organization,"
                       "ABPerson.Department AS department,DATETIME(ABPerson.Birthday + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS Birthday,ABPerson.JobTitle as jobtitle,"
                       "ABPerson.Note,ABPerson.Nickname,DATETIME(ABPerson.CreationDate + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS Created,DATETIME(ABPerson.ModificationDate + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS Modified,( SELECT value FROM ABMultiValue "
                       "WHERE property = 3 AND record_id = ABPerson.ROWID AND label = (SELECT ROWID FROM ABMultiValueLabel "
                       "WHERE value = '_$!<Work>!$_')) AS phone_work,( SELECT value FROM ABMultiValue "
                       "WHERE property = 3 AND record_id = ABPerson.ROWID AND label = (SELECT ROWID FROM ABMultiValueLabel "
                       "WHERE value = '_$!<Mobile>!$_')) AS phone_mobile,"
                       "( SELECT value FROM ABMultiValue WHERE property = 3 AND record_id = ABPerson.ROWID AND label = ("
                       "SELECT ROWID FROM ABMultiValueLabel WHERE value = '_$!<Home>!$_')) AS phone_home,"
                       "( SELECT value FROM ABMultiValue WHERE property = 4 AND record_id = ABPerson.ROWID AND label IS null)"
                       " AS email,( SELECT value FROM ABMultiValueEntry WHERE parent_id IN ("
                       "SELECT ROWID FROM ABMultiValue WHERE record_id = ABPerson.ROWID) AND key = ("
                       "SELECT ROWID FROM ABMultiValueEntryKey WHERE lower(value) = 'street')) AS address,"
                       "( SELECT value FROM ABMultiValueEntry WHERE parent_id IN ("
                       "SELECT ROWID FROM ABMultiValue WHERE record_id = ABPerson.ROWID) AND key = ("
                       "SELECT ROWID FROM ABMultiValueEntryKey WHERE lower(value) = 'city')) AS city "
                       "FROM ABPerson "
                       "INNER JOIN ABPersonFullTextSearch_content"
                       " ON ABPersonFullTextSearch_content.docid = ABPerson.ROWID"
                       " ORDER BY ABPerson.first")

        self.extracted_data['contacts'] = []
        self.extracted_data['contacts'].append([description[0] for description in cursor.description])
        self.extracted_data['contacts'].append(cursor.fetchall())
        return self.extracted_data['contacts']

    def extract_sms(self):
        # Temp
        source_file = os.path.join(self.backup_path, "3d", "3d0d7e5fb2ce288813306e4d4636395e047a3d28")
        if not os.path.exists(source_file):
            return None
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "sms.db")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT
                            chat_message_join.chat_id,chat.display_name,
                            datetime(message.date/ 1000000000 + 978307200, 'unixepoch') AS date,
                            message.is_from_me,
                            handle.id AS sender_number,
                            message.text AS content
                        FROM
                            message
                        JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
                        JOIN chat ON chat_message_join.chat_id = chat.ROWID
                        JOIN handle ON message.handle_id = handle.ROWID
                        ORDER BY message.date;
                       """)
        self.extracted_data['sms'] = cursor.fetchall()
        return self.extracted_data['sms']

    def extract_calender(self):
        source_file = os.path.join(self.backup_path, "20", "2041457d5fe04d39d0ab481178355df6781e6858")
        if not os.path.exists(source_file):
            return None
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "Calendar.sqlitedb")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("SELECT ci.summary,DATETIME(ci.start_date + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime'),"
                       "DATETIME(ci.end_date + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime'),"
                       "ci.description, l.title FROM CalendarItem "
                       "ci LEFT JOIN Location l ON ci.location_id = l.ROWID")

        self.extracted_data['calendar'] = cursor.fetchall()
        return self.extracted_data['calendar']

    # TBT
    def extract_web_history(self):
        source_file = os.path.join(self.backup_path, "1a", "1a0e7afc19d307da602ccdcece51af33afe92c53")
        if not os.path.exists(source_file):
            return None
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "History.db")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)
        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("SELECT * from history_visits LEFT JOIN history_items ON history_items.ROWID = "
                       "history_visits.history_item")
        self.extracted_data['web_history'] = cursor.fetchall()
        return self.extracted_data['web_history']

    # TBD
    def extract_notes(self):
        # Temp
        source_file = os.path.join(self.backup_path, "4f", "4f98687d8ab0d6d1a371110e6b7300f6e465bef2")
        if not os.path.exists(source_file):
            return None
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "NoteStore.sqlite")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ZICNOTEDATA;
            """)

        headers = [i[0] for i in cursor.description]

        self.extracted_data['notes'] = cursor.fetchall()

        for row in self.extracted_data['notes'] :
            i = 0
            for header in headers:
                print(header," : ",row[i])
                i += 1
            print("----------------")

        #print(self.extracted_data['notes'])

    def extract_call_history(self):
        # Temp
        source_file = os.path.join(self.backup_path, "5a", "5a4935c78a5255723f707230a451d79c540d2741")
        if not os.path.exists(source_file):
            return None
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "CallHistory.storedata")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("SELECT ZORIGINATED,ZANSWERED,ZLOCATION,DATETIME(ZDATE + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime'),ZDURATION,ZADDRESS FROM ZCALLRECORD ORDER BY ZDATE;")
        result = cursor.fetchall()
        if 'contacts' not in self.extracted_data.keys():
            self.extract_contacts()

        self.extracted_data['call_history'] = []
        for row in result:
            row = list(row)
            seconds = row[4]
            # converting time
            seconds = seconds % (24 * 3600)
            hour = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            row[4] = "%d:%02d:%02d" % (hour, minutes, seconds)

            row.insert(2, "Unknown number")
            for contact in self.extracted_data['contacts']:
                if contact[0] and row[-1].decode('utf-8') in contact[0].split(" "):
                    # row.insert(2, contact[1] + " " + contact[2])
                    row[2] = contact[1] + " " + contact[2]
            row[-1] = ""+row[-1].decode()
            row = tuple(row)
            self.extracted_data['call_history'].append(row)

        return self.extracted_data['call_history']

    def extract_data(self,backup_manager, backup_id):
        """extracts data from the backup file and returns it as a dictionary"""
        if not self.backup_path:
            return None
        self.extract_photos(backup_manager,backup_id)
        self.extract_videos(backup_manager,backup_id)
        self.extract_contacts()
        self.extract_sms()
        self.extract_calender()
        self.extract_web_history()

        self.extract_call_history()
        return self.extracted_data



