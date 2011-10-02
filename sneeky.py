import re, random, math
from rangecoder import RangeEncoder, RangeDecoder
from corpus import Corpus

def tokenise(s):
    endpos = 0
    for m in re.finditer("(.*?)([a-z][a-z]+)", s):
        if m.group(1):
            yield m.group(1)
        yield m.group(2)
        endpos = m.end()
    if s[endpos:]:
        yield s[endpos:]



def decode(txt, corpus):
    d = RangeDecoder()
    for w in tokenise(txt):
        c = corpus.correction_idx(w)
        if c:
            d.decode(c[0], c[1])
    return d.finish()
    
def encode(txt, data, corpus):
    e = RangeEncoder(data)
    s = []
    txtlen = float(len(txt))
    pos = float(0)
    encprob = 0.5 # FIXME
    for w in tokenise(txt):
        lw = len(w)
        w, spelings = corpus.get_spellings(w)
        if spelings:
            p_txt = pos/txtlen
            p_enc = e.completion_est()
            if p_txt > p_enc: encprob = min(encprob * 1.1, 1)
            elif p_txt < p_enc: encprob = max(encprob / 1.1, 1e-5)
            if random.random() < encprob:
                k = e.encode(len(spelings))
                s.append(spelings[k])
            else:
                s.append(w)
        else:
            s.append(w)
        pos += lw
    if not e.finished():
        return False
    return "".join(s)
    
def max_entropy(txt, corpus):
    lg = lambda x: math.log(x) / math.log(2)
    entropy = 0
    for w in tokenise(txt):
        w, spelings = corpus.get_spellings(w)
        if spelings:
            entropy += lg(len(spelings))
    return entropy
