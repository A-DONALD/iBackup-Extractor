import code

from app.backup_manager import BackupManager
import os
import shutil
import sqlite3
import unittest


'''def test1 ():
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
            '''


class BackupManagerTest (unittest.TestCase) :
    # Create a BackupManager object

    def setUp(self):
        self.temp_dir = "C:\\Users\\kamde\\OneDrive\\Bureau\\Erasmus Course\\ZSWIE"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Create mock backup data in the temporary directory
        # (e.g., create folders with Manifest.plist and Manifest.db files)


    def tearDown(self):
        #shutil.rmtree(self.temp_dir)
        pass


    def test_search_backups(self):
        backup_manager = BackupManager(self.temp_dir)
        # Test if the search_backups method correctly identifies backup folders
        expected_backups = None  # The expected backup folder names
        self.assertEqual(backup_manager.search_backups(), expected_backups)



    def test_list_backups(self):
        backup_manager = BackupManager(self.temp_dir)
        backup_manager.search_backups()
        # Test if the list_backups method returns the correct list of backups
        expected_backups = ['6e81410f-6424-4ec2-829e-1471769a741e'] # The expected backup folder names
        self.assertEqual(backup_manager.list_backups(), expected_backups)


    def test_list_backup_files(self):
        backup_manager = BackupManager(self.temp_dir)
        # Test if the list_backup_files method returns the correct list of files for a given backup_id
        expected_backup_files = ['AppDomain-com.tencent.xin/Documents/d97fe37b0a29a5e898334a8a0a4f5b21/DB/MM.sqlite', 'AppDomainGroup-group.com.bsb.hike/messagesDB.sqlite', 'AppDomainGroup-group.viber.share.container/database/Contacts.data', 'CameraRollDomain/Media/DCIM/100APPLE/IMG_0008.JPG', 'AppDomain-com.cardify.tinder/Library/Application Support/Tinder/Tinder2.sqlite', 'AppDomainGroup-group.com.kik.chat/cores/private/2397401800a84992a72eca4b171e6522/kik.sqlite', 'AppDomainGroup-group.com.kik.chat/cores/private/2397401800a84992a72eca4b171e6522/attachments/e3f2d391-b42f-4f6c-8845-3497145cc4c5', 'AppDomainGroup-group.com.kik.chat/Library/Preferences/group.com.kik.chat.plist', 'AppDomainGroup-group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite', 'AppDomainGroup-group.com.linecorp.line/Library/Application Support/PrivateStore/P_u87dfe7c117b73cb67a5b03c43787a6b2/Messages/Line.sqlite', 'AppDomainGroup-group.com.tencent.xin/Library/Preferences/group.com.tencent.xin.plist', 'CameraRollDomain/Media/PhotoData/Photos.sqlite', 'HomeDomain/Library/Calendar/Calendar.sqlitedb', 'AppDomainGroup-group.com.apple.notes/NoteStore.sqlite', 'HomeDomain/Library/AddressBook/AddressBook.sqlitedb', 'RootDomain/Library/Caches/locationd/consolidated.db', 'HomeDomain/Library/CallHistoryDB/CallHistory.storedata', 'HomeDomain/Library/SMS/sms.db', 'HomeDomain/Library/SpringBoard/IconState.plist', 'CameraRollDomain/Media/DCIM/100APPLE/IMG_0007.JPG', 'CameraRollDomain/Media/DCIM/100APPLE/IMG_0006.MP4', 'CameraRollDomain/Media/DCIM/100APPLE/IMG_0005.JPG', 'CameraRollDomain/Media/DCIM/100APPLE/IMG_0002.JPG', 'CameraRollDomain/Media/DCIM/100APPLE/IMG_0003.JPG', 'CameraRollDomain/Media/DCIM/100APPLE/IMG_0004.JPG', 'AppDomain-net.whatsapp.WhatsApp/Library/Media/40741757524@s.whatsapp.net/0/0/00700321-8dcc-4394-9336-b64643082849.jpg', 'AppDomain-net.whatsapp.WhatsApp/Library/Media/40741757524@s.whatsapp.net/0/0/00700321-8dcc-4394-9336-b64643082849.thumb', 'AppDomainGroup-group.com.kik.chat/cores/private/2397401800a84992a72eca4b171e6522/content_manager/data_cache/e3f2d391-b42f-4f6c-8845-3497145cc4c5', 'AppDomain-com.tencent.xin/Documents/d97fe37b0a29a5e898334a8a0a4f5b21/Img/c974d167528e4eedac052a2d4002a697/5.pic', 'AppDomain-com.tencent.xin/Documents/d97fe37b0a29a5e898334a8a0a4f5b21/Img/c974d167528e4eedac052a2d4002a697/5.pic_thum', 'AppDomain-jp.naver.line/Library/Application Support/PrivateStore/P_u87dfe7c117b73cb67a5b03c43787a6b2/Message Attachments/u813875af3cff6f32aa22d89d9bd70dd7/5719285560565.jpg', 'AppDomainGroup-group.com.linecorp.line/Library/Application Support/PrivateStore/P_u87dfe7c117b73cb67a5b03c43787a6b2/Message Thumbnails/u813875af3cff6f32aa22d89d9bd70dd7/5719285560565.thumb', 'HomeDomain/Library/Preferences/com.apple.springboard.plist', 'HomeDomain/Library/Preferences/com.apple.restrictionspassword.plist']
        # The expected backup folder names
        self.assertEqual(backup_manager.list_backup_files(0), expected_backup_files)

    def test_get_file_path(self):
        backup_manager = BackupManager(self.temp_dir)
        backup_manager.list_backup_files(0)
        # Test if the get_file_path method returns the correct file path for a given backup_id and file
        expected_file_path = r"C:\Users\kamde\OneDrive\Bureau\Erasmus Course\ZSWIE\6e81410f-6424-4ec2-829e-1471769a741e\6c\6c35901eb1273c5f71992905cb75b087b60e24e7"
        self.assertEqual(backup_manager.get_file_path(0, "AppDomainGroup-group.com.bsb.hike/messagesDB.sqlite"), expected_file_path)

if __name__ == "__main__":
    unittest.main()
