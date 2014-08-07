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

import sys
import re
#from nltk.corpus import wordnet
#import nltk
'''
three scenarios:
    1. string with underscore 'DnsModifyRecordsInSet_W'
    2. string with UPPERCASE, underscore and standard 'HDC_UserFree'
    3. underscore and lowercase '_vsnprintf'
'''
class token_api():
    def __init__(self):
        self.token_str = []
        self.final = []
        self.finalized = []
    
    def tokenizer(self, api_string):
        self.__init__()
        # ignore name mangled apis.
        if '@' in api_string or '$' in api_string or '?' in api_string or '*' in api_string:
            return None
        # remove end of line character if present
        self.api_string = api_string.strip()
        if self.api_string[:-1].islower() and '_' not in self.api_string:
            # create class object
            tl = tokenize_lower()
            tl.run(self.api_string)
            self.finalized = self.charred(tl.str_queue)
            return self.finalized
        elif '_' not in self.api_string:
            # rare case that the whole string is upper case 
            if api_string.isupper():
                self.final.append(self.api_string)
                return self.final
            # create class object
            ts = tokenize_standard()
            ts.run(self.api_string)
            self.finalized = self.charred(ts.str_queue)
            return self.finalized
        else:
            tmp_710 = self.api_string.split('_')
            # remove blank items in the list
            for s in range(tmp_710.count('')):
                tmp_710.remove('')
            for x in tmp_710:
                if len(x) <= 1:
                    self.token_str.append(x)
                elif x.isupper():
                    self.token_str.append(x)
                elif x.islower():
                    tl = tokenize_lower()
                    tl.run(x)
                    self.token_str.append(tl.str_queue)
                else:
                    ts = tokenize_standard()
                    ts.run(x)
                    self.token_str.append(self.charred(ts.str_queue))
            self.final = self.flatten(self.token_str )
            return self.final
            
    def flatten(self, lst):
        # source http://rosettacode.org/wiki/Flatten_a_list#Python
        return sum( ([x] if not isinstance(x, list) else self.flatten(x)
            for x in lst), [] )

    def charred(self,t):
        'smash together uppercase chars'
        final = []
        upp = ''
        flag = False
        for value in t:
            if value.isupper() and len(value) == 1:
                flag = True
                upp += str(value)
            if value.isupper() and re.findall('\d', value):
                final.append(value)                
            if value.isupper() == False:
                flag = False
                if upp != '':
                    final.append(upp)
                    upp = ''
                if upp == '':
                    final.append(value)

        if upp != '':
            final.append(upp)
        return final
                    
class tokenize_standard():
    def __init__(self):
        self.api_string = ''
        self.lower = False
        self.upper = False
        self.under = False
        self.str_queue = []
        self.words_len = 0

    def run(self, api_str):
        self.__init__()
        if '_' in api_str:
            pass
        elif self.api_string.islower() == True:
            self.lower = True
            self.str_lower(api_str)
        elif self.api_string.isupper() == True:
            self.str_upper(api_str)
            self.upper = False
        else:
            self.str_split(api_str)
        self.words_len = len(self.str_queue)

    def str_upper(self, str_up):
        'add all uppercase strings to all strings list'
        self.str_queue.append(str_up)
    
    def str_lower(self, str_low):
        self.str_queue.append(str_low)

    def str_split(self, api_str):
        'break up API name into smaller strings'
        # NdrDllGetClassObject becomes ['Ndr', 'Dll', 'Get', 'Class', 'Object']
        tmp = ''
        for s in api_str:
            if s.islower():
                tmp += str(s)
            else:
                if tmp != '':
                    self.str_queue.append(tmp)
                break
        split_up = re.findall('[A-Z][^A-Z]*', api_str)
        for sp in split_up:
            self.str_queue.append(sp)

'''
tokenizing the lowercase strings is diffcult because there are no pattern to split
off of. A keyword approach has to be used. The set of undercase APIs is rare.  
'''
class tokenize_lower():
    def __init__(self):
        self.str_queue = []
        self.final_sweep = False
        self.modified = False

    def run(self, api_str):
        'tokenizes the lower case strings'
        self.__init__()
        self.str_queue.append(api_str)
        self.str_keywords()
        self.modified = True
        self.prep_queue(api_str)
        self.final_sweep = True
        for count in range(5):
            for string in self.str_queue:
                self.prep_queue(string)
            if self.modified == False:
                break
        for s in range(self.str_queue.count('')):
            self.str_queue.remove('')
        for s in range(self.str_queue.count('s')):
            self.str_queue.remove('s')

    def prep_queue(self, l_api):
        'most common substring to be parsed off of'
        if '_' in l_api:
            self.split_underscore(l_api)
            self.modified = True
        if 'get' in l_api[0:3] and l_api != 'get':
            self.str_tok(l_api[0:3], l_api[3:], l_api)
            self.modified = True
        elif 'to' in l_api and l_api != 'to':
            self.token_to_str(l_api, 'to')
            self.modified = True
        elif 'wcs' in l_api and l_api != 'wcs':
            self.token_to_str(l_api, 'wcs')
            self.modified = True
        elif 'is' in l_api[0:2] and l_api != 'is':
            self.str_tok(l_api[0:2], l_api[2:], l_api)
            self.modified = True
        elif 'mem' in l_api[0:3]and l_api != 'mem':
            self.str_tok(l_api[0:3], l_api[3:], l_api)
            self.modified = True
        elif 'str' in l_api[0:3] and l_api != 'str':
            self.str_tok(l_api[0:3], l_api[3:], l_api)
            self.modified = True
        elif 'lstr' in l_api[0:4] and l_api != 'lstr':
            self.str_tok(l_api[0:4], l_api[4:], l_api)
            self.modified = True
        elif self.modified == False:
            self.str_parse(l_api)

    def str_keywords(self):
        keywords = ['shutdown', 'sprintf', 'printf', 'select', 'socket', 'event', 'strstr', 'create', \
                    'close', 'qsort', 'write', 'split', 'ioctl', 'scan', 'open', 'find', 'main', 'pure',    \
                    'addr', 'seek', 'make', 'port', 'serv', 'used', 'user', 'math', 'read', 'free', 'peer',  \
                    'path', 'name', 'info', 'recv', 'call', 'sqrt', 'set', 'wcs', 'lwr', 'chk', 'opt', 'jmp',  \
                    'sqt', 'str', 'flt', 'cat', 'cpy', 'upr', 'cmp', 'len', 'brk', 'div', 'chk', 'by']
        for key in keywords:
            count = 0
            _item = [s for s in self.str_queue if key in s]
            if len(_item) == 0:
                continue
            count = self.str_queue.count(_item[0])
            if count != 0:
                # splits the string by the found keword 
                self.token_to_str(_item[0], key)

    def str_tok(self, add_str, parse_me, full_str):
        replace_list = [ add_str, parse_me]
        self.update_list(full_str, replace_list)

    def str_parse(self, api_str):
        self.update_list(api_str, None)
        
    def split_underscore(self, str_under):
        tmp = str_under.split('_')
        # remove empty items in list
        for s in range(tmp.count('')):
            tmp.remove('')
        self.update_list(str_under, tmp)

    def token_to_str(self, to_str, sp):
       str_splitter = ' ' + sp + ' '
       tmp = to_str.replace(sp, str_splitter )
       final = tmp.split(' ')
       # remove empty items in list
       for s in range(final.count('')):
            final.remove('')
       self.update_list(to_str, final)
           
    def flatten(self, lst):
        # source http://rosettacode.org/wiki/Flatten_a_list#Python
        return sum( ([x] if not isinstance(x, list) else self.flatten(x)
            for x in lst), [] )
    
    def update_list(self, tok_str, replace_with):
        'replaces list item with the tokenized version or sub-strings'
        if replace_with == None:
            if self.str_queue.count(tok_str) <= 1 and len(self.str_queue) != 1:
                self.str_queue.append(tok_str)
        else:
            for count, item in enumerate(self.str_queue):
                if tok_str == item:
                    self.str_queue[count] = replace_with
                    break
            self.str_queue = self.flatten(self.str_queue)

