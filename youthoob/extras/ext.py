import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 \
  as Features

natural_language_understanding = NaturalLanguageUnderstandingV1(
  username="4f715217-9f93-4257-b977-c732bbfeecb3",
  password="Fgy3OcTQqmxo",
  version="2017-02-27")

with open('c.txt', 'r') as f:
  to_pass = f.read()


response = natural_language_understanding.analyze(
  text=to_pass,
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

print(json.dumps(response, indent=2))

to_ret={}

for a in response["keywords"]:
  to_ret.update({a['text'] : '#'})

for a in response["entities"]:
  try:
    to_ret.update({a['text']: a['disambiguation']['dbpedia_resource']})
  except:
    to_ret.update({a['text']: '#'})

print(to_ret)