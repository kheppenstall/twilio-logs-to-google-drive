import csv
import datetime
from twilio.rest import Client
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import date
from datetime import datetime as dt


class Service:

    twilio_logs_folder_name = "twilio_logs"

    def __init__(self, account_sid, auth_token, pii_enabled):
        gauth = GoogleAuth()
        self.drive = GoogleDrive(gauth)
        self.twilio_client = Client(account_sid, auth_token)
        self.pii_enabled = pii_enabled

    def save_data(self, start):
        now = date.today()

        # Create root twilio_logs folder.
        fileList = self.drive.ListFile(
            {'q': "'root' in parents and trashed=false"}).GetList()
        twilio_logs_folder_id = ''
        for file in fileList:
            if(file['title'] == self.twilio_logs_folder_name):
                twilio_logs_folder_id = file['id']

        if twilio_logs_folder_id == '':
            metadata = {
                "title": self.twilio_logs_folder_name,
                "mimeType": 'application/vnd.google-apps.folder',
            }
            f = self.drive.CreateFile(metadata)
            f.Upload()
            twilio_logs_folder_id = f.get('id')

        # Create folder for current log upload.
        metadata = {
            "title": dt.now().strftime("%Y.%m.%d.%H.%M") + ".upload",
            "mimeType": 'application/vnd.google-apps.folder',
            "parents": [{"kind": "drive#parentReference", "id": twilio_logs_folder_id}]
        }
        f = self.drive.CreateFile(metadata)
        f.Upload()
        folder_id = f.get('id')

        # Upload logs to drive.
        until = first_day_of_next_month(now.month, now.year)
        while (start < until):
            self.save_call_data(start.month, start.year, folder_id)
            self.save_message_data(start.month, start.year, folder_id)
            start = first_day_of_next_month(start.month, start.year)

    def get_call_data(self, month, year):
        # Call properties - https://www.twilio.com/docs/voice/api/call-resource#call-properties
        start_time_after = first_day_of_month(month, year)
        start_time_before = first_day_of_next_month(month, year)

        data = []
        for call in self.twilio_client.calls.list(start_time_before=start_time_before, start_time_after=start_time_after):
            d = {}

            # Not PII
            d["sid"] = call.sid
            d["forwarded_from"] = call.forwarded_from
            d["start_time"] = format_date(call.start_time)
            d["end_time"] = format_date(call.end_time)
            d["duration"] = call.duration
            d["direction"] = call.direction
            d["date_updated"] = format_date(call.date_updated)
            d["date_created"] = format_date(call.date_created)
            d["api_version"] = call.api_version
            d["account_sid"] = call.account_sid
            d["price"] = call.price
            d["price_unit"] = call.price_unit
            d["phone_number_sid"] = call.phone_number_sid
            d["parent_call_sid"] = call.parent_call_sid
            d["group_sid"] = call.group_sid
            d["direction"] = call.direction
            d["annotation"] = call.annotation
            d["trunk_sid"] = call.trunk_sid
            d["uri"] = call.uri
            d["queue_time"] = call.queue_time
            d["status"] = call.status

            # PII
            if self.pii_enabled:
                d["caller_name"] = call.caller_name
                d["answered_by"] = call.answered_by
                d["to_formatted"] = call.to_formatted
                d["to"] = call.to_formatted
                d["from_"] = call.from_
                d["from_formatted"] = call.from_formatted
                d["forwarded_from"] = call.forwarded_from

            data.append(d)

        return data

    def save_call_data(self, month, year, folder_id):
        data = self.get_call_data(month, year)
        if len(data) == 0:
            return

        filename = str(year) + "." + str(month) + ".calls.csv"
        save_csv(filename, data)
        self.save_to_drive(filename, folder_id)

    def get_message_data(self, month, year):
        # Message properties - https://www.twilio.com/docs/sms/api/message-resource
        date_sent_after = first_day_of_month(month, year)
        date_sent_before = first_day_of_next_month(month, year)

        data = []
        for message in self.twilio_client.messages.list(date_sent_before=date_sent_before, date_sent_after=date_sent_after):
            d = {}

            # Not PII
            d["sid"] = message.sid
            d["direction"] = message.direction
            d["date_updated"] = format_date(message.date_updated)
            d["date_created"] = format_date(message.date_created)
            d["date_sent"] = format_date(message.date_sent)
            d["api_version"] = message.api_version
            d["direction"] = message.direction
            d["error_code"] = message.error_code
            d["error_message"] = message.error_message
            d["account_sid"] = message.account_sid
            d["num_segments"] = message.num_segments
            d["num_media"] = message.num_media
            d["messaging_service_sid"] = message.messaging_service_sid
            d["price"] = message.price
            d["price_unit"] = message.price_unit
            d["status"] = message.status
            d["uri"] = message.uri

            # PII
            if self.pii_enabled:
                d["to"] = message.to
                d["from_"] = message.from_
                d["body"] = message.body.replace('\n', '').replace('\t', '')

            data.append(d)

        return data

    def save_message_data(self, month, year, folder_id):
        data = self.get_message_data(month, year)
        if len(data) == 0:
            return

        filename = str(year) + "." + str(month) + ".messages.csv"
        save_csv(filename, data)
        self.save_to_drive(filename, folder_id)

    def save_to_drive(self, filename, folder_id):
        metadata = {
            "name": filename,
            "mimeType": "text/csv",
            "parents": [{"kind": "drive#parentReference", "id": folder_id}]
        }
        f = self.drive.CreateFile(metadata=metadata)
        f.SetContentFile(filename)
        f.Upload()


def first_day_of_month(month, year):
    return datetime.date(year, month, 1)


def first_day_of_next_month(month, year):
    if month == 12:
        return datetime.date(year+1, 1, 1)

    return datetime.date(year, month+1, 1)


def save_csv(filename, data):
    fieldnames = data[0].keys()
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(data)


def format_date(d):
    if d == None:
        return ''
    return d.isoformat('T')
