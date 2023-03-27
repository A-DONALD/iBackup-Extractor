import os
import plistlib

class BackupExtractor:
    """This class is responsible for extracting the data from the backup files."""
    def __init__(self,backup_path):
        self.backup_path = backup_path
        self.extracted_data = {}

    def get_metadata(self):
        metadata ={}
        manifest = os.path.join(self.backup_path, "Manifest.plist")
        with open(manifest, 'rb') as fp:
            metadata['Manifest'] = plistlib.load(fp)

        info = os.path.join(self.backup_path, "Info.plist")
        with open(info, 'rb') as fp:
            metadata['Info'] = plistlib.load(fp)

        status = os.path.join(self.backup_path, "Status.plist")
        with open(status, 'rb') as fp:
            metadata['Status'] = plistlib.load(fp)
        return metadata

    def extract_data(self):
        """extracts data from the backup file and returns it as a dictionary"""
        return self.extracted_data
