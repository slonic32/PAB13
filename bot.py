from typing import Callable, List, Tuple
from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle
import copy


class Field:
    """Базовий клас для полів запису"""

    def __init__(self, value: str):
        self.value = value.strip()

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Клас для зберігання імені контакту"""

    def __init__(self, value: str):
        if len(value.strip()) == 0:
            raise ValueError("Name can not be empty!")
        super().__init__(value)


class Phone(Field):
    """Клас для зберігання номера телефону з валідацією формату."""

    def __init__(self, value: str):
        if Phone.isValid(value):
            super().__init__(value)
        else:
            raise ValueError("Phone number must contain 10 digits")

    @staticmethod
    def isValid(phone) -> bool:
        """Валідація телефону - 10 цифр"""
        if re.fullmatch(r"\d{10}", phone):
            return True
        else:
            return False

    def __eq__(self, value: object) -> bool:
        """=="""
        return self.value == value.value

    def edit(self, new_value: str) -> None:
        """edit phone"""
        if Phone.isValid(new_value):
            self.value = new_value.strip()
        else:
            raise ValueError("Phone number must contain 10 digits")


class Birthday(Field):
    """Клас для зберігання дня народження."""

    def __init__(self, value: str):
        try:
            # Перетворюємо рядок на об'єкт datetime
            birthday = datetime.strptime(value.strip(), "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        # перевірка на коректність дати
        if birthday > datetime.today().date():
            raise ValueError("Birthday from the future is not allowed!")
        self.value = birthday

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Record:
    """Клас для зберігання інформації про контакт."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str) -> None:
        """Додавання номера телефону."""
        self.phones.append(Phone(phone))

    def find_phone(self, phone: str) -> str:
        """Пошук телефону у записі."""
        find_phone = Phone(phone)
        for p in self.phones:
            if p == find_phone:
                return p
        raise ValueError(f"Phone number {phone} not found")

    def remove_phone(self, phone: str) -> None:
        """Видалення номера телефону."""
        self.phones.remove(self.find_phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Редагування телефону."""
        self.find_phone(old_phone).edit(new_phone)

    def add_birthday(self, birthday: str) -> None:
        """Додавання дня народження."""
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}{birthday_str}"


class Note:
    """Клас для зберігання нотаток."""

    _id_counter = 1  # останній ID

    def __init__(self, content: str, tags: list[str] = None):
        if len(content.strip()) == 0:
            raise ValueError("Note can not be empty!")
        self.id = Note._id_counter
        Note._id_counter += 1
        self.content = content.strip()
        self.timestamp = datetime.now()
        self.tags = tags if tags else []

    def __str__(self) -> str:
        tags_str = ", ".join(self.tags) if self.tags else "No tags"
        return f"Note ID: {self.id}, Created: {self.timestamp.strftime('%d.%m.%Y %H:%M:%S')}\nContent: {self.content}\nTags: {tags_str}"

    def edit(self, new_content: str) -> None:
        """Редагування вмісту нотатки."""
        if len(new_content.strip()) == 0:
            raise ValueError("Note can not be empty!")
        self.content = new_content.strip()

    def edit_tags(self, new_tags: list[str] = None) -> None:
        """Редагування тегів нотатки."""
        if new_tags is not None:
            self.tags = sorted([tag.strip() for tag in new_tags])
        else:
            self.tags = []


class AddressBook(UserDict):
    """Клас для зберігання та управління записами в адресній книзі."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notes: List[Note] = []

    def add_record(self, record: Record) -> None:
        """Додавання запису до книги."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        """Пошук запису за ім'ям."""
        if name in self.data:
            return self.data[name]
        return None

    def delete(self, name: str) -> None:
        """Видалення запису за ім'ям."""
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Record with name {name} not found")

    def get_upcoming_birthdays(self) -> list:
        """Отримання списку користувачів, яких потрібно привітати на наступному тижні."""
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if today <= birthday_this_year <= today + timedelta(days=7):
                    upcoming_birthdays.append(
                        {
                            "name": str(record.name),
                            "congratulation_date": birthday_this_year.strftime(
                                "%d.%m.%Y"
                            ),
                        }
                    )

        return upcoming_birthdays

    # нотатки

    def add_note(self, content: str) -> Note:
        """Додавання нової нотатки."""
        note = Note(content)
        self.notes.append(note)
        return note

    def find_notes(self, search_term: str) -> List[Note]:
        """Пошук нотаток за змістом."""
        return [
            note for note in self.notes if search_term.lower() in note.content.lower()
        ]

    def search_notes_by_tag(self, tag: str) -> List[Note]:
        """Пошук нотаток за тегом."""
        return [note for note in self.notes if tag in note.tags]

    def sort_notes_by_tag(self) -> List[Note]:
        return sorted(self.notes, key=lambda note: note.tags)

    def get_note_by_id(self, note_id: int) -> Note:
        """Отримання нотатки за ID."""
        for note in self.notes:
            if note.id == note_id:
                return note
        raise ValueError(f"Note with ID {note_id} not found.")

    def edit_note(self, note_id: int, new_content: str) -> None:
        """Редагування нотатки за ID."""
        note = self.get_note_by_id(note_id)
        note.edit(new_content)

    def edit_tags(self, note_id: int, tags: List[str]) -> None:
        """Редагування нотатки за ID."""
        note = self.get_note_by_id(note_id)
        note.edit_tags(tags)

    def delete_note(self, note_id: int) -> None:
        """Видалення нотатки за ID."""
        note = self.get_note_by_id(note_id)
        self.notes.remove(note)

    # нові методи копіювання
    def __copy__(self):
        new_ab = AddressBook()
        new_ab.data = self.data.copy()
        new_ab.notes = self.notes.copy()
        return new_ab

    def __deepcopy__(self, memo):
        new_ab = AddressBook()
        new_ab.data = copy.deepcopy(self.data, memo)
        new_ab.notes = copy.deepcopy(self.notes, memo)
        return new_ab


def input_error(func: Callable) -> Callable:
    """Декоратор для обробки помилок"""

    def inner(*args, **kwargs) -> str:
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter the correct arguments."
        except (FileNotFoundError, FileExistsError):
            return "File error!"
        except e:
            return str(e)

    return inner


@input_error
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


@input_error
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
            # Оновлення id для Note
            if book.notes:
                max_id = max(note.id for note in book.notes)
                Note._id_counter = max_id + 1
            return book
    except FileNotFoundError:
        # Повертаємо нову адресу книгу, якщо файл не знайдено
        return AddressBook()


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """parse input"""
    parts = user_input.split()
    cmd = parts[0].strip().lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return cmd, args


@input_error
def add_contact(args: List[str], contacts: AddressBook) -> str:
    """add contact"""
    if len(args) < 2:
        raise ValueError("Not enough arguments provided.")

    name = " ".join(args[:-1]).strip()
    phone = args[-1].strip()
    record = contacts.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        contacts.add_record(record)
    return f"Contact '{name}' added with phone number {phone}."


@input_error
def change_contact(args: List[str], contacts: AddressBook) -> str:
    """edit contact"""
    if len(args) < 3:
        raise ValueError("Not enough arguments provided.")

    name = " ".join(args[:-2]).strip()
    old_phone = args[-2].strip()
    new_phone = args[-1].strip()
    record = contacts.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
    else:
        raise KeyError(f"Record with name {name} not found")
    return f"Contact '{name}' updated to phone number {new_phone}."


@input_error
def show_phone(args: List[str], contacts: AddressBook) -> str:
    """show contact"""
    if len(args) == 0:
        raise IndexError("No contact name provided.")

    name = " ".join(args).strip()
    record = contacts.find(name)
    if record:
        phones = record.phones
    else:
        raise KeyError(f"Record with name {name} not found")

    return f"{name}'s phone number is {'; '.join(str(p) for p in phones).strip()}."


@input_error
def show_all(contacts: AddressBook) -> str:
    """show all contacts"""
    if not contacts:
        return "No contacts found."

    result = "All contacts:\n"
    for _, record in contacts.data.items():
        result += f"{str(record)}\n"
    return result.strip()


@input_error
def add_birthday(args: List[str], contacts: AddressBook) -> str:
    """Add birthday to contact."""
    if len(args) < 2:
        raise ValueError("Not enough arguments provided.")
    name = " ".join(args[:-1]).strip()
    birthday = args[-1].strip()
    record = contacts.find(name)
    if record:
        record.add_birthday(birthday)
    else:
        record = Record(name)
        record.add_birthday(birthday)
        contacts.add_record(record)
    record.add_birthday(birthday)
    return f"Added birthday {birthday} for {name}."


@input_error
def show_birthday(args: List[str], contacts: AddressBook) -> str:
    """Show birthday for a contact."""
    if len(args) == 0:
        raise IndexError("No contact name provided.")

    name = " ".join(args).strip()
    record = contacts.find(name)
    if record is None:
        raise KeyError(f"Record with name {name} not found.")
    if record.birthday:
        return f"{name}'s birthday is on {record.birthday}."
    return f"{name} does not have a birthday recorded."


@input_error
def birthdays(contacts: AddressBook) -> str:
    """Show upcoming birthdays."""
    upcoming_birthdays = contacts.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays within the next week."
    return "\n".join(
        [
            f"{entry['name']} - {entry['congratulation_date']}"
            for entry in upcoming_birthdays
        ]
    )


# команди для роботи з нотатками


@input_error
def add_note(args: List[str], contacts: AddressBook) -> str:
    """Додавання нової нотатки."""
    if not args:
        raise ValueError("Note is empty!  Usage: add-note <some_text>")
    content = " ".join(args).strip()
    note = contacts.add_note(content)
    return f"Added note with ID {note.id}."


@input_error
def find_note(args: List[str], contacts: AddressBook) -> str:
    """Пошук нотаток за змістом."""
    if not args:
        raise ValueError("Nothing to find! Usage: find-note <some_text>")
    search_term = " ".join(args).strip()
    found_notes = contacts.find_notes(search_term)
    if not found_notes:
        return "No notes found."
    result = "Found notes:\n"
    for note in found_notes:
        result += f"{str(note)}\n"
    return result.strip()


@input_error
def find_note__by_tag(args: List[str], contacts: AddressBook) -> str:
    """Пошук нотаток за тегом."""
    if not args:
        raise ValueError("Nothing to find! Usage: find-note-by-tag <tag>")
    search_tag = " ".join(args).strip()
    found_notes = contacts.search_notes_by_tag(search_tag)
    if not found_notes:
        return "No notes found."
    result = "Found notes:\n"
    for note in found_notes:
        result += f"{str(note)}\n"
    return result.strip()


@input_error
def view_all_notes(contacts: AddressBook) -> str:
    """Показ усіх нотаток."""
    if not contacts.notes:
        return "No notes available."
    return "\n\n".join(str(note) for note in contacts.notes)


@input_error
def sort_notes_by_tag(contacts: AddressBook) -> str:
    """Показ усіх нотаток з сортуванням за тегами."""
    if not contacts.notes:
        return "No notes available."
    return "\n\n".join(str(note) for note in contacts.sort_notes_by_tag())


@input_error
def view_note_by_id(args: List[str], contacts: AddressBook) -> str:
    """Показ нотатки по ID."""
    if len(args) != 1:
        raise ValueError("Invalid arguments. Usage: note-by-id <id>")
    try:
        note_id = int(args[0])
    except ValueError:
        raise ValueError("Note ID must be an integer.")

    found_note = contacts.get_note_by_id(note_id)
    if not found_note:
        return f"No note found with ID {note_id}."
    result = "Found note:\n" f"{str(found_note)}\n"
    return result.strip()


@input_error
def edit_note(args: List[str], contacts: AddressBook) -> str:
    """Редагування нотатки."""
    if len(args) < 2:
        raise ValueError(
            "Not enough arguments provided. Usage: edit-note <id> <new_content>"
        )
    try:
        note_id = int(args[0])
    except ValueError:
        raise ValueError("Note ID must be an integer.")
    new_content = " ".join(args[1:]).strip()
    contacts.edit_note(note_id, new_content)
    return f"Note with ID {note_id} has been updated."


@input_error
def edit_tags(args: List[str], contacts: AddressBook) -> str:
    """Редагування нотатки."""
    if len(args) < 1:
        raise ValueError(
            "Not enough arguments provided. Usage: edit-tags <id> <new_tag1, tag2, tag3...>"
        )
    try:
        note_id = int(args[0])
    except ValueError:
        raise ValueError("Note ID must be an integer.")
    tags_str = " ".join(args[1:]).strip()
    new_tags = tags_str.split(",")
    contacts.edit_tags(note_id, new_tags)
    return f"Note with ID {note_id} has been updated."


@input_error
def delete_note(args: List[str], contacts: AddressBook) -> str:
    """Видалення нотатки за ID."""
    if len(args) != 1:
        raise ValueError("Invalid arguments. Usage: delete-note <id>")
    try:
        note_id = int(args[0])
    except ValueError:
        raise ValueError("Note ID must be an integer.")
    contacts.delete_note(note_id)
    return f"Note with ID {note_id} has been deleted."


def show_help() -> str:
    """print help"""
    help_text = """
    Available commands:
    - hello: Greet the bot.
    - add <name> <phone>: Add a new contact.
    - change <name> <old_phone> <new_phone>: Change an existing contact's phone number.
    - phone <name>: Show the phone number(s) of a contact.
    - all: Show all contacts.
    - add-birthday <name> <DD.MM.YYYY>: Add birthday for a contact.
    - show-birthday <name>: Show birthday of a contact.
    - birthdays: Show upcoming birthdays within the next week.
    - add-note <note_content>: Add a new text note.
    - find-note <search_term>: Find notes containing the search term.
    - find-note-by-tag <tag>: Find notes containing the search term.
    - all-notes: Show all notes.
    - sort-notes-by-tag: Show all notes sorted by tags.
    - note-by-id <id>: Show note with specified ID.
    - edit-note <note_id> <new_content>: Edit an existing note.
    - edit-tags <id> <new_tag1, tag2, tag3...>: Edit note's tags
    - delete-note <note_id>: Delete a note by its ID.
    - close or exit: Exit the bot.
    - help: Show this help message.
    """
    return help_text.strip()


def main() -> None:
    """main"""
    # Завантаження адресної книги з файлу
    contacts = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # Збереження даних перед виходом
            save_data(contacts)
            print("Good bye!")
            break
        elif command == "hello":
            print("Hello! How can I assist you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(contacts))
        elif command == "add-note":
            print(add_note(args, contacts))
        elif command == "find-note":
            print(find_note(args, contacts))
        elif command == "find-note-by-tag":
            print(find_note__by_tag(args, contacts))
        elif command == "edit-note":
            print(edit_note(args, contacts))
        elif command == "edit-tags":
            print(edit_tags(args, contacts))
        elif command == "delete-note":
            print(delete_note(args, contacts))
        elif command == "all-notes":
            print(view_all_notes(contacts))
        elif command == "sort-notes-by-tag":
            print(sort_notes_by_tag(contacts))
        elif command == "note-by-id":
            print(view_note_by_id(args, contacts))
        elif command == "help":
            print(show_help())
        else:
            print("Invalid command. Type 'help' to see available commands.")


if __name__ == "__main__":
    main()
