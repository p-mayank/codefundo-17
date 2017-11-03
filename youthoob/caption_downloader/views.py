####################################-----DJANGO IMPORTS----##############################################################

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
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import pycurl


####################################-----API DEPENDENCIES----##############################################################


''' API Libraries'''
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


####################################-----HELPER FUNCTIONS----##############################################################


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
  message=MISSING_CLIENT_SECRETS_MESSAGE)
  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    return False

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
  return subtitle

def build_file(token_id):
  time_curr = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
  null = None
  false = False
  print(token_id)
  to_write = {"_module": "oauth2client.client", "user_agent": null, "token_expiry": "time_curr", "_class": "OAuth2Credentials", "refresh_token": null, "token_response": {"access_token": token_id, "token_type": "Bearer", "expires_in": 3600}, "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "id_token_jwt": null, "token_info_uri": "https://www.googleapis.com/oauth2/v3/tokeninfo", "access_token": token_id, "id_token": null, "scopes": ["https://www.googleapis.com/auth/youtube.force-ssl"], "client_secret": "NTy966jpbkL5MwAz4e5v78RK", "token_uri": "https://accounts.google.com/o/oauth2/token", "client_id": "518513510656-6c1kjfcctiqpj65nab1ba4mr5mjhj1jg.apps.googleusercontent.com", "invalid": false}
  #ext = json.loads(to_write)
  # captions_json_storage_link = 'cfd/youtube-v3-api-captions.json'

  with open('manage.py-oauth2.json', 'w') as f:
    # print("YO")
    json.dump(to_write, f)
    # print("yes")

def parse_subtitle(subtitle):
  n = [(m.start(0), m.end(0)) for m in re.finditer('"', subtitle)]
  subtitle = subtitle[n[0][1]:]
  x = subtitle.split('\\n')
  x = filter(None, x)
  out=[]
  for a in x:
      if(a[0]!='0'):
          out.append(a)
  #print(out)
  out = ' '.join(out)
  n = [(m.start(0), m.end(0)) for m in re.finditer('"', out)]
  out = out[:n[0][0]]
  summary(out)
  return out

####################################-----SUMMARY------#################################################
summary_api_url = "http://api.smmry.com/"

def summary(text):
    summary_key = "7A401654BB"
    # json_in = {"SM_API_KEY": summary_key, "SM_LENGTH": 7, "sm_api_input": text}
    # r = requests.post(summary_api_url, json=json_in)
    # r_json = r.json()
    # print(r_json["sm_api_content"])
    # long_article = "Long article text goes here";
    #
    # $ch = curl_init("http://api.smmry.com/&SM_API_KEY=XXXXXXXXX&SM_LENGTH=14&SM_WITH_BREAK");
    # curl_setopt($ch, CURLOPT_HTTPHEADER, array("Expect:")); // Important do not remove
    # curl_setopt($ch, CURLOPT_POST, true);
    # curl_setopt($ch, CURLOPT_POSTFIELDS, "sm_api_input=".$long_article);
    # curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    # curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    # curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 20);
    # curl_setopt($ch, CURLOPT_TIMEOUT, 20);
    # $return = json_decode(curl_exec($ch), true);
    # curl_close($ch);

    # c = pycurl.Curl()
    # c.setopt(c.URL, summary_api_url)
    # c.setopt(c.HTTPHEADER, ["Expect:"])
    # c.setopt(c.POST, 1)
    # c.setopt(c.POSTFIELDS, "sm_api_input="+text)
    # c.perform()
    # print(c)
    print(r.status_code, r.reason)
####################################-----VIEWS----##############################################################

def home(request):
  return render(request, 'caption_downloader/client_side.html')

####Exempt CSRF
@csrf_exempt
def indexer(request):
  if request.method == 'POST':
    video_url = request.POST["url"]
    pos = [(m.start(0), m.end(0)) for m in re.finditer('v=', video_url)]

    # logger = logging.getLogger(__name__)
    # logger.error(os.getcwd())
    print(video_url)
    print(pos)
    video_id = video_url[pos[0][1]:]

    args = Namespace(auth_host_name='localhost', auth_host_port=[8080, 8090], noauth_local_webserver=False, logging_level='ERROR')
    print("args")
    youtube = get_authenticated_service(args)
    print(youtube)
    if(youtube is False):
      return JsonResponse({'token':'False'})
    try:
      caption_id = list_captions(youtube, video_id)
      subtitle = download_caption(youtube, caption_id, 'sbv')
      subtitle_parsed = parse_subtitle(str(subtitle))
      json_in = {'token':'True', 'subtitle':subtitle_parsed}
      return JsonResponse(json_in)
    except:
      return JsonResponse({'token':'False'})

####Exempt CSRF
@csrf_exempt
def build_token(request):
  if request.method == 'POST':
    token_id = request.POST['access_token']
    print(token_id)
    build_file(token_id)
    return JsonResponse({'token':'True'})
