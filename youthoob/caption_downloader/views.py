from django.shortcuts import render
import requests
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
import json
import re
import math
import logging
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core import serializers
import httplib2
import os
import sys

from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

#KEYS
googleApiKey = ""

#API URLS
# places_nearbysearch_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


# logger = logging.getLogger(__name__)
# logger.error(your_variable)

def home(request):


    # return render(request, 'caption_downloader/base.html', {"googleApiKey": googleApiKey})
    return render(request, 'caption_downloader/index.html')
