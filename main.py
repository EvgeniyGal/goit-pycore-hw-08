import pickle
from datetime import datetime, timedelta
from collections import UserDict
import re
import os


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Invalid phone number format.")
        super().__init__(value)

    @staticmethod
    def validate(phone):
        return re.match(r"^\d{10}$", phone) is not None


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone number not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = (
            f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}"
            if self.birthday
            else ""
        )
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found.")


def get_upcoming_birthdays(address_book):
    upcoming_birthdays = []
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    for record in address_book.values():
        if record.birthday:
            birthday = record.birthday.value
            next_birthday = birthday.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            if today <= next_birthday <= next_week:
                upcoming_birthdays.append(record)

    return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError) as e:
            return str(e)

    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phones(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    phones = [p.value for p in record.phones if p.value is not None]
    return f"Phones: {'; '.join(phones)}" if phones else "No phones found."


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    if record.birthday:
        return f"Birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
    return "No birthday set."


@input_error
def birthdays(args, book: AddressBook):
    upcoming = get_upcoming_birthdays(book)
    if upcoming:
        return "\n".join(
            f"{record.name.value}: {record.birthday.value.strftime('%d.%m.%Y')}"
            for record in upcoming
        )
    return "No upcoming birthdays."


@input_error
def delete_contact(args, book: AddressBook):
    name = args[0]
    book.delete(name)
    return "Contact deleted."


def parse_input(user_input):
    return user_input.split()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print("\n".join(str(record) for record in book.values()))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "delete":
            print(delete_contact(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
