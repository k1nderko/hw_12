from collections import UserDict
from datetime import datetime, timedelta
import re
from itertools import islice
import pickle

class Field:
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        self.value = value

class Phone(Field):
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
           if re.match(r'^\d{12}$', value):
               self._value = value               
        except ValueError:
            return ValueError('Phone must be in 123456789012 format')
        
        
class Birthday(Field):
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = datetime.strptime(value, '%d-%m-%Y').date()
            self._value = value 
        except ValueError:
            raise ValueError('Date must be in DD-MM-YYYY format')

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday
    
    def add_phone(self, phone):
        self.phones.append(phone)
    
    def change_phone(self, phone, ind):
        self.phones[ind] = phone

    def delete_phone(self, ind):
        self.phones.pop(ind)

    def add_birthday(self, birthday):
        self.birthday = birthday

    def days_to_birthday(self):
        if self.birthday:
            date = datetime.strptime(self.birthday.value, '%d-%m-%Y')
            today = datetime.now()
            birthday = datetime(today.year, date.month, date.day)
            if today > birthday:
                birthday = datetime.date(today.year + 1, self.birthday.month, self.birthday.day)
            days = birthday - today
            return days
        
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def change_record(self, name, record):
        self.data[name.value] = record

    def search_records(self, name):
        search_records = []
        for key in self.data:
            if name.lower() in key.lower():
                search_records.append(self.data[key])
        return search_records
    
    def iterator(self, start=None, stop=None):
        keys = islice(self.data.keys(), start, stop)
        result = '\n'.join(
            f'{i}: +{", +".join(p.value for p in self.data.get(i).phones)}, birthday {self.data.get(i).birthday}' for i in keys)

        yield result
    


contacts = AddressBook()

def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return 'No name or phone, try again or enter help'
        except KeyError:
            return 'No name or phone, try again or enter help'
        except  ValueError:
            return 'Wrong input, enter help for help'       
    return inner  

def hello(args) -> str:
    return 'How can I help you?'

def help(args) -> str:
    return '''
    hello -- just hello
    add (name phone) -- add new contact
    change (name phone) -- change contact phone
    del phone (name phone_number_on_the_list) -- delete phone
    phone (name) -- print contact phone
    set birthday name dd-mm-yyyy -- add birthday
    birthday name -- show birthday
    show all -- print all contacts
    exit, goodbye, close -- exit program'''

@input_error
def add(args) -> str:
    name = Name(args[0])
    phone = Phone(args[1])
    if not phone.value:
        return "Phone must be in 123456789876 format"
    if name.value in contacts:
        record = contacts[name.value]
        record.add_phone(phone)
        return f'Another phone for contact {name.value} added'
    else:
        record = Record(name)
        record.add_phone(phone)
        contacts.add_record(record)
        return f'Contact {name.value} added successfully.'

@input_error
def change(args) -> str:
    name = Name(args[0])
    phone = Phone(args[1])
    if not phone.value:
        return "Phone must be in 123456789876 format"
    record = contacts[name.value]
    record.change_phone(phone, 0)
    return f'Contact {name.value} modified successfully.'

@input_error
def delete_phone(args):
    name = Name(args[0])
    ind = int(args[1]) - 1
    record = contacts[name.value]
    record.delete_phone(ind)
    return f'Phone delete from contact {name.value}'

@input_error
def phone(args) -> str:
    name = Name(args[0])
    result = contacts.search_records(name.value)
    if result:
        for record in result:
            return f"{', '.join(str(phone) for phone in record.phones)}"

    return f'Have not contact {name.value}'

@input_error
def add_birthday(args):
    name = Name(args[0])
    birthday = Birthday(args[1])
    if not birthday.value:
        return "Date must be in DD-MM-YYYY format"
    record = contacts[name.value]
    record.add_birthday(birthday)
    return 'Birthday added'

@input_error
def when_birthday(args):
    name = Name(args[0])
    record = contacts[name.value]
    result = record.days_to_birthday()
    print(result)
    return f'until the birthday: {result}'

@input_error
def show_all(args) ->str:
    stop = int(input('Input quantity contacts in page'))
    start = 0
    step = stop
    while True:
        page = next(contacts.iterator(start, stop))
        if not page:
            break
        print(page)
        input('Press enter to next page')
        start += step
        stop += step
    return f'End of list'

def unknown_command(*args):
    return 'Invalid command'

COMMANDS = {hello: 'hello', help: 'help', add: 'add', change: 'change', phone: 'phone', show_all: 'show all', delete_phone: 'del phone', add_birthday: 'set birthday', when_birthday: 'birthday'}


def command_handler(input_com: str):
    for func, val in COMMANDS.items():
        if input_com.lower().startswith(val):
            args = input_com.replace(val, '').strip().split(' ')
            return func, args
    return unknown_command, None

def save_contacts():
    with open('contacts.bin', 'wb') as file:
        pickle.dump(contacts, file)
    print('Address book saved successfully!')

def load_contacts():
    try:
        with open('contacts.bin', 'rb') as file:
            global contacts   
            contacts = pickle.load(file)
            print('Address book loaded successfully!')
    except FileNotFoundError:
        print('You dont have contacts')

def main():
    load_contacts()
    while True:
        command = input('>>>')
        EXIT = ['exit', 'goodbye', 'close']
        if command.lower() in EXIT:
            save_contacts()
            print('Good bye')
            break
        func, args = command_handler(command)
        print(func(args))
        
        
        

if __name__ == '__main__':
    main()