[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

##CodeFunDo Campus Hackathon '17
* Application Resources

## About
Youthoob is a youtube-based web-application which uses Natural language processing and machine learning intelligence to extract summary out of a youtube video, which can be really helpful in identifying click-baits. It also uses microsoft azure services to translate the youtube video into different languages, and is smart enough to pause the video when the user is out of sight.

#SERVER APDRESS: 52.170.30.130 (Azure-SSD)

##Deployment Instructions
# Create Mysql Database with Name 'youthoob'
# Change Accrodingly or Change in 'settings.py'
```
  'NAME': 'youthoob',
  'USER': 'root',
  'PASSWORD': 'roshandashnovember11',
  'HOST': '127.0.0.1',
  'PORT': '3306',
```

##INSTALL DEPENDENCIES
```
sudo pip install -r requirements.txt
```

##Django Instructions
```
python3 manage.py makemigrations caption_downloader
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

## Summry API
```
# usern:roshandash
# pass:12345
# apikey : 7A401654BB
```
## IBM Watson API
```
# "url": "https://gateway.watsonplatform.net/natural-language-understanding/api",
# "username": "4f715217-9f93-4257-b977-c732bbfeecb3",
# "password": "Fgy3OcTQqmxo"
```
Star the repo if you like it :smile:


