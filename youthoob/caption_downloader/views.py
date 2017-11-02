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
from argparse import Namespace

# YOUTUBE API
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  with open("youtube-v3-api-captions.json", "r") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

def list_captions(youtube, video_id):
  results = youtube.captions().list(
    part="snippet",
    videoId=video_id
  ).execute()

  for item in results["items"]:
    id = item["id"]
    name = item["snippet"]["name"]
    language = item["snippet"]["language"]
    print("Caption track '%s(%s)' in '%s' language." % (name, id, language))
    #To extract ID
    if(language=='en' and item["snippet"]["trackKind"]=='standard'):
        return(id)

def download_caption(youtube, caption_id, tfmt):
  subtitle = youtube.captions().download(
    id=caption_id,
    tfmt=tfmt
  ).execute()

  print("%s" % (subtitle))

def home(request):

    # return render(request, 'caption_downloader/base.html', {"googleApiKey": googleApiKey})
    return render(request, 'caption_downloader/index.html')

def indexer(request):

    if request.method == 'POST':
        video_url = request.POST["url"]
        pos = [(m.start(0), m.end(0)) for m in re.finditer('v=', video_url)]
        video_id = video_url[pos[0][1]:]
        args = Namespace(auth_host_name='localhost', auth_host_port=[8080, 8090], noauth_local_webserver=False, logging_level='ERROR')
        youtube = get_authenticated_service(args)
        caption_id = list_captions(youtube, video_id)
        download_caption(youtube, caption_id, 'srt')
        
        json_in = {}
        return JsonResponse(json_in)
