import re 

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)


def tokenize_on_whitespace(text):
    if text:
        tokens = "".join([c if c.isalnum() else " " for c in text.lower().strip()])
        return list(set(filter(None, tokens.split())))