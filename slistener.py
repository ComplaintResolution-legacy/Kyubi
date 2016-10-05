from tweepy import StreamListener
import json, time, sys
import os
from models import Complaint, Complainant
import datetime

class SListener(StreamListener):


    def on_status(self, status):
        timestamp = datetime.datetime.now()
        complaint = Complaint(
            text=status.text,
            timestamp=timestamp,
            status="waiting",
            department_ids=["admin"]
        )

        complainant = Complainant.get_or_create_complainant(
            status.author.screen_name,
            "twitter",
        )
        complainant.save()
        complaint.save()

        complainant.complaint_ids.append(complaint.id)
        complaint.complainant_id = complainant.id
        complainant.save()
        complaint.save()

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        if status_code == 420:
            #returning False in on_data disconnects the stream
            print(self.api.rate_limit_status())
            return False

    def on_timeout(self):
        """Called when stream connection times out"""
        sys.stderr.write("Timeout, sleeping for 60 seconds...\n")
        time.sleep(60)
        return 