import csv
from datetime import date
import getopt
import sys
from service import Service

# Parse args
long_options = ["twilio_account_sid=", "twilio_auth_token=", "start=", "pii"]
full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]

try:
    arguments, values = getopt.getopt(argument_list, [], long_options)
except getopt.error as err:
    print(str(err))
    sys.exit(2)

pii_enabled = False
for current_argument, current_value in arguments:
    if current_argument == "--twilio_account_sid":
        account_sid = current_value
    elif current_argument == "--twilio_auth_token":
        auth_token = current_value
    elif current_argument == "--start":
        start = date.fromisoformat(current_value)
    elif current_argument == "pii":
        pii_enabled = True

s = Service(account_sid, auth_token, pii_enabled)
s.save_data(start)
