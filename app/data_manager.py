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
            writer = csv.writer(file, delimiter=',')
            writer.writerow(extracted_data[0])
            for contact in extracted_data[1]:
                Firstname, Lastname, Organization, Department, Birthday, Jobtitle, Note, Nickname, Creation, Modified, Phone_work, Phone_mobile, Phone_home, Email, Address, City = contact
                Firstname = Firstname.replace("\u200d","")
                Firstname = Firstname.replace("\u010d","")
                Firstname = ''.join(char for char in Firstname if char.isalnum())
                writer.writerow([Firstname, Lastname, Organization, Department, Birthday, Jobtitle, Note, Nickname, Creation, Modified, Phone_work, Phone_mobile, Phone_home, Email, Address, City])

    def export_call_history(self, extracted_data, data_dir):
        with open(os.path.join(data_dir, "call_history.csv"), 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
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
            writer = csv.DictWriter(csvfile, extracted_data.keys(), delimiter=',')
            writer.writeheader()
            writer.writerows(extracted_data)

    def export_sms(self, extracted_data, data_dir):
        # create a new folder messages
        if not (os.path.exists(os.path.join(data_dir, "messages"))):
            os.mkdir(os.path.join(data_dir, "messages"))
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
            pdf_filename = os.path.join(data_dir, "messages", f"{phone_number}.pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # add header with phone number
            c.setFont('Helvetica-Bold', 14)
            c.drawString(50, 750, f"Messages with {phone_number}")

            # add each message in the pdf
            c.setFont('Helvetica', 10)
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
# create data manager instance
manager = DataManager()
destination_file_location = r"C:\Users\donal\Downloads\backup samples"
contact = [['Firstname', 'Lastname', 'Organization', 'Department', 'Birthday', 'Jobtitle', 'Note', 'Nickname', 'Creation', 'Modified', 'Phone_work', 'Phone_mobile', 'Phone_home', 'Email', 'Address', 'City'],
         [('Albert Fitzpatrick', None, None, None, None, None, None, None, '2017-02-22 13:56:05', '2017-09-14 15:02:14', None, None, None, None, None, None),
          ("Doctor's Office", None, None, None, None, None, None, None, '2017-02-22 13:55:38', '2017-09-14 15:02:14', None, None, None, None, None, None),
          ('Ginny Weasley', None, None, None, None, None, None, None, '2017-02-22 13:56:20', '2017-09-14 15:02:14', None, None, None, None, None, None),
          ('Jane', 'Appleseed', None, None, None, None, None, None, '2017-02-22 13:09:56', '2017-09-14 15:02:14', None, '0741757524', None, None, None, None),
          ('Principal Howard', None, None, None, None, None, None, None, '2017-02-22 13:56:46', '2017-09-14 15:02:14', None, None, None, None, None, None)]]
# test export contact
manager.export_contacts(contact, destination_file_location)
contact = [['Firstname', 'Lastname', 'Organization', 'Department', 'Birthday', 'Jobtitle', 'Note', 'Nickname', 'Creation', 'Modified', 'Phone_work', 'Phone_mobile', 'Phone_home', 'Email', 'Address', 'City'], [('Adam', 'Korbelík', None, None, None, None, None, None, '2020-10-18 16:23:02', '2022-10-31 19:45:25', None, '+420770671187', None, None, None, None), ('Adam ', 'Hora', None, None, None, None, None, None, '2022-10-09 18:38:20', '2022-10-31 19:45:25', None, '+420773495084', None, None, None, None), ('Amálka', 'Burešová', None, None, None, None, None, None, '2022-01-28 17:59:37', '2022-10-31 19:45:25', None, '+420737155780', None, None, None, None), ('Amálka ', None, None, None, None, None, None, None, '2020-11-05 17:16:11', '2022-10-31 19:45:25', None, '+420607127051', None, None, None, None), ('Anet', None, None, None, '2011-02-20 13:00:00', None, None, None, '2022-09-08 12:27:32', '2022-10-31 19:45:25', None, '+420774270337', None, None, None, None), ('Anežka 🐎', None, None, None, '2011-01-17 13:00:00', None, None, None, '2020-08-09 16:03:58', '2022-10-31 19:45:25', None, '+420727828620', None, None, None, None), ('Anička ', 'Vítovcová', None, None, None, None, None, None, '2021-02-12 13:19:16', '2022-10-31 19:45:25', None, '+420732476709', None, None, None, None), ('Anička 🐾', None, None, None, '2011-06-16 14:00:00', None, None, None, '2022-09-07 11:24:47', '2022-10-31 19:45:25', None, '+420725919622', None, None, None, None), ('Antonín', 'Dezort', None, None, None, None, None, None, '2022-10-09 18:36:28', '2022-10-31 19:45:25', None, '+420703524073', None, None, None, None), ('Babička ', 'Zdenička', None, None, '1949-06-07 14:00:00', None, None, None, '2020-08-01 22:41:31', '2022-10-31 19:45:25', None, '+420721544917', '+420377966531', None, None, None), ('Barča', 'Houdková', None, None, None, None, None, None, '2022-08-31 19:13:41', '2022-10-31 19:45:25', None, '+420797819701', None, None, None, None), ('Barča', 'Kubiasová', None, None, None, None, None, None, '2022-10-05 18:59:20', '2022-10-31 19:45:25', None, '+420730576037', None, None, None, None), ('Barča🕊', 'Havlová', None, None, None, None, None, None, '2022-01-28 17:56:54', '2022-10-31 19:45:25', None, '+420778507667', None, None, None, None), ('Bětka', 'Vojtová', None, None, None, None, None, None, '2022-01-28 18:00:23', '2022-10-31 19:45:25', None, '+420730545867', None, None, None, None), ('David', 'Císař', None, None, None, None, None, None, '2022-10-09 18:43:26', '2022-10-31 19:45:25', None, '+420737772086', None, None, None, None), ('Deniska😃', None, None, None, None, None, None, None, '2022-09-23 19:38:23', '2022-10-31 19:45:25', None, '+420721510302', None, None, None, None), ('Dáša', 'Černá', None, None, '1978-05-09 14:00:00', None, None, None, '2020-09-17 17:09:44', '2022-10-31 19:45:25', None, '+420604826052 +420604826052 00420604826052 011420604826052 0604826052 604826052 826052 ', '+420604826052', None, 'Májová 1261', 'Starý Plzenec'), ('Děda', 'Tonda', None, None, None, None, None, None, '2020-08-01 22:42:19', '2022-10-31 19:45:25', None, '+420602324438', None, None, 'Dukelských hrdinů 1582', 'Rakovník'), ('Děda ', 'Pepa', None, None, '1949-05-05 14:00:00', None, None, None, '2020-08-01 22:41:06', '2022-10-31 19:45:25', None, '+420721653984', '+420 377 966 531', None, None, None), ('Elen', 'Rotová', None, None, None, None, None, None, '2020-10-19 19:31:49', '2022-10-31 19:45:25', None, '+420602471199', None, None, None, None), ('Ema', 'Machová', None, None, None, None, None, None, '2022-10-07 18:10:54', '2022-10-31 19:45:25', None, '+420777220179', None, None, None, None), ('František ', 'Lacina', None, None, None, None, None, None, '2022-05-26 13:20:14', '2022-10-31 19:45:25', None, '+420733285128', None, None, None, None), ('František ', 'Pěchota', None, None, None, None, None, None, '2022-10-09 18:37:32', '2022-10-31 19:45:25', None, '+420723513500', None, None, None, None), ('Gabriela ', 'Ulikova (zdravotnice)', None, None, None, None, 'Hotel, pokoj č. 204\n', None, '2022-07-31 18:48:31', '2022-10-31 19:45:25', None, '602\xa0972\xa0782 +420602972782 00420602972782 011420602972782 0602972782 602972782 972782 ', '602\xa0972\xa0782', None, None, None), ('Gabča✌️📱:3', None, None, None, None, None, None, None, '2020-10-10 19:39:41', '2022-10-31 19:45:25', None, '+420733272808', None, None, None, None), ('Hanka', 'Ratajová', None, None, None, None, None, None, '2021-08-15 21:27:28', '2022-10-31 19:45:25', None, '+420608261348', None, None, None, None), ('Hanka ', 'Rotová', None, None, None, None, None, None, '2020-10-19 18:37:27', '2022-10-31 19:45:25', None, '+420607966788 +420607966788 00420607966788 011420607966788 0607966788 607966788 966788 ', '+420607966788', None, None, None), ('Helča', 'Soudková', None, None, None, None, None, None, '2022-10-14 18:48:48', '2022-10-31 19:45:25', None, '+420703350548', None, None, None, None), ('Honza', 'Zatloukal', None, None, '2010-09-25 14:00:00', None, None, None, '2020-11-04 08:01:25', '2022-10-31 19:45:25', None, '+420608499489', None, None, None, None), ('Iva ', 'Pomajbíková', None, None, None, None, None, None, '2022-10-07 20:35:46', '2022-10-31 19:45:25', None, '+420777230651', None, None, None, None), ('Jakub', 'Valenta', None, None, None, None, None, None, '2022-10-09 18:44:19', '2022-10-31 19:45:25', None, '+420734446441', None, None, None, None), ('Jakub ', 'Vícha', None, None, None, None, None, None, '2020-10-18 16:21:58', '2022-10-31 19:45:25', None, '+420605065551', None, None, None, None), ('Jaroslav', 'Vodička', None, None, None, None, None, None, '2022-05-26 13:20:44', '2022-10-31 19:45:25', None, '+420606904954', None, None, None, None), ('Jaroslav ', 'Belatka', None, None, None, None, None, None, '2022-10-09 18:38:00', '2022-10-31 19:45:25', None, '+420737086236', None, None, None, None), ('Jaroslava', 'Tůmová 👩🏻\u200d🏫', None, None, None, None, None, None, '2021-01-10 19:18:25', '2022-10-31 19:45:25', None, '+420737239335', None, None, None, None), ('Jenda ', 'Protivínský', None, None, None, None, None, None, '2021-02-12 09:15:37', '2022-10-31 19:45:25', None, '+420776015044', None, None, None, None), ('Johanka', 'Kilianová', None, None, None, None, None, None, '2022-10-09 18:35:27', '2022-10-31 19:45:25', None, '+420702231854', None, None, None, None), ('Julinka', 'Rotová', None, None, None, None, None, None, '2020-10-19 19:35:34', '2022-10-31 19:45:25', None, '+420702245371', None, None, None, None), ('Julča', 'Štipská', None, None, None, None, None, None, '2022-01-28 17:57:11', '2022-10-31 19:45:25', None, '+420776301733', None, None, None, None), ('Justý', 'Kožnarová', None, None, None, None, None, None, '2022-10-07 13:57:59', '2022-10-31 19:45:25', None, '+420725657003', None, None, None, None), ('Justý ', 'Svobodová', None, None, None, None, None, None, '2022-10-07 19:03:19', '2022-10-31 19:45:25', None, '+420601533550', None, None, None, None), ('Jáchym ', 'Prokš', None, None, None, None, None, None, '2022-10-14 13:41:48', '2022-10-31 19:45:25', None, '+420602152166', None, None, None, None), ('Karolínka🐢⛄️', None, None, None, None, None, None, None, '2020-08-09 13:13:51', '2022-10-31 19:45:25', None, '+420734107307', None, None, 'Májová', 'Starý Plzenec'), ('Karol🏊🏼\u200d♀️🤸🏼\u200d♀️🏃🏼\u200d♀️', None, None, None, '2011-02-07 13:00:00', None, None, None, '2020-08-09 16:07:38', '2022-10-31 19:45:25', None, '+420777816370', None, None, None, None), ('Kačka', 'Černá', None, None, None, None, None, None, '2022-01-28 17:58:27', '2022-10-31 19:45:25', None, '+420773762841', None, None, None, None), ('Kačka ', 'Šimicová', None, None, None, None, None, None, '2022-01-28 17:58:53', '2022-10-31 19:45:25', None, '+420770118252', None, None, None, None), ('Kačka💜', 'Fialová', None, None, None, None, None, None, '2022-01-28 18:02:28', '2022-10-31 19:45:25', None, '+420607256509', None, None, None, None), ('Klaudi', 'Heringová', None, None, None, None, None, None, '2022-01-28 18:04:33', '2022-10-31 19:45:25', None, '+420601093898', None, None, None, None), ('Klaudi', 'Bláhová', None, None, '2010-12-23 13:00:00', None, None, None, '2022-09-07 10:45:35', '2022-10-31 19:45:25', None, '+420722084812', None, None, None, None), ('Klárka🐶', 'Pařízková', None, None, None, None, None, None, '2022-01-28 17:57:56', '2022-10-31 19:45:25', None, '+420776226088', None, None, None, None), ('Kristý', 'Hrabětová', None, None, None, None, None, None, '2020-10-12 20:10:53', '2022-10-31 19:45:25', None, '+420606568831', None, None, None, None), ('Kristýna', 'Pospíšilová', None, None, '2011-07-31 14:00:00', None, None, None, '2021-02-08 16:40:53', '2022-10-31 19:45:25', None, '737\xa0412\xa0446 +420737412446 00420737412446 011420737412446 0737412446 737412446 412446 ', '737\xa0412\xa0446', None, 'Karolíny Světlé 239 ', 'Starý Plzenec '), ('Kristýnka', 'Pospíšilová', None, None, '2011-07-31 14:00:00', None, None, None, '2020-08-09 20:24:06', '2022-10-31 19:45:25', None, '+420 737 412 446 +420737412446 00420737412446 011420737412446 0737412446 737412446 412446 ', None, None, 'Karolíny Světlé 239', 'Starý Plzenec'), ('Kristýnka ', 'Roubová', None, None, None, None, None, None, '2021-03-25 16:10:34', '2022-10-31 19:45:25', None, '+420737189389', None, None, None, None), ('Kristý🐨', None, None, None, '2011-02-07 13:00:00', None, None, None, '2021-02-12 15:29:29', '2022-10-31 19:45:25', None, '+420607917841', None, None, None, None), ('Káťa', 'Bednářová', None, None, None, None, None, None, '2020-11-05 15:20:36', '2022-10-31 19:45:25', None, '+420775444100', None, None, None, None), ('Lea⛸', 'Kratochvílová', None, None, None, None, None, None, '2022-01-28 18:01:24', '2022-10-31 19:45:25', None, '+420608209500', None, None, None, None), ('Lili 😺', None, None, None, None, None, None, None, '2020-08-09 16:02:47', '2022-10-31 19:45:25', None, '+420792769803 +420792769803 00420792769803 011420792769803 0792769803 792769803 769803 ', None, None, None, None), ('Lucka', 'Šimicová', None, None, None, None, None, None, '2022-03-19 10:52:01', '2022-10-31 19:45:25', None, '721\xa0634\xa0616 +420721634616 00420721634616 011420721634616 0721634616 721634616 634616 ', '721\xa0634\xa0616', None, None, None), ('Majda', None, None, None, '2011-01-12 13:00:00', None, None, None, '2022-09-09 17:57:15', '2022-10-31 19:45:25', None, '+420775331125', None, None, None, None), ('Maminka 👩🏼\u200d⚕️', None, None, None, '1976-07-15 14:00:00', None, None, None, '2020-11-05 20:29:49', '2022-10-31 19:45:25', None, '+420604470072', None, None, None, None), ('Markét🏀', None, None, None, None, None, None, None, '2022-09-02 10:53:13', '2022-10-31 19:45:25', '+420601324765', '+420601324765 +420601324765 00420601324765 011420601324765 0601324765 601324765 324765 ', None, None, None, None), ('Martin', 'Reitspies', None, None, None, None, None, None, '2022-10-09 18:37:03', '2022-10-31 19:45:25', None, '+420773999046', None, None, None, None), ('Maruška ', 'Legátová', None, None, None, None, None, None, '2022-01-28 18:03:52', '2022-10-31 19:45:25', None, '+420605558117', None, None, None, None), ('Matyáš ', 'Tomášek', None, None, None, None, None, None, '2021-04-22 19:14:43', '2022-10-31 19:45:25', None, '+420605784116', None, None, None, None), ('Michal', 'Karas', None, None, None, None, None, None, '2022-10-09 18:43:45', '2022-10-31 19:45:25', None, '+420739768723', None, None, None, None), ('Michal', 'Vatrs', None, None, None, None, None, None, '2022-10-17 20:27:19', '2022-10-31 19:45:25', None, '+420777047747', None, None, None, None), ('Monika ', 'Korčáková', None, None, None, None, None, None, '2022-09-08 12:27:52', '2022-10-31 19:45:25', None, '+420777834934', None, None, None, None), ('Natka', 'Horčičková', None, None, None, None, None, None, '2020-10-18 16:22:34', '2022-10-31 19:45:25', None, '+420737497820', None, None, None, None), ('Natálie', 'Čejková', None, None, None, None, None, None, '2022-10-17 20:28:12', '2022-10-31 19:45:25', None, '+420730504547', None, None, None, None), ('Natálka🕴🏻🐧', 'Mlejnková', None, None, None, None, None, None, '2021-01-06 15:12:30', '2022-10 -31 19:45:25', None, '+420734415000 +420734415000 00420734415000 011420734415000 0734415000 734415000 415000 ', None, None, None, None), ('Nella', 'Nováková', None, None, None, None, None, None, '2022-10-09 18:34:44', '2022-10-31 19:45:25', None, '+420604923243', None, None, None, None), ('Nelča ', 'Zelenková', None, None, None, None, None, None, '2022-01-28 18:02:01', '2022-10-31 19:45:25', None, '+420608147300', None, None, None, None), ('Niki', 'Kasalová', None, None, '2011-04-06 14:00:00', None, None, None, '2021-06-15 17:29:31', '2022-10-31 19:45:25', None, '722\xa0034\xa0690 +420722034690 00420722034690 011420722034690 0722034690 722034690 034690 ', '722\xa0034\xa0690', None, None, None), ('Ondra ', None, None, None, '2015-02-17 13:00:00', None, None, None, '2021-02-16 17:26:14', '2022-10-31 19:45:25', None, None, None, None, 'Karolíny Světlé 239', 'Starý Plzenec'), ('Pavel', 'Jůza', None, None, None, None, None, None, '2022-10-09 18:36:46', '2022-10-31 19:45:25', None, '+420774101308', None, None, None, None), ('Petr', 'Čejka', 'Storm Balet', None, None, None, None, None, '2020-10-26 18:06:53', '2022-10-31 19:45:25', '+420603223051', '+420724719099 +420724719099 00420724719099 011420724719099 0724719099 724719099 719099 +420603223051 +420603223051 00420603223051 011420603223051 0603223051 603223051 223051 ', '+420724719099', None, None, None), ('Petra ', 'Capová👩🏼\u200d🏫', None, None, None, None, None, None, '2021-03-05 08:42:50', '2022-10-31 19:45:25', None, '+420724526323', None, None, None, None), ('Radovan ', 'Volf', None, None, None, None, None, None, '2022-10-13 20:49:25', '2022-10-31 19:45:25', None, '+420702158710', None, None, None, None), ('Rudolf', 'Stehlík', None, None, None, None, None, None, '2022-10-09 18:33:53', '2022-10-31 19:45:25', None, '+420602836277', None, None, None, None), ('Sofi ', 'Nováková', None, None, None, None, None, None, '2021-06-19 09:42:36', '2022-10-31 19:45:25', None, '+420725579101', None, None, None, None), ('Sofča', 'Hájková', None, None, None, None, None, None, '2022-01-28 18:00:37', '2022-10-31 19:45:25', None, '+420725596815', None, None, None, None), ('Stela ', 'Baťková', None, None, None, None, None, None, '2022-01-28 18:00:56', '2022-10-31 19:45:25', None, '+420722973381', None, None, None, None), ('Tatínek👨🏻\u200d💻', None, None, None, '1976-06-15 14:00:00', None, None, None, '2020-08-01 22:40:29', '2022-10-31 19:45:25', '+420377632675', '+420721544920', None, None, None, None), ('Tobias ', 'Gruszka', None, None, None, None, None, None, '2022-01-28 18:00:47', '2022-10-31 19:45:25', None, '+420723341472', None, None, None, None), ('Tomáš', 'Jílek ', None, None, None, None, None, None, '2021-02-12 09:15:58', '2022-10-31 19:45:25', None, '+420731630516', None, None, None, None), ('Tomáš', 'Tran', None, None, None, None, None, None, '2022-10-09 18:35:03', '2022-10-31 19:45:25', None, '+420792394666', None, None, None, None), ('Vašík', 'Rataj ⚽️', None, None, None, None, None, None, '2020-08-25 14:02:51', '2022-10-31 19:45:25', None, '+420608322605', None, None, None, None), ('Veronika', 'Vacková', None, None, None, None, None, None, '2022-10-17 20:27:49', '2022-10-31 19:45:25', None, '+420734272025', None, None, None, None), ('Verča', 'Blažková', None, None, None, None, None, None, '2022-10-09 18:44:01', '2022-10-31 19:45:25', None, '+420732546789', None, None, None, None), ('Viky🐰', 'Nguyen', None, None, None, None, None, None, '2021-11-11 18:32:46', '2022-10-31 19:45:25', None, '+420774775999', None, None, None, None), ('Vlaďka', 'Mlejnková', None, None, None, None, None, None, '2020-08-28 13:20:45', '2022-10-31 19:45:25', None, '603 898 489 +420603898489 00420603898489 011420603898489 0603898489 603898489 898489 ', '603 898 489', None, None, None), ('Vojtěch ', 'Pexa', None, None, None, None, None, None, '2022-10-09 18:34:21', '2022-10-31 19:45:25', None, '+420603396967', None, None, None, None), ('Áďa', 'Hoštičková', None, None, None, None, None, None, '2022-01-28 18:01:14', '2022-10-31 19:45:25', None, '+420608381336', None, None, None, None), ('Štěpán', 'Kerner', None, None, None, None, None, None, '2022-05-26 13:21:00', '2022-10-31 19:45:25', None, '+420602624770', None, None, None, None)]]
# test export sms
manager.export_contacts(contact, destination_file_location)