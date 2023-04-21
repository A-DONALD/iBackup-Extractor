from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC # timezone
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
    def export_sms(self, extracted_data):
        # group the message by phone number
        grouped_data = {}
        for data in extracted_data:
            title, datetime, is_for_me, phone_number, message = data
            if phone_number not in grouped_data:
                grouped_data[phone_number] = []
            grouped_data[phone_number].append((title, datetime, is_for_me, message))

        # for each phone number, we will create a new pdf doc
        for phone_number, messages in grouped_data.items():
            pdf_filename = os.path.join(self.__data_dir, "messages", f"{phone_number}.pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # ajouter un en-tête avec le numéro de téléphone
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, 750, f"Messages with {phone_number}")

            # ajouter chaque message dans le corps du PDF
            c.setFont('Helvetica', 12)
            y = 700
            for title, datetime, is_for_me, message in messages:
                if is_for_me == 1:
                    c.drawString(50, y, f"sent on {datetime}: {message}")
                elif is_for_me == 0:
                    c.drawString(50, y, f"received on {datetime}: {message}")
                y -= 20
            c.save()
    def export_calendar(self, extracted_data):
        # create a new calendar
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
        for data in extracted_data:
            summary, dtstart, dtend, description, title = data
            event = Event()
            event.add('summary', f'{summary}')
            event.add('dtstart', datetime(int(dtstart.split("-")[0]),
                                            int(dtstart.split("-")[1]),
                                            int(dtstart.split("-")[2].split(" ")[0]),
                                            int(dtstart.split(":")[0].split(" ")[1]),
                                            int(dtstart.split(":")[1]),
                                            int(dtstart.split(":")[2]), tzinfo=UTC))
            event.add('dtend', datetime(int(dtend.split("-")[0]),
                                          int(dtend.split("-")[1]),
                                          int(dtend.split("-")[2].split(" ")[0]),
                                          int(dtend.split(":")[0].split(" ")[1]),
                                          int(dtend.split(":")[1]),
                                          int(dtend.split(":")[2]), tzinfo=UTC))
            event.add('description', f'{description}')
            event.add('title', f'{title}')
            event.add('priority', 5)
            cal.add_component(event)

        f = open(os.path.join(self.__data_dir, "calendar.ics"), 'wb')
        f.write(cal.to_ical())
        f.close()