# Twilio Log Exporter to Google Drive

## Overview

The twilio log exporter tool downloads logs from Twilio for calls and messages
via the the Twilio export
[API](https://support.twilio.com/hc/en-us/articles/223183588-Exporting-SMS-and-Call-Logs)
and saves them to Google Drive as CSVs.

CSVs are organized per month and type. For example, if the tool is run for the
past 12 months then there will be 24 CSVs - one per month for SMS and call logs.
If the month has no logs, no CSV is saved. CSVs are saved in google drive under
the folder `twilio_logs/<<current_date_time>>` folder. Full logs are downloaded
each time the tool is run. Copies of the CSV files are also saved locally to the
current working directory.

Note that the tool does not downloads logs that include PII by default. To enable downloading PII then pass the `-pii` flag.

## Dependencies
* [Python 3](https://www.python.org/downloads/)
* [pydrive python package](https://pypi.org/project/PyDrive/) (`pip install pydrive`)
* [twilio python package](https://www.twilio.com/docs/libraries/python)
  (`pip install twilio`)
* [Twilio account sid and authorization token](https://support.twilio.com/hc/en-us/articles/223136027-Auth-Tokens-and-How-to-Change-Them)
* `client_secrets.json` file for
  [Google Auth](https://pythonhosted.org/PyDrive/quickstart.html#authentication)

## Usage

* `git clone https://github.com/kheppenstall/twilio-logs-to-google-drive.git`
* `cd twilio-logs-to-google-drive`
*
  `python migrate_logs.py --twilio_account_sid<<sid>> --twilio_auth_token=<<token>> --start=<<YYYY-MM-DD>>`

### Parameters
* `twilio_account_sid` - account sid from Twilio console
* `twilio_auth_token` - auth token from Twilio console
* `start` - beginning date for log downloads (`YYYY-MM-DD`)
* `pii` - include personally identifiable information in downloaded logs

### Example

`python migrate_logs.py --twilio_account_sid=ACXXXXX --twilio_auth_token=XXXXXX--start=2019-01-01 --pii`
