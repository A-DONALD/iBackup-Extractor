from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from icalendar import Calendar, Event
from datetime import datetime
# for time zone UTC
from pytz import UTC
import csv
import os
import shutil


class DataManager:
    """This class is responsible for managing the extracted data, storing it, and retrieving it as necessary."""

    def export_contacts(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "contact.csv"), 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for contact in extracted_data:
                writer.writerow(contact)

    def export_call_history(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "call_history.csv"), 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                ["From", "To", "Name", "Type", "Start date", "Duration", "Location"])
            for contact in extracted_data:
                is_for_me, call_successful, name, location, call_time, call_duration, phone_number = contact
                if is_for_me == 0:
                    writer.writerow([phone_number, "me", name, "standard", call_time, call_duration, location])
                elif is_for_me == 1:
                    writer.writerow(["me", phone_number, name, "standard", call_time, call_duration, location])

    def export_web_history(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "web_history.csv"), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, extracted_data.keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(extracted_data)

    def export_sms(self, extracted_data, data_dir):
        # create a new folder messages
        if not (os.path.exists(os.path.join(data_dir, "messages"))):
            os.mkdir(os.path.join(data_dir, "messages"))
        # group the message by phone number
        grouped_data = {}
        for data in extracted_data:
            title, datetime, is_for_me, phone_number, message = data
            if phone_number not in grouped_data:
                grouped_data[phone_number] = []
            grouped_data[phone_number].append((title, datetime, is_for_me, message))

        # for each phone number, we will create a new pdf doc
        for phone_number, messages in grouped_data.items():
            pdf_filename = os.path.join(data_dir, "messages", f"{phone_number}.pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # add header with phone number
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, 750, f"Messages with {phone_number}")

            # add each message in the pdf
            c.setFont('Helvetica', 12)
            y = 700
            for title, datetime, is_for_me, message in messages:
                if is_for_me == 1:
                    c.drawString(50, y, f"sent on {datetime}: {message}")
                elif is_for_me == 0:
                    c.drawString(50, y, f"received on {datetime}: {message}")
                y -= 20
            c.save()

    def export_calendar(self, extracted_data, data_dir):
        # create a new calendar
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
        for data in extracted_data:
            summary, dtstart, dtend, description, title = data
            # create new event for each element of extracted_data
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

        f = open(os.path.join(data_dir, "calendar.ics"), 'wb')
        f.write(cal.to_ical())
        f.close()

    def export_photos(self, photos, data_dir):
        if isinstance(photos, list):
            for file in photos:
                self.export_photos(file, data_dir)

        else:
            if os.path.exists(photos[2]):
                source_file = photos[2]
                os.makedirs(os.path.join(data_dir, "Photos"),
                            exist_ok=True)  # create Photos directory if it doesn't exist
                data_dir = os.path.join(data_dir, "Photos", photos[0])
                shutil.copy2(source_file, data_dir)

    def export_videos(self, videos, data_dir):
        if isinstance(videos, list):
            for file in videos:
                self.export_videos(file, data_dir)

        else:
            if os.path.exists(videos[1]):
                source_file = videos[1]
                os.makedirs(os.path.join(data_dir, "Videos"),
                            exist_ok=True)  # create Photos directory if it doesn't exist
                data_dir = os.path.join(data_dir, "Videos", videos[0])
                shutil.copy2(source_file, data_dir)