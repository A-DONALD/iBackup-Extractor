import csv

employee_info = ['emp_id', 'emp_name', 'skills']

new_dict = [
    {'emp_id': 456, 'emp_name': 'George', 'skills': 'Python'},
    {'emp_id': 892, 'emp_name': 'Adam', 'skills': 'Java'},
    {'emp_id': 178, 'emp_name': 'Gilchrist', 'skills': 'Mongo db'},
    {'emp_id': 155, 'emp_name': 'Elon', 'skills': 'Sql'},
    {'emp_id': 299, 'emp_name': 'Mask', 'skills': 'Ruby'},
]

with open(r'C:\Users\donal\Downloads\backup samples\test.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=employee_info, delimiter=';')
    writer.writeheader()
    writer.writerows(new_dict)