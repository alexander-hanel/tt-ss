The below text is from a blog post I wrote on the tool. The original post can be found [here](http://hooked-on-mnemonics.blogspot.com/2013/09/tt-tokens-tagging-and-silly-sentences.html). 

In the past couple of years machine learning has been coming up more and more in regards to malware analysis and reverse engineering. Besides having some basic discussions with Willi over drinks about the topic or trying to guess what Ero Carrero is working on via random tweets, I have never looked into it. Disclaimer: This post is not about machine learning. It's more about NLP.  My start into machine learning started with a great book called Natural Language Processing with Python. While reading the book and working through the examples I started to wonder how can I make this relate to reverse engineering malware? All the examples use large bodies of text which are called corpus in natural language processing (NLP) terminology. The corpus range from MacBeth, Milton Paradise to Firefox discussion forums.The example corpus is possibly the complete opposite of the output of a disassembler. The corpus contains sentences, which contains a clause and verb, which contains words and which are all grammatically linked (usually) to express a thought. The output from a disassembler contains assembly instructions and APIs that can be used to accomplish a set of specific tasks. Assembly instructions without context of other instructions makes it very difficult to understand the overall task. Words on the other hand our very different. If we know the noun and the verb we can infer the subject and the action.  Multiple assembly language instructions would need to be read in order of execution to infer the subject and the action. Combining multiple instructions to find the subject and action is basically the beginning of writing a decompiler. In the situation of calling an application programming interface (API) we wouldn't need to do analysis on the subsets of instructions of the API. In most situations we can read the API name to understand it's functionality.  Why not use the APIs names to create sentences? In order to do this we need to understand how NLP processes text. Let' use the following example taken from the Natural Language Toolkit (NLTK) website


```
#!python

>>> import nltk
>>> sentence = """At eight o'clock on Thursday morning
... Arthur didn't feel very good."""
>>> tokens = nltk.word_tokenize(sentence)
>>> tokens
['At', 'eight', "o'clock", 'on', 'Thursday', 'morning',
'Arthur', 'did', "n't", 'feel', 'very', 'good', '.']
>>> tagged = nltk.pos_tag(tokens)
>>> tagged[0:6]
[('At', 'IN'), ('eight', 'CD'), ("o'clock", 'JJ'), ('on', 'IN'),
('Thursday', 'NNP'), ('morning', 'NN')]
```
The first step is to apply tokenization to the stream of data to break it up into a smaller list/set of data. In the sentence above each element separated by whitespace characters or punctuation are broken up into tokens. The second step is to tag each token/word with it's part of speech (POS). In summary the sub-strings need to be broken up into tokens using a simple heuristic or pattern and then each token needs to be tagged with it's own part of speech.

If we were to apply tokenization to the API GetProcAddress. We would have the tokens as ["Get", "Proc", "Address"] if we used the pattern of the uppercase to delimit the start of a token. A regular expression to search for this pattern would be re.findall('[A-Z][^A-Z]*', "GetProcAddress"). This works for camel cased API names but not all APIs follow this naming convention. Some API names are all lower case but contain sub-strings that need to be broken up into tokens. Most Windows sockets APIs are lower case for example getpeername, getsockopt and recv. Then some API names contain all upper case for one sub-string, with an underscore as the next char, then lowercase and then back to camel case. An example of this WTF stayle can be see in  FONTOBJ_cGetAllGlyphHandles. For each naming convention a different tokenizer would need to be written

For the second step, the POS "Get" would be a verb, "Proc" would be unknown and "Address" would be a noun. Without the previous step of tokenizing the API we would not be able to get the POS. If we don't have the POS we would not know where it is supposed to reside in a sentence. Our example of using GetProcAddress deviates from the normal NLTK process of tagging because we are not looking up the POS in the context of a sentence. Rather we are getting the POS of individual strings. A way around this is to access Princton's wordnet dictionary. We can look up the definition and POS.  An issue with this approach is it will give us all multiple definitions.


```
#!python

from nltk.corpus import wordnet
import nltk

>>> synsets = wordnet.synsets('get')
>>> for synset in synsets:
     print synset.lexname

noun.act
verb.possession
verb.change
verb.change
verb.change
verb.motion
verb.contact
verb.perception
verb.competition
verb.possession
verb.communication
verb.contact
verb.body
verb.body
verb.communication
verb.change
verb.communication
verb.cognition
verb.contact
verb.contact
verb.cognition
verb.possession
verb.possession
verb.perception
verb.perception
```
If we choose the most common POS we can remove the manual aspect of tagging the token. 

```
#!python


def lex_type( word ):
    'get lex type (noun, verb, etc)'
    tmp = []
    synsets = wordnet.synsets(word)
    for synset in synsets:
        tmp.append(synset.lexname.split('.')[0])
    if len(tmp) == 0:
        return None
    # find the most common string
    # source http://stackoverflow.com/a/1518632
    lex = max(set(tmp), key=tmp.count)
    return lex  
```

Since "proc" is not a valid dictionary we wouldn't have a means to label the POS and assign a meaning. In this situation we would have to manually tag the tokens. During my research I found around two hundred non-dictionary words that were manually labeled. Here is example of twenty five of them. 


```
#!text

"tst"
"lstrcat"
"to"
"keybd"
"wave"
"co"
"get3"
"throw"
"put3"
"rec"
"handler3"
"m32"
"vba"
"xcpt"
"null"
"fp"
"ld"
"rchr"
"vec"
"printf"
"by"
"fp"
"mdi"
"gdiplus"
"lwr"
```

Now that we have the POS for the tokens we can start applying those forgotten rules of grammar to form a sentence. Here are some rules that I found during my research that I used to structure my sentences.

    Sentence Rules and order:

    Adjectives stand in front of the noun or after the verb
    Adverbs frequency usually come in front of the main verb 
    Verbs
    Preposition - verb, prep, the noun
    Pronoun - before the noun
    Nouns and objects go last.

If we apply these rules to our example of "GetProcAddress" and some filler words to make it look prettier we would have a sentence of "Gets a process address". Poetry. This sample is an easy one but when we start to add the different API naming conventions, objects with similar functionality that need to be grouped together and all the other madlib approaches of making sentences things get complicated quickly. So without further ado I'd like to introduce  Tokens, Tagging and Silly Sentences. TT&SS. My goal of this project is to generate corpus from APIs used in malware to experiment with machine learning. I'm releasing it because I hope others might find it useful. The input and output is as simple as possible.  The first step is to create an object, then call object.run( list(API_LIST), str("Function_Name") and then print object.summary.  This design makes it easy to create a corpus from IDA, radare2 or an API monitor. From there the corpus could be used with machine learning to see it could accurately classify behavior of a set of APIs.


```
#!python

>>> from silly_sentence import sentencer
>>> s = sentencer()
>>> s.run(["LookupPrivilegeValueA","OpenProcessToken","RegCloseKey","RegDeleteValueA","RegQueryValueExA"], 'sub_xxxx')
>>> s.summary
u'Function sub_xxxx a lookup privilege value. The function opens a process token. The function closes a registry key. Then the function deletes and querys a registry value. '
```


The code can be downloaded on my bitbucket repo. I would highly recommend checking for updates often. Parsing and tokenizing the different API naming schemes has made for some interesting one off bugs.  Plus I frequently update the JSON files which contain all the substrings, their POS and a replacement string. The format for the individual elements in the JSON are string:[POS, replacement] for example "ghost": ["noun", "None"]. All strings needs to lowercase, minus the replacement string. They need to be "None" if you do not want them to be replaced.

Thanks to Philip Porter for sending over his list of the most common APIs used by malware. 

Disclaimer:
There is also a known issue where API names that do not have a POS with a noun will not be printed. It's hard to make a sentence without an object. A good example is "VirtualAlloc". "Virtual" is an adjective. 'Alloc" which is short for allocate is a verb. I'll be looking into the best way to fix soon but for now enjoy. Also, don't expect perfect grammar or even intelligent text ;)