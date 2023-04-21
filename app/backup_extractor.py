import os
import biplist
import plistlib
import sqlite3
import shutil

class BackupExtractor:
    """This class is responsible for extracting the data from the backup files."""
    def __init__(self,backup_path=None):
        self.backup_path = backup_path
        self.backup_metadata = {}
        self.extracted_data = {}

    def get_metadata(self):
        manifest = os.path.join(self.backup_path, "Manifest.plist")
        with open(manifest, 'rb') as fp:
            self.backup_metadata['Manifest'] = plistlib.load(fp)

        info = os.path.join(self.backup_path, "Info.plist")
        with open(info, 'rb') as fp:
            self.backup_metadata['Info'] = plistlib.load(fp)

        status = os.path.join(self.backup_path, "Status.plist")
        with open(status, 'rb') as fp:
            self.backup_metadata['Status'] = plistlib.load(fp)

    '''def extract_photos(self,files):
        if isinstance(files,list):
            for file in files:
                self.extract_photos(file)
        else:
            if os.path.exists(files[1]):
                source_file = files[1]
                os.makedirs(os.path.join(os.path.curdir, "Photos"), exist_ok=True)  # create Photos directory if it doesn't exist
                dest_file = os.path.join(os.path.curdir, "Photos", files[0].split('/')[-1])
                shutil.copy2(source_file, dest_file)'''

    def extract_photos(self):
        # Temp
        source_file = os.path.join(self.backup_path, "12", "12b144c0bd44f2b3dffd9186d3f9c05b917cee25")
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "Photos.sqlite")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
              ZDIRECTORY,
              DATETIME(ZDATECREATED + STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime'), -- Creation Timestamp
              ZLATITUDE,  -- Latitude
              ZLONGITUDE, -- Longitude
              ZFILENAME -- On-Disk filename
              FROM ZGENERICASSET
              ORDER BY ZDATECREATED ASC
                    """)

        self.extracted_data['photos'] = cursor.fetchall()

    # TBD
    def extract_videos(self):
        pass

    def extract_contacts(self):
        #Temp
        source_file = os.path.join(self.backup_path, "31", "31bb7ba8914766d4ba40d6dfb6113c8b614be442")
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "AddressBook.sqlitedb")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()

        # Execute a query to get information about the files in the backup
        cursor.execute("SELECT ROWID, ABPerson.first,ABPerson.last,ABPerson.Organization AS organization,"
                       "ABPerson.Department AS department,DATETIME(ABPerson.Birthday + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS Birthday,ABPerson.JobTitle as jobtitle,"
                       "ABPerson.Organization,ABPerson.Department,ABPerson.Note,ABPerson.Nickname,DATETIME(ABPerson.CreationDate + "
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
                       "FROM ABPerson ORDER BY ABPerson.first")

        self.extracted_data['contacts'] = cursor.fetchall()

    def extract_sms(self):
        # Temp
        source_file = os.path.join(self.backup_path, "3d", "3d0d7e5fb2ce288813306e4d4636395e047a3d28")
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "sms.db")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT
                        display_name,
                        DATETIME(date +
                        STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime'),
                        is_from_me,
                        handle.id as sender_name,text
                        FROM chat_message_join,chat
                        INNER JOIN message
                          ON message.rowid = chat_message_join.message_id
                        INNER JOIN handle
                          ON handle.rowid = message.handle_id
                        ORDER BY message.date
                       """)

        self.extracted_data['sms'] = cursor.fetchall()

    def extract_calender(self):
        # Temp
        source_file = os.path.join(self.backup_path, "20", "2041457d5fe04d39d0ab481178355df6781e6858")
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
        print(self.extracted_data['calendar'] )

    # TBT
    def extract_web_history(self):
        source_file = os.path.join(self.backup_path, "1a", "1a0e7afc19d307da602ccdcece51af33afe92c53")
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

    # TBD
    def extract_notes(self):
        # Temp
        source_file = os.path.join(self.backup_path, "4f", "4f98687d8ab0d6d1a371110e6b7300f6e465bef2")
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "NoteStore.sqlite")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ZDATA FROM ZICNOTEDATA
        """)

        self.extracted_data['notes'] = cursor.fetchall()

        print(self.extracted_data['notes'])

    # TBD
    def extract_call_history(self):
        # Temp
        source_file = os.path.join(self.backup_path, "5a", "5a4935c78a5255723f707230a451d79c540d2741")
        os.makedirs(os.path.join(os.path.curdir, "../tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "../tmp", "CallHistory.storedata")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT ZUNIQUE_ID, ZDURATION, ZLOCATION
                        FROM ZCALLRECORD;

                        """)

        self.extracted_data['call_history'] = cursor.fetchall()
        print(self.extracted_data['call_history'])

    def extract_data(self):
        """extracts data from the backup file and returns it as a dictionary"""

        if not self.backup_path:
            return None


        return self.extracted_data

