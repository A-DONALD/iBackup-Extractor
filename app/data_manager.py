from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
import string
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
            writer = csv.writer(file, delimiter=',')
            writer.writerow(extracted_data[0])
            for contact in extracted_data[1]:
                Firstname, Lastname, Organization, Department, Birthday, Jobtitle, Note, Nickname, Creation, Modified, Phone_work, Phone_mobile, Phone_home, Email, Address, City = contact
                if Firstname:
                    Firstname = Firstname.replace("\u200d","")
                    Firstname = Firstname.replace("\u010d","")
                    Firstname = ''.join(char for char in Firstname if char.isalnum())
                writer.writerow([Firstname, Lastname, Organization, Department, Birthday, Jobtitle, Note, Nickname, f"'{Creation}", f"'{Modified}", Phone_work, Phone_mobile, Phone_home, Email, Address, City])

    def export_call_history(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "call_history.csv"), 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(
                ["From", "To", "Name", "Type", "Start date", "Duration", "Location"])
            for contact in extracted_data:
                is_for_me, call_successful, name, location, call_time, call_duration, phone_number = contact
                phone_number = f"'{phone_number}"
                if is_for_me == 0:
                    writer.writerow([phone_number, "me", name, "standard", call_time, call_duration,
                                     location if location != '<<RecentsNumberLocationNotFound>>' else ''])
                elif is_for_me == 1:
                    writer.writerow(["me", phone_number, name, "standard", call_time, call_duration,
                                     location if location != '<<RecentsNumberLocationNotFound>>' else ''])

    def export_web_history(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "web_history.csv"), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, extracted_data.keys(), delimiter=',')
            writer.writeheader()
            writer.writerows(extracted_data)

    def export_sms(self, extracted_data, data_dir):
        # create a new folder messages
        if not (os.path.exists(os.path.join(data_dir, "Messages"))):
            os.mkdir(os.path.join(data_dir, "Messages"))
        # group the message by phone number
        grouped_data = {}
        for data in extracted_data:
            id, display_name, datetime, is_for_me, phone_number, message = data
            if phone_number not in grouped_data:
                grouped_data[phone_number] = []
            grouped_data[phone_number].append((display_name, datetime, is_for_me, message))

        # for each phone number, we will create a new pdf doc
        for phone_number, messages in grouped_data.items():
            if phone_number.find("*") != -1:
                phone_number = phone_number.split("*")[1]
            pdf_filename = os.path.join(data_dir, "Messages", f"{phone_number}.pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # add header with phone number
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, 750, f"Messages with {phone_number}")

            # Wrap the message text
            wrap_width = 110  # Adjust this value based on your desired line width

            # add each message in the pdf
            c.setFont('Helvetica', 10)
            y = 700

            for title, datetime, is_for_me, message in messages:
                if is_for_me == 1:
                    wrapped_message = textwrap.wrap(f"Sent on {datetime}: {message}", wrap_width)
                    for line in wrapped_message:
                        c.drawString(50, y, line)
                        y -= 20
                elif is_for_me == 0:
                    wrapped_message = textwrap.wrap(f"Received on {datetime}: {message}", wrap_width)
                    for line in wrapped_message:
                        c.drawString(50, y, line)
                        y -= 20
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
                data_dir = os.path.join(data_dir, "Photos", photos[1])
                shutil.copy2(source_file, data_dir)

    def export_videos(self, videos, data_dir):
        if isinstance(videos, list):
            for file in videos:
                self.export_videos(file, data_dir)

        else:
            if os.path.exists(videos[2]):
                source_file = videos[2]
                os.makedirs(os.path.join(data_dir, "Videos"),
                            exist_ok=True)  # create Photos directory if it doesn't exist
                data_dir = os.path.join(data_dir, "Videos", videos[1])
                shutil.copy2(source_file, data_dir)

    def export_notes(self,notes,data_dir):
        # create a new folder messages
        if not (os.path.exists(os.path.join(data_dir, "Notes"))):
            os.mkdir(os.path.join(data_dir, "Notes"))
            # for note, we will create a new pdf doc
        for i,(title, date, content) in enumerate(notes):
            title = [char for char in title if char not in string.punctuation]
            title = ''.join(title)
            if title:
                pdf_filename = os.path.join(data_dir, "Notes", f"{title}.pdf")
            else:
                pdf_filename = os.path.join(data_dir, "Notes", f"note-{i}.pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # add header
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, 750, title)
            c.setFont('Helvetica', 9)
            c.drawString(50, 730, date)

            # Wrap the message text
            wrap_width = 110  # Adjust this value based on your desired line width

            # add each message in the pdf
            c.setFont('Helvetica', 10)
            y = 700

            wrapped_message = textwrap.wrap(content,wrap_width)
            for line in wrapped_message:
                c.drawString(50, y, line)
                y -= 20
            y -= 20
            c.save()

    def export_whatsapp(self,extracted_data, data_dir):
        # create a new folder whatsapp messages
        if not (os.path.exists(os.path.join(data_dir, "Whatsapp"))):
            os.mkdir(os.path.join(data_dir, "Whatsapp"))

        # group the message by phone number
        grouped_data = {}
        for data in extracted_data:
            id, sender, groupName, is_from_me, date, message = data
            if id not in grouped_data.keys():
                grouped_data[id] = []
            grouped_data[id].append((sender, groupName, is_from_me, date, message))

        # for each chat, we will create a new pdf doc
        for data in grouped_data.values():
            if data[0][1]:
                chat_name = f"Group chat {data[0][1]}"
            else:
                chat_name = f"{data[0][0]}"
            chat_name = [char for char in chat_name if char not in string.punctuation]
            chat_name = ''.join(chat_name)
            pdf_filename = os.path.join(data_dir, "Whatsapp", chat_name+".pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # add header with phone number
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, 750, f"Messages with {chat_name}")

            # Wrap the message text
            wrap_width = 110  # Adjust this value based on your desired line width

            # add each message in the pdf
            c.setFont('Helvetica', 10)
            y = 700
            bottom_margin = 50  # Adjust this value based on your desired bottom margin
            for sender, groupName, is_from_me, date, message in data:
                if y < bottom_margin:  # Check if the y-coordinate is less than the bottom margin
                    y = self.create_new_page(c, chat_name)  # Create a new page and reset the y-coordinate

                if is_from_me:
                        wrapped_message = textwrap.wrap(f"Sent on {date}: {message}", wrap_width)
                        for line in wrapped_message:
                            c.drawString(50, y, line)
                            y -= 20
                else:
                    wrapped_message = textwrap.wrap(f"Received from {sender if sender else groupName} on {date}: {message}", wrap_width)
                    for line in wrapped_message:
                        c.drawString(50, y, line)
                        y -= 20
                y -= 20
            c.save()

    def create_new_page(self,c, chat_name):
        c.showPage()
        c.setFont('Helvetica', 10)
        c.drawString(50, 750, f"Messages with {chat_name}")
        return 700
