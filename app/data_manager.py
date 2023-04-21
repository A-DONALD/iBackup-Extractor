import csv
import os
class DataManager:
    """This class is responsible for managing the extracted data, storing it, and retrieving it as necessary."""
    def __init__(self, data_dir):
        self.__data_dir = data_dir

    def export_contacts(self, extracted_data):
        with open(os.path.join(self.__data_dir, "contacts.csv"), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, extracted_data.keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(extracted_data)
    def export_call_history(self, extracted_data):
        with open(os.path.join(self.__data_dir, "call_history.csv"), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, extracted_data.keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(extracted_data)
    def export_web_history(self, extracted_data):
        with open(os.path.join(self.__data_dir, "web_history.csv"), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, extracted_data.keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(extracted_data)