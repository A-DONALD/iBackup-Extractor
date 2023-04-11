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

    def extract_photos(self,files):
        if isinstance(files,list):
            for file in files:
                self.extract_photos(file)
        else:
            if os.path.exists(files[1]):
                source_file = files[1]
                os.makedirs(os.path.join(os.path.curdir, "Photos"), exist_ok=True)  # create Photos directory if it doesn't exist
                dest_file = os.path.join(os.path.curdir, "Photos", files[0].split('/')[-1])
                shutil.copy2(source_file, dest_file)

    def extract_videos(self):
        pass

    def extract_contacts(self):
        #Temp
        source_file = os.path.join(self.backup_path, "31", "31bb7ba8914766d4ba40d6dfb6113c8b614be442")
        os.makedirs(os.path.join(os.path.curdir, "tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "tmp", "AddressBook.sqlitedb")
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

    def extract_calender(self):
        # Temp
        source_file = os.path.join(self.backup_path, "20", "2041457d5fe04d39d0ab481178355df6781e6858")
        os.makedirs(os.path.join(os.path.curdir, "tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "tmp", "Calendar.sqlitedb")
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

    def extract_sms(self):
        # Temp
        source_file = os.path.join(self.backup_path, "3d", "3d0d7e5fb2ce288813306e4d4636395e047a3d28")
        os.makedirs(os.path.join(os.path.curdir, "tmp"), exist_ok=True)
        dest_file = os.path.join(os.path.curdir, "tmp", "sms.db")
        shutil.copy2(source_file, dest_file)

        # Connect to the Manifest.db file
        conn = sqlite3.connect(dest_file)

        # Get a cursor object
        cursor = conn.cursor()
        cursor.execute("SELECT chat.display_name AS discussion_title,message.is_from_me AS is_sent_message,"
                       "handle.uncanonicalized_id AS sender_uncanonicalized_id,"
                       "DATETIME(message.date + "
                       "STRFTIME('%s', '2001-01-01 00:00:00'), 'unixepoch', 'localtime') AS message_datetime,"
                       "message.text AS message_content FROM chat_message_join,chat_handle_join "
                       "INNER JOIN chat ON chat.ROWID = chat_message_join.chat_id "
                       "INNER JOIN message ON message.ROWID = chat_message_join.message_id "
                       "INNER JOIN handle ON handle.ROWID = chat_handle_join.handle_id "
                       "ORDER BY message.date")

        self.extracted_data['sms'] = cursor.fetchall()

    def extract_web_history(self):
        pass

    def extract_data(self):
        """extracts data from the backup file and returns it as a dictionary"""

        if not self.backup_path:
            return None

        return self.extracted_data



