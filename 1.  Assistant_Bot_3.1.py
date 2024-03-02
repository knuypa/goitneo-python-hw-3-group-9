from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)
    
    @staticmethod
    def validate(phone_number):
        return phone_number.isdigit() and len(phone_number) == 10

class Birthday(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Birthday must be in DD.MM.YYYY format")
        super().__init__(value)
        
    @staticmethod
    def validate(birthday):
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None if birthday is None else Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        found = False
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                found = True
                break
        return found

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = ', '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {str(self.birthday)}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_birthdays_per_week(self):
        today = datetime.now()
        one_week_later = today + timedelta(days=7)
        birthdays_this_week = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                if today <= birthday_date.replace(year=today.year) <= one_week_later:
                    birthdays_this_week.append(record.name.value)
        return birthdays_this_week

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def input_error(handler):
    def inner(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except Exception as e:
            return str(e)
    return inner

@input_error
def add_contact(book, args):
    if len(args) < 2:
        raise ValueError("Error: Missing name or phone number.")
    name, phone = args
    if name in book:
        record = book[name]
        record.add_phone(phone)
        return "Phone number added to the existing contact."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."

@input_error
def change_contact(book, args):
    if len(args) < 3:
        raise ValueError("Error: Missing name, old phone, or new phone number.")
    name, old_phone, new_phone = args
    if name in book:
        record = book[name]
        if record.edit_phone(old_phone, new_phone):
            return "Contact phone updated."
        else:
            return "Old phone number not found."
    else:
        return "Contact not found."

@input_error
def show_phone(book, args):
    if not args:
        raise ValueError("Error: Missing name.")
    name = args[0]
    if name in book:
        return str(book[name])
    else:
        return "Contact not found."

@input_error
def show_all(book, args):
    if not book:
        return "No contacts saved."
    return '\n'.join(str(record) for record in book.values())

@input_error
def add_birthday(book, args):
    if len(args) < 2:
        raise ValueError("Error: Missing name or birthday.")
    name, birthday = args
    if name in book:
        record = book[name]
        record.add_birthday(birthday)
        return "Birthday added to the contact."
    else:
        return "Contact not found."

@input_error
def show_birthday(book, args):
    if not args:
        raise ValueError("Error: Missing name.")
    name = args[0]
    if name in book and book[name].birthday:
        return f"Birthday of {name}: {book[name].birthday}"
    else:
        return "Birthday not found for this contact."

@input_error
def show_birthdays(book, args):
    birthdays_next_week = book.get_birthdays_per_week()
    if birthdays_next_week:
        return "Birthdays next week:\n" + "\n".join(birthdays_next_week)
    else:
        return "No birthdays next week."

def handle_command(command, book, args):
    commands = {
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": show_birthdays,
        "hello": lambda book, args: "How can I help you?"
    }
    if command in commands:
        return commands[command](book, args)
    else:
        return "Invalid command."

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if user_input.lower() in ["exit", "close"]:
            print("Goodbye!")
            break
        command, args = parse_input(user_input)
        print(handle_command(command, book, args))

if __name__ == "__main__":
    main()