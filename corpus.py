import re, random, cPickle
from collections import defaultdict




def transpose2(word, pos):
    return word[0:pos] + word[pos+1] + word[pos] + word[pos+2:]

def all_tranposes(word):
    return [(transpose2(word, i), 1) for i in range(1, len(word) - 2)]
def all_removals(word):
    return [(word[:i] + word[i+1:], 0.5) for i in range(1, len(word)-1)]
replacements = [
  ["ea", "ee"],
  ["ly", "illy", "lly", "ily"],
  ["l","ll"],
  ["an", "en", "on"],
  ["p", "pp"],
  ["f", "ff"],
  ["ay","ey"],
  ["r","rr"],
  ["ie","ei"],
  ["tte","te"],
  ["ise","ize"],
  ["our","or"],
  ["ce","se"],
  ["tch", "tsh"],
  ["er", "ar", "err", "arr"],
  ["isation","ization","isasion","izasion",
   "isetion","izetion","isesion","izesion"],
  ["tion","sion"]
  ]
def find_positions(haystack, needle):
    pos = 0
    while 1:
        p = haystack.find(needle, pos)
        if p == -1:
            break
        yield p
        pos = p + len(needle)
            
def all_replacements(word):
    for rset in replacements:
        for i in range(len(rset)):
            for p in find_positions(word, rset[i]):
                if p == 0:# or p + len(rset[i]) == len(word):
                    continue
                preword = word[:p]
                postword = word[p+len(rset[i]):]
                for rep in rset:
                    if rep != rset[i]:
                        yield (preword + rep + postword, 0.7)

def misspellings(w):
    return all_tranposes(w) + all_removals(w) + list(all_replacements(w))

def hist(text):
    d = {}
    for m in re.finditer('[a-z][a-z]+', text):
        w = m.group(0)
        if w in d: d[w] += 1
        else: d[w] = 1
    return d

def train(words):
    misspell_probs = {}
    for word,freq in words.iteritems():
        pword = float(freq)
        for speling, prel in misspellings(word):
            if speling in words: continue
            p = pword * prel
            if speling in misspell_probs:
                word2, p2 = misspell_probs[speling]
                if p2 > p: continue
            misspell_probs[speling] = (word, p)

    misspell_list = {}
    for speling, (word, p) in misspell_probs.iteritems():
        assert speling not in words
        if word not in misspell_list: misspell_list[word] = [speling]
        else: misspell_list[word].append(speling)

    for word, spelings in misspell_list.items():
        if len(spelings) < 2:
            del misspell_list[word]

    correction = {}
    for word, spelings in misspell_list.iteritems():
        random.shuffle(spelings)
        for i,s in enumerate(spelings):
            assert s not in correction
            correction[s] = (word, i, len(spelings))
    return misspell_list, correction


class Corpus(object):
    @staticmethod
    def load(fname):
        c = Corpus(None)
        c.misspell_list, c.corrections = cPickle.load(open(fname))
        return c

    def save(self, fname):
        cPickle.dump((self.misspell_list, self.corrections), open(fname, "w"))

    def __init__(self, txt):
        if txt:
            if txt.__class__.__name__ == 'Corpus':
                self.misspell_list, self.corrections = \
                    txt.misspell_list, txt.corrections
            else:
                self.train(hist(txt))

    def train(self, words):
        misspell_probs = {}
        for word,freq in words.iteritems():
            pword = float(freq)
            for speling, prel in misspellings(word):
                if speling in words: continue
                p = pword * prel
                if speling in misspell_probs:
                    word2, p2 = misspell_probs[speling]
                    if p2 > p: continue
                misspell_probs[speling] = (word, p)
    
        misspell_list = {}
        for speling, (word, p) in misspell_probs.iteritems():
            assert speling not in words
            if word not in misspell_list: misspell_list[word] = [speling]
            else: misspell_list[word].append(speling)
    
        for word, spelings in misspell_list.items():
            if len(spelings) < 2:
                del misspell_list[word]
    
        corrections = {}
        for word, spelings in misspell_list.iteritems():
            random.shuffle(spelings)
            for i,s in enumerate(spelings):
                assert s not in corrections
                corrections[s] = (word, i, len(spelings))

        self.misspell_list, self.corrections = misspell_list, corrections

    def correction_idx(self, word):
        if word in self.corrections:
            c, n, k = self.corrections[word]
            return n,k
        else:
            return None
    
    def get_spellings(self, word):
        if word in self.corrections:
            word = self.corrections[word][0]

        spelings = self.misspell_list.get(word)
        if spelings:
            return word, spelings
        else:
            return word, []
