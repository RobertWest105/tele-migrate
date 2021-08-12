# Tele-migrate: Telegram Group Migration Script

A python script which can either send a message to all users in a chosen source group and not in a chosen destination group or save the details of such users to a file.

Upon running the script with either command, it will show a list of all groups you have access to and ask for the source and destination groups.

Ensure the `apiID`, `apiHash` and `phone` variables are set to the correct values for your Telegram account before running the script. You can find out how to get an API ID and API Hash at https://core.telegram.org/api/obtaining_api_id.

# Usage

`python(3) tele-migrate.py [command]`

Available commands:
- save: store to a file the details of all users in source group and not in destination group
- message: send a message to all users in source group and not in destination group
