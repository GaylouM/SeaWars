#!/usr/bin/env python

"""exceptions_model.py

Seawars server-side Python App Engine data & ProtoRPC models

"""

import httplib
import endpoints


class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT
