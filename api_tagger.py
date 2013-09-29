'''
Name:
        TT&SS

Version:
        0.1
        
Description:
        Python library for creating text out of API names

Author:
        alexander<dot>hanel<at>gmail<dot>com

License:
TT&SS is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see
<http://www.gnu.org/licenses/>.

'''
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
