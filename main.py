#!/usr/bin/env python

import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail

"""
main.py -- Udacity conference server-side Python App Engine
    HTTP controller handlers for memcache & task queue access

$Id$

created by wesc on 2014 may 24

"""

__author__ = 'gaylord.marville@gmail.com (Gaylord Marville)'


class SendConfirmationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email confirming Conference creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Game!',            # subj
            'Hi, you have created a following '         # body
            'conference:\r\n\r\n%s' % self.request.get(
                'conferenceInfo')
        )


class SendReminderEmailHandler(webapp2.RequestHandler):
    def get(self):
        """Set Announcement in Memcache."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get(
                'email'),      # to
            '%s has played' % self.request.get(
                'player'),            # subj
            'Hi, you can now reach the game, %s has made his move'
            % self.request.get('player')
        )

app = webapp2.WSGIApplication([
    ('/tasks/send_confirmation_email', SendConfirmationEmailHandler),
    ('/tasks/send_reminder_email', SendReminderEmailHandler),
], debug=True)
