from tweepy import StreamListener
import json, time, sys
import os
from models import Complaint, Complainant, Comment
import datetime

class SListener(StreamListener):

    def _create_comment_from_status(self, status, complaint, prev_comment=None):
        comment = Comment.create_comment(complaint,
            id=str(status.id),
            text=status.text,
            timestamp=datetime.datetime.now(),
            by=status.author.screen_name,
            prev_comment=prev_comment
        )
        comment.save()

        complaint.latest_comment_id = comment.id
        complaint.save()
        
        return comment

    def on_status(self, status):
        print("status arrived")
        if(status.in_reply_to_status_id is None and status.author.screen_name != self.api.auth.get_username()):
            timestamp = datetime.datetime.now()
            complaint = Complaint(
                id=str(status.id),
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

            reply_text = ("Hey @"
                + status.author.screen_name
                + "! "
                + "Thanks for registering your complaint with us. "
                + "We will try to resolve it ASAP.")

            self.api.update_status(reply_text, status.id)

        else:

            replied_to = self.api.get_status(status.in_reply_to_status_id)
            complaint = Complaint.get(status.in_reply_to_status_id_str)
            prev_comment = Comment.get(status.in_reply_to_status_id_str)
            

            if(complaint is not None and complaint.datatype == "Complaint"):

                self._create_comment_from_status(status, complaint)

            elif(prev_comment is not None and complaint.datatype == "Comment"):

                complaint = prev_comment.get_complaint()
                self._create_comment_from_status(status, complaint, prev_comment)

            else:
                complaint = Complaint.get(replied_to.in_reply_to_status_id_str)
                prev_comment = Comment.get(replied_to.in_reply_to_status_id_str)

                if(complaint is not None and complaint.datatype == "Complaint"):
                    self._create_comment_from_status(status, complaint)

                elif(prev_comment is not None and complaint.datatype == "Comment"):
                    complaint = prev_comment.get_complaint()
                    self._create_comment_from_status(status, complaint, prev_comment)


    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

    def on_timeout(self):
        """Called when stream connection times out"""
        sys.stderr.write("Timeout, sleeping for 60 seconds...\n")
        time.sleep(60)
        return 