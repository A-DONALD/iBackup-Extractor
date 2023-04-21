from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC # timezone
import csv
import os
import shutil
class DataManager:
    """This class is responsible for managing the extracted data, storing it, and retrieving it as necessary."""
    def export_contacts(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "contact.csv"), 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                ['ROWID', 'First', 'Last', 'organization', 'department', 'Birthday', 'jobtitle', 'Organization',
                 'Department', 'Note', 'Nickname', 'Created', 'Modified', 'phone_work', 'phone_mobile', 'phone_home',
                 'email', 'address', 'city'])
            for contact in extracted_data:
                writer.writerow(contact)
    def export_call_history(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "call_history.csv"), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, extracted_data.keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(extracted_data)
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
            if os.path.exists(photos[1]):
                source_file = photos[1]
                os.makedirs(os.path.join(data_dir, "Photos"),
                            exist_ok=True)  # create Photos directory if it doesn't exist
                dest_file = os.path.join(data_dir, "Photos", photos['filename'])
                shutil.copy2(source_file, dest_file)

test = DataManager()
sms_data = [('', '2017-02-22 14:28:40', 1, '+40741757524', "Don't forget to buy food for Tommy. Love you!"),
            ('', '2017-02-22 15:00:10', 0, '+33741757524', "Wanna play BasketBall today ?"),
            ('', '2017-02-22 15:28:00', 0, '+40741757524', "Don't worry, I will buy the food. Love you too! ^_^"),
            ('', '2017-02-22 16:00:01', 1, '+33741757524', "Of course. lets go!")]
test.export_sms(sms_data, r'C:\Users\donal\Downloads\backup samples')
calendar_data = [('back to angers', '2022-05-13 09:28:40', '2022-05-13 20:30:00', 'We need to back in our country', None)]
test.export_calendar(calendar_data, r'C:\Users\donal\Downloads\backup samples')
cars = [
{'No': 1, 'Company': 'Ferrari', 'Car Model': '488 GTB'},
{'No': 2, 'Company': 'Porsche', 'Car Model': '918 Spyder'},
{'No': 3, 'Company': 'Bugatti', 'Car Model': 'La Voiture Noire'},
{'No': 4, 'Company': 'Rolls Royce', 'Car Model': 'Phantom'},
{'No': 5, 'Company': 'BMW', 'Car Model': 'BMW X7'},
]
contact_data = [(4, 'Albert Fitzpatrick', None, None, None, None, None, None, None, None, None, '2017-02-22 13:56:05', '2017-09-14 15:02:14', None, None, None, None, None, None),
                (3, "Doctor's Office", None, None, None, None, None, None, None, None, None, '2017-02-22 13:55:38', '2017-09-14 15:02:14', None, None, None, None, None, None),
                (5, 'Ginny Weasley', None, None, None, None, None, None, None, None, None, '2017-02-22 13:56:20', '2017-09-14 15:02:14', None, None, None, None, None, None),
                (2, 'Jane', 'Appleseed', None, None, None, None, None, None, None, None, '2017-02-22 13:09:56', '2017-09-14 15:02:14', None, None, None, None, None, None),
                (6, 'Principal Howard', None, None, None, None, None, None, None, None, None, '2017-02-22 13:56:46', '2017-09-14 15:02:14', None, None, None, None, None, None)]

test.export_contacts(contact_data, r'C:\Users\donal\Downloads\backup samples')