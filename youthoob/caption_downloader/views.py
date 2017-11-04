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
from xml.etree import ElementTree
from datetime import timedelta
from datetime import datetime


avail_languages = {'English':'en', 'German':'de', 'Italian':'it', 'Spanish':'es', 'French':'fr'}

####################################-----API DEPENDENCIES----##############################################################


''' API Libraries'''
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from argparse import Namespace
# from auth import AzureAuthClient

############WATSON################
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 \
  as Features

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


class AzureAuthClient(object):
    """
    Provides a client for obtaining an OAuth token from the authentication service
    for Microsoft Translator in Azure Cognitive Services.
    """

    def __init__(self, client_secret):
        """
        :param client_secret: Client secret.
        """

        self.client_secret = client_secret
        # token field is used to store the last token obtained from the token service
        # the cached token is re-used until the time specified in reuse_token_until.
        self.token = None
        self.reuse_token_until = None

    def get_access_token(self):
        '''
        Returns an access token for the specified subscription.

        This method uses a cache to limit the number of requests to the token service.
        A fresh token can be re-used during its lifetime of 10 minutes. After a successful
        request to the token service, this method caches the access token. Subsequent
        invocations of the method return the cached token for the next 5 minutes. After
        5 minutes, a new token is fetched from the token service and the cache is updated.
        '''

        if (self.token is None) or (datetime.utcnow() > self.reuse_token_until):

            token_service_url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'

            request_headers = {'Ocp-Apim-Subscription-Key': self.client_secret}

            response = requests.post(token_service_url, headers=request_headers)
            response.raise_for_status()

            self.token = response.content
            self.reuse_token_until = datetime.utcnow() + timedelta(minutes=5)

        return self.token


####################################-----HELPER FUNCTIONS----##############################################################

def get_keywords(text):
  natural_language_understanding = NaturalLanguageUnderstandingV1(
  username="4f715217-9f93-4257-b977-c732bbfeecb3",
  password="Fgy3OcTQqmxo",
  version="2017-02-27")

  response = natural_language_understanding.analyze(
    text=text,
    features=[
      Features.Entities(
        emotion=True,
        sentiment=True,
        limit=10
      ),
      Features.Keywords(
        emotion=True,
        sentiment=True,
        limit=10
      )
    ]
  )

  # print(json.dumps(response, indent=2))

  to_ret={}

  for a in response["keywords"]:
    to_ret.update({a['text'] : '#'})

  for a in response["entities"]:
    try:
      to_ret.update({a['text']: a['disambiguation']['dbpedia_resource']})
    except:
      to_ret.update({a['text']: '#'})

  return to_ret


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
summary_api_url = "http://api.smmry.com/&SM_API_KEY=7A401654BB&SM_LENGTH=7&SM_WITH_BREAK"

def summary(text):
    summary_key = "7A401654BB"
    json_in = {"sm_api_input": text}
    r = requests.post(summary_api_url, data=json_in)
    r_json = r.json()
    return(r_json['sm_api_content'])
    '''
    long_article = "Long article text goes here";

    $ch = curl_init("http://api.smmry.com/&SM_API_KEY=XXXXXXXXX&SM_LENGTH=14&SM_WITH_BREAK");
    curl_setopt($ch, CURLOPT_HTTPHEADER, array("Expect:")); // Important do not remove
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, "sm_api_input=".$long_article);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 20);
    curl_setopt($ch, CURLOPT_TIMEOUT, 20);
    $return = json_decode(curl_exec($ch), true);
    curl_close($ch);

    c = pycurl.Curl()
    c.setopt(c.URL, summary_api_url)
    c.setopt(c.HTTPHEADER, ["Expect:"])
    c.setopt(c.POST, 1)

    post_data = {'sm_api_input':text}
    print("l")
    postfields = urlencode(post_data)

    c.setopt(c.POSTFIELDS, postfields)
    c.setopt(c.FOLLOWLOCATION, 1)
    c.setopt(c.RETURNTRANSFER, 1);
    c.setopt(c.CONNECTTIMEOUT, 20);
    c.setopt(c.TIMEOUT, 20);

    c.perform()
    print(c)

    print(r.status_code, r.reason)'''
###################################------Timestamps for youtube locations-----###############################
def timeStamp(list_time):
    """
    Format time stam into `00h00m00s` into the dictionary
    :param list_time: float list of time stamp in second
    :return format_time: dictionary of format time
    """
    format_time = dict()
    i = 0
    for time in list_time:
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        format_time[i] = {"%dh%02dm%02ds" % (h, m, s): time}
        i += 1
    return format_time

def transcribe_video(keyword, video_id):
    xml_url = "http://video.google.com/timedtext?lang=en&v={}".format(video_id)
    response = requests.get(xml_url)

    print(response.content)

    timestamps = list()
    content_subs = response.content
    # keyword = "like"
    # print(response.status_code)
    if response.status_code == 200:
        tree = ElementTree.fromstring(content_subs)

        for node in tree:
            if keyword in node.text:
                print(node.text)
                # print(node.attrib)
                timestamps.append(float(node.attrib["start"]))

        # with open('d.txt', 'w') as f:
        #     for node in tree:
        #         print(node.text)
        #         # print("YO")
        #         f.write(node.text + '\n')
        #         # print("yes")

    return(json.dumps(timeStamp(timestamps), sort_keys=True))


def GetTextAndTranslate(finalToken, toLang, string):
    fromLangCode = " "
    toLangCode = " "
    textToTranslate = " "

    # Get the source language
    fromLangCode = "en"
    # Get the destination language
    toLangCode = toLang
    textToTranslate = string


    # Call to Microsoft Translator Service
    headers = {"Authorization ": finalToken}
    translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&to={}".format(textToTranslate, toLangCode)

    translationData = requests.get(translateUrl, headers = headers)
    # parse xml return values
    translation = ElementTree.fromstring(translationData.text.encode('utf-8'))
    # display translation
    return translation.text

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

    ## For youtube locations
    # transcribe_video(video_id)
    ##

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
      summary_text = summary(subtitle_parsed)
      print(subtitle_parsed)
      keywords = get_keywords(subtitle_parsed)
      json_in = {'token':'True', 'subtitle':subtitle_parsed}
      json_in.update({'keywords':keywords})
      json_in.update({'summary':summary_text})
      json_in.update({'video_id':video_id})      
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

####Exempt CSRF
@csrf_exempt
def timestamp_return(request):
  if request.method == 'POST':
    keyword = request.POST.get('keyword', "Austin")
    video_url = request.POST["url"]
    pos = [(m.start(0), m.end(0)) for m in re.finditer('v=', video_url)]

    video_id = video_url[pos[0][1]:]
    print(keyword)
    output_json = transcribe_video(keyword, video_id)
    return JsonResponse(output_json, safe=False)

####Exempt CSRF
@csrf_exempt
def translate(request):
  if request.method=='POST':  
    client_secret = 'a7867a2553884464b0f657a74f8ef0cc'
    auth_client = AzureAuthClient(client_secret)
    bearer_token = 'Bearer ' + auth_client.get_access_token().strip().decode('utf-8')
    to_trans = "Ken, do you have anything to say for yourself? About this abomination, about this travesty that's in front of me right now? I didn't think so. Hey you guys, this is Austin. This disaster that sits in front of me are some of the most popular PS4 accessories. Now sure, unlike a gaming PC which you can fully customize, a PS4 is pretty much what you get is, well, what you get. However, what I'm curious about is whether any of this stuff is remotely worth it. So to start with, we have the Nyko Intercooler so they claim that this is going to direct hot air away from the console, which in theory is going to be a thing that actually could be really helpful, especially with the old, fat PS4, it could get really loud under load. So one of the things that drew me to the Intercooler is that this actually is fairly well-integrated into the PS4 design, so as you'll see in a second here, it basically just clips right on. And that's pretty much it. So what we can have here is, it looks like one large fan and a couple of smaller fans, and the cool part is, it actually has its own power pass-through so you don't need to turn this thing on or off or run any extra cables, it should just go on the back. This just clips into place, I think. That actually integrates pretty well, I've gotta say. So it's even the sort of same two-toned finish on the back, you still have access to all of your ports and you can still plug in the power cable right here. Now I'm curious how well it'll actually work but it's worth a shot. So if you're rocking the PS4 Slim or Pro then Dobe has you covered. So this is the P4 series multi-functional cooling stand. And we'll see exactly how multi-functional it really is. So the idea here is that not only can you actually get a stand, but you can also mount your controllers as well as some games all in the one stand. So here. (laughs) This is a little bit bigger. This product can decrease the temperature for the PS4 effectively, improving its performance and decreasing the power loss. The power loss? So while these cooling products claim to lower the temperature of the PS4, that really shouldn't give you more performance. The real advantage and the thing that I'm going to be looking for is if temperatures come down, in theory, fan noise should come down and potentially longevity of your PS4 should be improved a little bit, but we'll see. So this is made for everything from the fat PS4 to the Slim to the Pro. So if you have a Slim, it drops in here but if we have the Pro, we should just be able to get it in something like this. Actually, it fits pretty well. So there's nothing really holding it in besides friction. On the bottom, we do have those, wait what? It's really only pulling a little bit of air from here. I mean, they look like reasonable sized fans but how is that gonna drive any significant airflow into the PS4? Next up, we have something a little bit more simple. This is a PS4 USB hub. So as the name suggests, it's pretty straightforward. It turns the two USB ports on the front of the PS4 into five. So this is specifically made for the fat PS4. So in the back, we have a pair of USB ports and on the front, we have one USB 3, which is a pass-through, and four standard USB 2. It should be pretty much as simple as just lining it up and that's it. Again, I appreciate how well this actually fits with the original design, so even with this and the intercooler, it doesn't really look like a Frankenstein. I mean, at least not yet. Now it's time for the big guns. This is the DongCoh Game Bar. Now that name doesn't really tell you much, but what this is going to allow you to do is install a full desktop hard drive into your PS4. Infinity storage, super speed, dissipation, and stability. Man, I am excited for this one. Oh boy, here we go. Oh that looks like a lot. So this is going to require just a little bit of surgery on our PS4. However, it's not going to be bad. So the PS4, as well as the PS4 Slim, PS4 Pro, all have removable hard drives. So what this is going to allow us to do is instead of using a small 2.5 inch drive like from a laptop, to actually use a full desktop drive. This is feeling like a dumber and dumber idea each second. So essentially, this should kind of go and replace this top piece. So this glossy piece right here just pops right off and inside, normally, you would just replace the hard drive here. However, it's gonna be a little bit more involved with this guy. So to start, we're gonna take out the puny 500-gigabyte hard drive in favor of something just a little bit beefier. So to really go all out, we're upgrading this with a four-terabyte hard drive. However, this actually supports up to six terabytes if you really need all the storage you can. On top of that, they actually just announced a new PS4 firmware update that will allow you to actually put games on external USB drives. So if you really wanna get crazy with it, you could put a ton of storage in your PS4. So I just need to set the SATA cable in like that and I can close the whole thing up. So all this is is really just a pass-through. So once we're ready, we just slide it into the standard PS4 slot and screw it in. Alright, here goes nothing. So we want to run all of our power and data through this little slot. Get around here. Okay, that actually kinda works. Now we just need to drop the hard drive in like this and doesn't seem very stable, but besides that, we just have to attach the cable and in theory, we pretty much have a four-terabyte PS4. Uh-oh. It totally fits. (laughs) We have created a monster. Dude, if this is about to work, I'm gonna be so happy. It totally fits! This is, I gotta say, this might be the proudest moment of my entire life, this is a masterpiece of elegant Japanese engineering, or it's all Ken's fault. So one quick firmware update later, we have the ultimate Frankenstein PS4 up and running, and as you can hear, it's kind of loud. We also have the Energizer Xtra Life for the controller. So this is a dock that comes with an external battery that clips on the bottom of the controller so it doesn't really get in the way when you're actually playing a game. First thing, I wanna check to see if our storage is here so yep, there we go, 3.51 terabytes of free space. Now, with so many PS4s shipping with a 500-gigabyte hard drive, it can really get cramped quickly. So this is Uncharted 4 and it looks, well, exactly like Uncharted 4. So what I'm curious about are the temperatures. I can pretty confidently say that this is louder than a normal PS4, but I'm curious whether that loudness actually does anything. So the PS4 with the intercooler and the cooling stand topped out around 49 degrees with the exhaust. However, when you take all that stuff off and run it, it tops out at about 50. That shouldn't be a huge surprise. So the intercooler is just adding additional fans for the exhaust, it's still restricted by how much intake air can actually get into the PS4. Now the cooling stand in theory would actually help things by giving it some fresh air. However, the actual intakes themselves are tiny and really not able to make a big difference. So is any of this worth it? Kind of. So first of all, the Energizer Xtra Life dock is actually not bad. The dock itself is clean, but most importantly, the battery doesn't get in the way, it legitimately does give you extra time on the PS4. Which brings us to the Game Bar. So on one hand, it actually works really well. Once you get past the setup, it's completely seamless, and if you really do need four or six terabytes of storage with your PS4, then it's kind of a no-brainer. However, if you don't need that much storage, it's a lot easier to just install a one- or two-terabyte hard drive, and on top of that, the update to allow you to put games on a USB drive is coming soon. I do really like the USB hub. So with the PS4 only having two USB ports, especially if you have something like PlayStation VR set up, those ports disappear quickly. Which brings us to the intercooler and the cooling stand. Don't buy these. The intercooler, while it actually does integrate pretty well and doesn't really hurt anything, I'm not convinced it actually makes difference whatsoever. Now the stand does give you a few options like being able to dock your controllers, as well as in theory giving you a little bit more cooling, but again, I don't really believe it's actually making any significant difference. As always, all the links you guys need to any of this stuff will be in the description if you wanna go check it out, and I'm curious, what do you think about this monstrosity? Let me know in the comments below and I will catch you in the next one."
    translated = GetTextAndTranslate(bearer_token, "fr", to_trans)
    return JsonResponse({'translated':translated})




