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


from api_tokener import *
from api_tagger import *
from collections import *

'''
Sentence Rules:
    * Adjectives stand in front of the noun or after the verb
    * Adverbs frequency usually come in front of the main verb
    * preposition - verb, prep, the noun
    * pronoun - before the noun

POS: adv (adverb), noun, pro (pronoun), verb, adj, prep
Sample text:
Function sub_0x401000 opens, creates and closes a registry key. It sets a registry value.
It then creates and writes a file.


Function_name verb, verb and verb 'a' noun, noun. 

'''


class sentencer():
    def __init__(self):
        self.most_common = []
        self.nouns = set([])
        self.subjects = set([])
        self.summary = ''
        # used to store the objects/nouns; subject is first
        self.phrase = []
        self.function_name = ''
        self.append_with = {}
        self.tag = tagger()
        self.toka = token_api()
        ## dict that contains the api name as a key and list of tokenized strings 
        self.api_tokens = OrderedDict()
        self.api_tokens_pos = OrderedDict() # dict[api] = [pos, pos, pos]
        self.tokened_nouns = OrderedDict()
        self.first_noun = OrderedDict()
        self.dict_phrase_api = OrderedDict() # dict[phrase] = [api1, api2, api3]

    def run(self,api_str_list, func):
        'main, pass a list of the API names as the 1st argument and the name of the function as the second'
        # the created sentence(s) will be in the object.summary
        # delete previous summary
        self.__init__()
        # populate
        self.start(api_str_list,func)
        # remove a (ascii) & w (wide)
        self.remove_a_w()
        self.get_nouns()
        # phrase is the nouns (subjects & objects)
        self.get_phrase()
        self.get_pos_4_api()
        self.get_apis_phrases()
        self.create_sentence() 

    def start(self, api_str_list, func):
        'gets a sorted list of the most common strings. assigns them to self.most_common'
        self.function_name = func
        cunt = Counter()
        # populates a dict that contains tokenized API sub-strings
        for api in api_str_list:
            self.api_tokens[api] = self.toka.tokenizer(api)
            for tok in self.api_tokens[api]:
                ret = self.tag.lookup(tok)
                try: 
                    cunt[ret[0]] += 1
                except:
                    cunt[tok] += 1
        # probably can delete...
        self.most_common = cunt.most_common()
        

    def get_pos(self, str_part):
        'return the part of speech of the string'
        # aka am I a noun, verb, etc
        try:
            return self.tag.lookup(str_part)[1]
        except:
            return None

    def get_nouns(self):
        'creates a dict with the api name as the key with a list of the nouns'
        for api in self.api_tokens:
            toks = self.api_tokens[api]
            for item in toks:
                if self.get_pos(item) == 'noun':
                    self.nouns.add(item)
                    if self.tokened_nouns.has_key(api):
                        self.tokened_nouns[api].append(item)
                    else:
                        self.tokened_nouns[api] = []
                        self.tokened_nouns[api].append(item)

    def remove_a_w(self):
        'remove a, ex and w sub-strings from the string'
        # Ascii, wide or extended are of very little use
        for i in self.api_tokens:
            if 'A' in self.api_tokens[i]:
                self.api_tokens[i].remove('A')
            if 'W' in self.api_tokens[i]:
                self.api_tokens[i].remove('W')
            if 'Ex' in self.api_tokens[i]:
                self.api_tokens[i].remove('Ex')
                
    def get_phrase(self):
        'group the nouns/phases of all the tokenized nouns'
        for item in self.tokened_nouns:
            # could have used a set but the order matters
            if self.tokened_nouns[item] not in self.phrase:
                self.phrase.append(self.tokened_nouns[item])

    def get_pos_4_api(self):
        # self.api_tokens_pos = dict[api] = [pos1, pos2,..] [noun, verb, noun]
        for api in self.api_tokens:
            tokened = self.api_tokens[api]
            self.api_tokens_pos[api] = []
            for item in tokened:
                self.api_tokens_pos[api].append(self.get_pos(item))
                
    def get_apis_phrases(self):
        # self.dict_phrase_api = dict[phrase] = [api1, api2, api3]
        for p in self.phrase:
            for api in self.api_tokens:
                c = 0
                # for each noun in a phrase
                for noun in p:
                    if noun in self.api_tokens[api]:
                        c += 1
                    else:
                        break
                    if c == len(p):
                        if self.dict_phrase_api.has_key(str(p)):
                            if api not in self.dict_phrase_api[str(p)]: 
                                self.dict_phrase_api[str(p)].append(api)
                        else:
                            self.dict_phrase_api[str(p)] = []
                            self.dict_phrase_api[str(p)].append(api)

    def get_all_parts(self, part, phrase):
        'returns all strings that are a specific POS for a phrase'
        pos_ret = []
        # create a list of all the API names 
        sub_phrase = self.dict_phrase_api[str(phrase)]
        for name in sub_phrase:
            # name is the API, example: AdjustTokensGroups.
            tokened = self.api_tokens_pos[name]
            for count, pos in enumerate(tokened):
                if part.decode('utf-8') == pos:
                    if count + 1 != len(tokened) and tokened[count+1] == None:
                        self.append_with[part] = ( self.api_tokens[name][count], self.api_tokens[name][count+1] ) 
                    pos_ret.append(self.api_tokens[name][count]) 
        return pos_ret

    def lookup_full(self, str_part):
        'return the part of speech of the string'
        try:
            return self.tag.lookup(str_part)[2]
        except:
            return None

    '''
    Sentence Rules:
        * Adjectives stand in front of the noun or after the verb
        * Adverbs frequency usually come in front of the main verb
        * preposition - verb, prep, the noun
        * pronoun - before the noun

    adverbs, verbs, prep, pronoun, noun, 
    POS: adv (adverb), noun, pro (pronoun), verb, adj, prep
    Sample text:
    Function sub_0x401000 opens, creates and closes a registry key. It sets a registry value.
    It then creates and writes a file.


    Function_name verb, verb and verb 'a' noun, noun.   
    '''

    # Get apis for each phrase - done 
    # Get verbs for each phrase - done
    # Get all other POS - done
    # Make a fucking sentence - done 
    
    def create_sentence(self):
        started = False
        tmp = ''
        for p in self.phrase:
            if started == False:
                self.summary = "Function %s" % self.function_name
                started = True
            elif started == True and p == self.phrase[-1]:
                self.summary += "Then the function"
            elif started == True:
                self.summary += "The function"

            # yes, I could have broken these up into functions but I didn't...hour 250 of a project makes for un-opitmization 
            # adverbs
            adverbs = self.get_all_parts('adv', p)
            for count, adv in enumerate(adverbs):
                ap = ''
                x1 = self.lookup_full(adv)
                if self.append_with.has_key('adv'): 
                    if self.append_with['adv'][0] == adv:  
                        ap = self.append_with['adv'][1] 
                if count != 0 and adv == adverbs[-1] and len(adverbs) != 0:
                    self.summary += ' '
                    self.summary  += 'and'
                if len(adverbs) > 2 and adv != adverbs[-1] and adv != adverbs[0]:
                    self.summary += ','
                tmp = self.lookup_full(adv)
                if tmp == 'None':
                    self.summary += ' '
                    self.summary += adv
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                else:
                    self.summary += ' '
                    self.summary += tmp.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                        
            # verbs
            verbs = self.get_all_parts('verb', p)
            for count, v in enumerate(verbs):
                ap = ''
                x1 = self.lookup_full(v)
                if self.append_with.has_key('verb'): #
                    if self.append_with['verb'][0] == v: # 
                        ap = self.append_with['verb'][1] #
                if count != 0 and v == verbs[-1] and len(verbs) != 0:
                    self.summary += ' '
                    self.summary  += 'and'
                if len(verbs) > 2 and v != verbs[-1] and v != verbs[0]:
                    self.summary += ','
                tmp = self.lookup_full(v)
                if tmp == 'None':
                    self.summary += ' '
                    self.summary += v.lower() + 's'
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                else:
                    self.summary += ' '
                    self.summary += tmp.lower()  + 's'
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                        
            # preposition
            preposition = self.get_all_parts('prep', p)
            for count, pre in enumerate(preposition):
                ap = ''
                x1 = self.lookup_full(pre)
                if self.append_with.has_key('prep'): 
                    if self.append_with['prep'][0] == pre: 
                        ap = self.append_with['prep'][1] 
                if count != 0 and pre == preposition[-1] and len(preposition) != 0:
                    self.summary += ' '
                    self.summary  += 'and'
                if len(preposition) > 2 and v != preposition[-1] and v != preposition[0]:
                    self.summary += ','
                tmp = self.lookup_full(pre)
                if tmp == 'None':
                    self.summary += ' '
                    self.summary += pre.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                else:
                    self.summary += ' '
                    self.summary += tmp.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                        
            # pronouns
            pronouns = self.get_all_parts('pro', p)
            for count, pro in enumerate(pronouns):
                ap = ''
                x1 = self.lookup_full(pro)
                if self.append_with.has_key('pro'): #
                    if self.append_with['pro'][0] == pro: # 
                        ap = self.append_with['pro'][1] #
                if count != 0 and pro == pronouns[-1] and len(pronouns) != 0:
                    self.summary += ' '
                    self.summary  += 'and'
                if len(pronouns) > 2 and v != pronouns[-1] and v != pronouns[0]:
                    self.summary += ','
                tmp = self.lookup_full(pro)
                if tmp == 'None':
                    self.summary += ' '
                    self.summary += pro.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                else:
                    self.summary += ' '
                    self.summary += tmp.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
            try:
                if self.phrase[0][0][0] == 'a' or self.phrase[0][0][0] == 'A':
                    self.summary += (' an')
                else:
                    self.summary += (' a')
            except:        
                self.summary += (' a')

            # adjectives
            adjectives = self.get_all_parts('adj', p)
            for count, adj in enumerate(adjectives):
                ap = ''
                x1 = self.lookup_full(adj)
                if self.append_with.has_key('adj'): 
                    if self.append_with['adj'][0] == adj:  
                        ap = self.append_with['adj'][1] 
                if count != 0 and adj == adjectives[-1] and len(adjectives) != 0:
                    self.summary += ' '
                    self.summary  += 'and'
                if len(adjectives) > 2 and adj != adjectives[-1] and adj != adjectives[0]:
                    self.summary += ','
                tmp = self.lookup_full(adj)
                if tmp == 'None':
                    self.summary += ' '
                    self.summary += adj.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                else:
                    self.summary += ' '
                    self.summary += tmp.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()

            # nouns
            na = self.get_all_parts('noun', p) #
            for noun in p:
                ap = ''
                x1 = self.lookup_full(noun)
                if self.append_with.has_key('noun'): #
                    if self.append_with['noun'][0] == noun: # 
                        ap = self.append_with['noun'][1] #
                if x1 == 'None':
                    self.summary += ' '
                    self.summary += noun.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
                else:
                    self.summary += ' '
                    self.summary += x1.lower()
                    if ap != '':
                        self.summary += ' '
                        self.summary += ap.lower()
            self.summary += '. '
            
            
# s = sentencer()
# s.run(["LookupPrivilegeValueA","OpenProcessToken","RegCloseKey","RegDeleteValueA","RegQueryValueExA","RegSetValueExA","AdjustTokenPrivileges","CloseHandle","CopyFileA","CreateFileA","CreateFileW","CreateMutexA","CreateThread","DeleteFileA","FindClose","FindFirstFileA","FindNextFileA","GetCurrentDirectoryA","GetFileSize","GetModuleFileNameA","GetProcAddress","GetSystemDirectoryA","GetWindowsDirectoryA","LoadLibraryA","LocalAlloc","LocalFree","MoveFileA","MoveFileExA","MultiByteToWideChar","OpenMutexA","ReadFile","SetCurrentDirectoryA","SetFilePointer","Sleep","TerminateProcess","WriteFile","lstrcatA","lstrcmpiA","lstrcpyA","lstrlenA","ExitWindowsEx","GetDlgItem","GetWindowTextA","PostMessageA","EnumWindows"], "sub_xxxxx")
# print s.summary

                

    

