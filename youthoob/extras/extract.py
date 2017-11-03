import re
with open('c.txt', 'r+') as f:
    k= f.read()
    n = [(m.start(0), m.end(0)) for m in re.finditer('"', k)]
    k = k[n[0][1]:]
    x = k.split('\\n')
    x = filter(None, x)
    out=[]
    for a in x:
        if(a[0]!='0'):
            out.append(a)
    #print(out)
    out = ' '.join(out)
    n = [(m.start(0), m.end(0)) for m in re.finditer('"', out)]
    out = out[:n[0][0]]
    print(out)
