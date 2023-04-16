
class DataManager:
    """This class is responsible for managing the extracted data, storing it, and retrieving it as necessary."""
    import csv
    with open(r'C:\Users\donal\Downloads\backup samples\test.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=';')
        data = [['Me', 'You'],
                ['293', '219'],
                ['54', '13']]
        a.writerows(data)