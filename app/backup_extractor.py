import os
import plistlib
import sqlite3
import shutil
import binascii
import logging
import zlib

__Plugin_Name = "NOTES"
log = logging.getLogger('MAIN.' + __Plugin_Name) # Do not rename or remove this ! This is the logger object


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
        photos = cursor.fetchall()
        self.extracted_data['photos'] = photos

        if include_path:
            if not os.path.exists(os.path.join(self.backup_path, "Manifest.db")):
                return None
            conn = sqlite3.connect(os.path.join(self.backup_path, "Manifest.db"))
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Files')
            files_list = cursor.fetchall()
            files = dict()
            for row in files_list:
                files[row[2].split("/")[-1]] = row[0]
            self.extracted_data['photos'] = []
            for photo in photos:
                photo = list(photo)
                if photo[1] in files.keys():
                    filename = files[photo[1]]
                    photo.insert(2,os.path.join(self.backup_path,filename[:2],filename))
                else:
                    photo.insert(2,"Unknown")
                self.extracted_data['photos'].append(tuple(photo))
        return self.extracted_data['photos']

    def extract_videos(self, include_path=True):
        if not os.path.exists(os.path.join(self.backup_path, "Manifest.db")):
            return None
        # Connect to the Manifest.db file
        conn = sqlite3.connect(os.path.join(self.backup_path, "Manifest.db"))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Files')
        files = cursor.fetchall()

        videos = []
        for file in files:
            filename = f"{file[1]}/{file[2]}"
            if filename.startswith("CameraRollDomain") and filename.casefold().endswith("mp4"):
                if include_path:
                    videos.append((filename.split("/")[-1],os.path.join(self.backup_path,file[0][:2],file[0])))
                else:
                    videos.append(filename.split("/")[-1])
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
        cursor.execute("SELECT IFNULL(ABPerson.first,c0First) AS Firstname,IFNULL(ABPerson.last,c1Last) AS Lastname ,"
                       "ABPerson.Organization AS Organization,"
                       "ABPerson.Department AS Department,DATETIME(ABPerson.Birthday + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS Birthday,ABPerson.JobTitle as Jobtitle,"
                       "ABPerson.Note,ABPerson.Nickname,DATETIME(ABPerson.CreationDate + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS Creation,DATETIME(ABPerson.ModificationDate + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS Modified,( SELECT value FROM ABMultiValue "
                       "WHERE property = 3 AND record_id = ABPerson.ROWID AND label = (SELECT ROWID FROM ABMultiValueLabel "
                       "WHERE value = '_$!<Work>!$_')) AS Phone_work,IFNULL(( SELECT value FROM ABMultiValue "
                       "WHERE property = 3 AND record_id = ABPerson.ROWID AND label = (SELECT ROWID FROM ABMultiValueLabel "
                       "WHERE value = '_$!<Mobile>!$_')),c16Phone) AS Phone_mobile,"
                       "( SELECT value FROM ABMultiValue WHERE property = 3 AND record_id = ABPerson.ROWID AND label = ("
                       "SELECT ROWID FROM ABMultiValueLabel WHERE value = '_$!<Home>!$_')) AS Phone_home,"
                       "( SELECT value FROM ABMultiValue WHERE property = 4 AND record_id = ABPerson.ROWID AND label IS null)"
                       " AS Email,( SELECT value FROM ABMultiValueEntry WHERE parent_id IN ("
                       "SELECT ROWID FROM ABMultiValue WHERE record_id = ABPerson.ROWID) AND key = ("
                       "SELECT ROWID FROM ABMultiValueEntryKey WHERE lower(value) = 'street')) AS Address,"
                       "( SELECT value FROM ABMultiValueEntry WHERE parent_id IN ("
                       "SELECT ROWID FROM ABMultiValue WHERE record_id = ABPerson.ROWID) AND key = ("
                       "SELECT ROWID FROM ABMultiValueEntryKey WHERE lower(value) = 'city')) AS City "
                       "FROM ABPerson "
                       "INNER JOIN ABPersonFullTextSearch_content"
                       " ON ABPersonFullTextSearch_content.docid = ABPerson.ROWID"
                       " ORDER BY Firstname ")

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
                            datetime((IFNULL(message.date,message.date_delivered)/ 1000000000) + 978307200, 'unixepoch') AS date,
                            message.is_from_me,
                            handle.id AS sender_number,
                            message.text AS content
                        FROM
                            message
                        JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
                        JOIN chat ON chat_message_join.chat_id = chat.ROWID
                        JOIN handle ON message.handle_id = handle.ROWID
                        ORDER BY date;
                       """)
        self.extracted_data['sms'] = cursor.fetchall()
        return self.extracted_data['sms']

    def extract_calendar(self):
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

        conn = sqlite3.connect(dest_file)
        cursor = conn.cursor()
        cursor.execute("""SELECT
                              IFNULL(ZICCLOUDSYNCINGOBJECT.ZTITLE,ZICCLOUDSYNCINGOBJECT.ZTITLE1) AS title,
                              datetime(ZMODIFICATIONDATE1 + 978307200, 'unixepoch') AS creation_date,
                              ZICNOTEDATA.ZDATA AS note_data
                            FROM
                              ZICCLOUDSYNCINGOBJECT
                            JOIN
                              ZICNOTEDATA ON ZICCLOUDSYNCINGOBJECT.Z_PK = ZICNOTEDATA.ZNOTE;
                        """)
        notes = cursor.fetchall()

        def ReadLengthField(blob):
            '''Returns a tuple (length, skip) where skip is number of bytes read'''
            length = 0
            skip = 0
            try:
                data_length = int(blob[0])
                length = data_length & 0x7F
                while data_length > 0x7F:
                    skip += 1
                    data_length = int(blob[skip])
                    length = ((data_length & 0x7F) << (skip * 7)) + length
            except (IndexError, ValueError):
                log.exception('Error trying to read length field in note data blob')
            skip += 1
            return length, skip

        def GetUncompressedData(compressed):
            if compressed == None:
                return None
            data = None
            try:
                data = zlib.decompress(compressed, 15 + 32)
            except zlib.error:
                log.exception('Zlib Decompression failed!')
            return data

        def ProcessNoteBodyBlob(blob):
            data = b''
            if blob == None: return data
            try:
                pos = 0
                if blob[0:3] != b'\x08\x00\x12':  # header
                    # log.error('Unexpected bytes in header pos 0 - ' + binascii.hexlify(blob[0:3]) + '  Expected 080012')
                    return ''
                pos += 3
                length, skip = ReadLengthField(blob[pos:])
                pos += skip

                if blob[pos:pos + 3] != b'\x08\x00\x10':  # header 2
                    log.error('Unexpected bytes in header pos {0}:{0}+3'.format(pos))
                    return ''
                pos += 3
                length, skip = ReadLengthField(blob[pos:])
                pos += skip

                # Now text data begins
                if blob[pos] != 0x1A:
                    log.error('Unexpected byte in text header pos {} - byte is 0x{:X}'.format(pos, blob[pos]))
                    return ''
                pos += 1
                length, skip = ReadLengthField(blob[pos:])
                pos += skip
                # Read text tag next
                if blob[pos] != 0x12:
                    log.error('Unexpected byte in pos {} - byte is 0x{:X}'.format(pos, blob[pos]))
                    return ''
                pos += 1
                length, skip = ReadLengthField(blob[pos:])
                pos += skip
                data = blob[pos: pos + length].decode('utf-8', 'backslashreplace')
                # Skipping the formatting Tags
            except (IndexError, ValueError):
                log.exception('Error processing note data blob')
            return data

        result = []
        for note in notes:
            tmp = [note[0], note[1]]
            data = GetUncompressedData(note[-1])
            data = ProcessNoteBodyBlob(data)
            tmp.append(data)
            result.append(tuple(tmp))

        return result

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
            for contact in self.extracted_data['contacts'][1]:
                if contact[11] and row[-1].decode('utf-8') in contact[11].split(" "):
                    # row.insert(2, contact[1] + " " + contact[2])
                    row[2] = contact[0] + " " + contact[1]
            row[-1] = ""+row[-1].decode()
            row = tuple(row)
            self.extracted_data['call_history'].append(row)

        return self.extracted_data['call_history']

    def extract_data(self,backup_manager, backup_id):
        """extracts data from the backup file and returns it as a dictionary"""
        if not self.backup_path:
            return None
        self.extract_photos(backup_manager)
        self.extract_videos(backup_manager)
        self.extract_contacts()
        self.extract_sms()
        self.extract_calendar()
        self.extract_web_history()

        self.extract_call_history()
        return self.extracted_data

test = BackupExtractor(r"C:\Users\MSI\Downloads\backup samples\00008020-0011548E34D1002E")
print(test.extract_notes())
