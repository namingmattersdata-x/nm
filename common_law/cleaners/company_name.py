from common_law.data.stopwords import CUSSWORD_DATA
from common_law.data.company import SUFFIX_TRANSFORMATIONS, SUFFIX_IDENTIFIERS, TOKEN_STOPWORDS
from common_law.data.text import remove_tags
from string import punctuation
import re

alpha = 'abcdefghijklmnopqrstuvwxyz '
punctuation = punctuation.replace('&',' ')

class CompanyName(object):
    __slots__ = [
    "raw",
    "clean",
    "is_valid",
    "suffixes",
    "sig_tokens",
    "name"
    ]   

    def __init__(self, raw):
        self.raw = raw
        self.clean = None
        self.name = None 
        self.is_valid = None
        self.suffixes = []
        self.sig_tokens = []

    def as_dict(self):
        if self.clean and self.is_valid != False:
            return {
                "clean": self.clean,
                "suffixes":self.suffixes, 
                "sig_tokens":self.sig_tokens,
                "name": self.name 
                }
        return
        
    def pre_process(self):
        if not self.raw:
            self.is_valid = False
            return self
        raw = self.raw.lower().strip('.')
        if not re.search('[a-z]+', raw):
            self.is_valid = False
            return self

        raw = remove_tags(raw)
        raw = re.sub(" +", " ", raw).strip().replace('&amp','&')
        if len([i for i in raw if i.isalpha()]) < 2 or len(raw) > 500:
            self.is_valid = False
            return self

        dusted = [t for t in [token.strip(punctuation) for token in raw.split()] if t]
        if [token for token in dusted if token in CUSSWORD_DATA]:
            self.is_valid = False
            return self
        if len(dusted) > 1:
            i = 1
            suffix_start = 0
            while(i < len(dusted)):
                if dusted[i] in SUFFIX_IDENTIFIERS:
                    if dusted[i] in ['co','co.']:
                        if dusted[i-1] in ['&','and']:
                            i += 1
                            continue
                    if not suffix_start:
                        suffix_start = i
                    if dusted[i] in SUFFIX_TRANSFORMATIONS:
                        j = 0
                        current_dict = SUFFIX_TRANSFORMATIONS
                        while(j < len(dusted) - i):
                            if dusted[i+j] in current_dict:
                                if isinstance(current_dict[dusted[i+j]], dict):
                                    if i + j == len(dusted) - 1:
                                        if dusted[i] == "limited":
                                            self.suffixes.append("ltd")
                                            if not suffix_start:
                                                suffix_start = i
                                        break
                                    else:
                                        current_dict = current_dict[dusted[i+j]]
                                else:
                                    self.suffixes.append(current_dict[dusted[i+j]])
                                    if not suffix_start:
                                        suffix_start = i
                                    i += j
                            else:
                                if dusted[i] == "limited":
                                    self.suffixes.append("ltd")
                                    if not suffix_start:
                                        suffix_start = i
                                break
                            j += 1
                    else:
                        self.suffixes.append(dusted[i])
                i += 1
            if suffix_start:
                self.clean = " ".join(dusted[:suffix_start])
                self.name = self.raw.strip().lower()
            else:
                self.clean = " ".join(dusted)
                self.name = self.raw.strip().lower()
        else:
            self.clean = dusted[0]
            self.sig_tokens = [dusted[0]]
            self.name = self.raw.strip().lower()
            return self

        self.sig_tokens = [t for t in self.clean.split() if t not in TOKEN_STOPWORDS]
        return self
