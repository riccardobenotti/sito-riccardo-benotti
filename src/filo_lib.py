import re, unicodedata, html
def unb(s):
    out=[]
    for ch in s:
        n=unicodedata.name(ch,'')
        if n.startswith('MATHEMATICAL SANS-SERIF BOLD'):
            out.append(unicodedata.normalize('NFKC',ch))
        else: out.append(ch)
    return ''.join(out)
def isbold(ch): return unicodedata.name(ch,'').startswith('MATHEMATICAL SANS-SERIF BOLD')
def tohtml(s):
    # wrap runs of bold chars (allow spaces/punct/combining between) in <b>
    res=''; i=0; n=len(s)
    while i<n:
        if isbold(s[i]):
            j=i
            while j<n and (isbold(s[j]) or (s[j] in " ,.:;'’'\"“”-–!?()0123456789̀́" and any(isbold(c) for c in s[j:j+3]))):
                j+=1
            res+='<b>'+html.escape(unb(s[i:j]).strip(),quote=False)+'</b>'+(' ' if s[i:j].endswith(' ') else '')
            i=j
        else:
            res+=html.escape(s[i],quote=False); i+=1
    return unicodedata.normalize('NFC',res)
EMO=re.compile(r'^[\U0001F300-\U0001FAFF☀-➿⬀-⯿️‍\s]+')
