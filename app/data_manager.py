import csv
import os
class DataManager:
    """This class is responsible for managing the extracted data, storing it, and retrieving it as necessary."""
    def __init__(self, data_dir):
        self.__data_dir = data_dir
        self.__extracted_data = dict()

    def export_contacts(self):
        with open(os.path.join(self.__data_dir, "contacts.csv"), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, self.__extracted_data.keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(self.__extracted_data)