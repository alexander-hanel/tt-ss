import json

class tagger():
    def __init__(self):
        self.status = True
        self.nltk = False
        self.pos = ''
        self.syn = ''
        self.words = {}
        self.wordsTo = {}
        self.loader()

    def loader(self):
        try:
            f = open('lwords.json', 'rb')
            self.words = json.load(f)
            f.close()
            f = open('lto_words.json', 'rb')
            self.wordsTo = json.load(f)
            f.close()
        except:
            self.status = False
            
    def lookup(self, value):
        'returns a list with the value, lex, replacement'
        value = value.lower()
        tmp = []
        tmp.append(value.decode('utf-8'))
        if self.words.has_key(value):
            tmp.extend(self.words[value])
            return tmp
        elif self.wordsTo.has_key(value):
            tmp.extend(self.wordsTo[value])
            return tmp
        elif self.nltk == True:
            pass
        else:
            return None 

    def help(self):
        print 'object.lookup(value)'
        print 'return list([value, part of speech, replacement])'
