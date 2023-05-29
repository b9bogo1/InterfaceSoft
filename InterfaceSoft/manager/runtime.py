from threading import Thread
import requests
import json
import time
import schedule
from InterfaceSoft.local_configs import get_node, get_emails_white_list

NODE = get_node()
EMAILS_WHITE_LIST = get_emails_white_list()
URI = f"http://{NODE['ip']}:{NODE['port']}/send-email"
headers = {"Content-Type": "application/json"}


def job():
    for item in EMAILS_WHITE_LIST:
        email_sent = requests.post(URI, data=json.dumps(item), headers=headers)
        time.sleep(15)
        if email_sent.status_code != 200:
            print(f"runtime not able to sent email")


schedule.every().day.at("05:00").do(job)
# schedule.every(5).seconds.do(job)
# schedule.every(2).minutes.do(job)


class ManageNetworkDataFlow(Thread):
    """A class that manages the network data flow between different nodes."""

    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        """A method that runs in a loop and checks the status and data of each node."""

        while True:
            schedule.run_pending()
            time.sleep(1)
