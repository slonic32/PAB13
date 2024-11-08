# PAB13

Personal Assistant Bot

## Dependencies:

Python 3.10

## Install locally

Create a symlink in user bin directory:

### On Mac/Linux:

Open terminal, CD to project installation dir and run:

```
sudo ln -s $PWD/bot.py /usr/local/bin/bot.py
```

Make sure `/usr/local/bin` is in PATH, otherwise change above cmd to point to bin folder from PATH.
Reopen terminal, launch bot.py from anywhere:

```
macbookpro1:~ yuriy$ bot.py
Welcome to the assistant bot!
```

## Usage

Launch bot.py and type one of the following command when prompted (On MacOS/Linux You can use TAB key for autocompletion
of the commands and arrow keys for history):

```
Available commands:
    - hello: Greet the bot.
    - add <name> <phone>: Add a new contact.
    - edit <name>: Rename existing contact.
    - delete <name>: Delete existing contact.
    - find <phone/email>: Find first matching contact by phone or email.
    - change-phone <name> <old_phone> <new_phone>: Change an existing contact's phone number.
    - change-email <name> <old_email> <new_email>: Change an existing contact's email address.
    - phone <name>: Show the phone number(s) of a contact.
    - email <name>: Show the email address(es) of a contact.
    - all: Show all contacts.
    - add-birthday <name> <DD.MM.YYYY>: Add birthday for a contact.
    - add-email <name> <email@domain>: Add email address for a contact.
    - show-birthday <name>: Show birthday of a contact.
    - birthdays <days>: Show upcoming birthdays within the next given days.
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
```
