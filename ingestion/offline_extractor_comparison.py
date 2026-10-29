"""Compare offline article extractors on the same already-authorized HTML response.

No network calls and no persistence of extracted article text.
"""
import hashlib
from html.parser import HTMLParser

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
        self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript','svg'):
            self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript','svg'):
            self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:
            self.parts.append(data)

def normalized(text):
    return ' '.join((text or '').split())

def metrics(text):
    text=normalized(text)
    import re
    words=text.split()
    sentences=[x.strip() for x in re.split(r'[.!?]+',text) if len(x.strip())>=30]
    repeated=sum(count-1 for count in __import__('collections').Counter(s.lower() for s in sentences).values() if count>1)
    boilerplate_terms=('cookie policy','privacy policy','all rights reserved','subscribe to our newsletter','accept cookies')
    boilerplate_hits=sum(term in text.lower() for term in boilerplate_terms)
    return {'chars':len(text),'words':len(words),
            'long_sentences':len(sentences),'repeated_long_sentences':repeated,
            'boilerplate_phrase_hits':boilerplate_hits,
            'substantial_1200_180':len(text)>=1200 and len(text.split())>=180,
            'sha256':hashlib.sha256(text.encode()).hexdigest() if text else None,
            'substantial_800':len(text)>=800 and len(text.split())>=100}

def extract_comparison(html):
    """Independent library outputs; never download again or store body text."""
    import trafilatura
    from readability import Document
    results={}
    try:
        text=trafilatura.extract(html,include_comments=False,include_tables=False)
        results['trafilatura']=metrics(text)
    except Exception as exc:
        results['trafilatura']={'error_type':type(exc).__name__}
    try:
        rendered=Document(html).summary()
        parser=TextOnly()
        parser.feed(rendered)
        results['readability']=metrics(' '.join(parser.parts))
    except Exception as exc:
        results['readability']={'error_type':type(exc).__name__}
    return results
