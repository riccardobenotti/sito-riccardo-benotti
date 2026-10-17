import re, unicodedata, html


def _style(ch):
    """Restituisce 'b', 'i', 'bi' o '' per i caratteri matematici Unicode usati su LinkedIn."""
    n = unicodedata.name(ch, '')
    if not n.startswith('MATHEMATICAL'):
        return ''
    bold, ital = 'BOLD' in n, 'ITALIC' in n
    return 'bi' if bold and ital else 'b' if bold else 'i' if ital else ''


def unb(s):
    """Converte i caratteri matematici (grassetti e corsivi Unicode) in lettere normali."""
    return ''.join(unicodedata.normalize('NFKC', ch) if _style(ch) else ch for ch in s)


def isbold(ch):
    return _style(ch) != ''


_GLUE = " ,.:;'’‘\"“”«»-–—!?()[]/%0123456789̀́"


def tohtml(s):
    """Testo LinkedIn -> HTML: le parti in grassetto/corsivo Unicode diventano <b>/<i>."""
    res, i, n = '', 0, len(s)
    while i < n:
        st = _style(s[i])
        if st:
            j = i
            while j < n and (_style(s[j]) == st or (s[j] in _GLUE and any(_style(c) == st for c in s[j:j + 3]))):
                j += 1
            seg = html.escape(unb(s[i:j]).strip(), quote=False)
            tag = {'b': ('<b>', '</b>'), 'i': ('<i>', '</i>'), 'bi': ('<b><i>', '</i></b>')}[st]
            res += tag[0] + seg + tag[1] + (' ' if s[i:j].endswith(' ') else '')
            i = j
        else:
            res += html.escape(s[i], quote=False)
            i += 1
    return unicodedata.normalize('NFC', res)


EMO = re.compile(r'^[\U0001F000-\U0001FAFF☀-➿⬀-⯿←-⇿⌀-⏿️‍⃣©®‼⁉™ℹ〰〽\U000E0000-\U000E007F\s]+')
