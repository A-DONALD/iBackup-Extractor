from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# tableau contenant les données extractées
extracted_data = [
    ('', '2017-02-22 14:28:40', 0, '+40741757524', "Don't forget to buy food for Tommy. Love you!"),
    ('', '2017-02-23 12:05:20', 1, '+40741757524', "Did you buy the food for Tommy?"),
    ('', '2017-02-24 10:35:15', 0, '+33678451236', 'Hi, how are you?'),
    ('', '2017-02-25 09:15:00', 1, '+33678451236', 'I am fine, thank you. And you?')
]

# regrouper les messages par numéro de téléphone
grouped_data = {}
for data in extracted_data:
    title, datetime, is_for_me, phone_number, message = data
    if phone_number not in grouped_data:
        grouped_data[phone_number] = []
    grouped_data[phone_number].append((title, datetime, is_for_me, message))

# pour chaque numéro de téléphone, créer un nouveau PDF
for phone_number, messages in grouped_data.items():
    pdf_filename = f"{phone_number}.pdf"
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
