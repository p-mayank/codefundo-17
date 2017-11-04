import re
with open('d.txt', 'r+') as f:
    k= f.read()
    k = k.split("\n")
    k = ' '.join(k)
    k = k.replace('&#39;', "'")
    print(k)