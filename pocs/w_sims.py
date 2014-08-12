import idautils

sys.path.append("../")

from api_tagger import *
from api_tokener import *
from collections import Counter

"""
Author:
    Alexander Hanel
Date:
    20140811
Version:
    - 12
Summary:
    Examples of using the TT&SS library

    TODO:
        * Finish the monster mash
            - already generated or manually named fuctions will make the tokenizer useless..
        * Figure out way to keep the order of the function name
            Example: SectionCriticalLeaveEnter
                Api names ( EnterCriticalSection, LeaveCriticalSection)
                EnterLeaveCriticalSection would be cleaner
        * Generate silly sentence example full text.
        * Download repo to new machine and test importing, etc
"""

class SimilarFunctions:
    def __init__(self):
        self.apis = []
        self.monster_mash = False
        self.calls = 0
        self.verbose = True
        self.rename = True
        self.matched = False
        self.threshold = 0
        self.count_strings = {}
        self.func_name = ""
        self.tagg = tagger()
        self.tok = token_api()

    def run(self, addr):
        self.get_apis(addr)
        self.match_apis()
        self.create_string()
        self.is_name_used(addr)
        if self.verbose and self.func_name:
            print "%s rename is %s" % (GetFunctionName(addr), self.func_name)

        if self.func_name and self.rename:
            idc.MakeName(GetFunctionAttr(addr, FUNCATTR_START), self.func_name)

    def is_name_used(self, addr):
        # do not rename the same function
        if LocByName(self.func_name) == GetFunctionAttr(addr, FUNCATTR_START):
            return
        # if function name does not exist use generated name
        if LocByName(self.func_name) == BADADDR:
            return
        # function name exists, rename it "func" will be "func_2"
        else:
            count = 2
            self.func_name += "_" + str(count)
            while LocByName(self.func_name) != BADADDR:
                self.func_name = self.func_name[:-2] + "_" + str(count)
                count += 1

    def get_apis(self, func_addr):
        flags = GetFunctionFlags(func_addr)
        # ignore library functions
        if flags & FUNC_LIB or flags & FUNC_THUNK:
            return None
        # list of addresses
        dism_addr = list(FuncItems(func_addr))
        for instr in dism_addr:
            tmp_api_address = ""
            tmp_api_name = ""
            if idaapi.is_call_insn(instr):
                # In theory an API address should only have one xrefs
                # The xrefs approach was used because I could not find how to
                # get the API name by address.
                for xref in XrefsFrom(instr, idaapi.XREF_FAR):
                    if xref.to == None:
                        self.calls += 1
                        continue
                    tmp_api_address = xref.to
                    break
                # get next instr since api address could not be found
                if tmp_api_address == "":
                    self.calls += 1
                    continue
                api_flags = GetFunctionFlags(tmp_api_address)
                # check for lib code (api)
                if api_flags & idaapi.FUNC_LIB == True or api_flags & idaapi.FUNC_THUNK:
                    tmp_api_name = NameEx(0, tmp_api_address)
                    if tmp_api_name:
                        self.apis.append(tmp_api_name)
                else:
                    self.calls += 1

    def match_apis(self):
        self.matched = False
        api_set = set(self.apis)
        # Optional Threshold. Only check functions with more than 2 apis
        if self.calls <= self.threshold and len(self.apis) > 1:
            api_tokend  = []
            # for each api in function
            for api_name in api_set:
                # for each tokenized string in API name
                for item in self.tok.tokenizer(api_name):
                    if item is None:
                        continue
                    api_tokend.append(item)
            # Count occurrence of strings.
            count_tmp = Counter(api_tokend)
            # if a common string is found in all APIs
            # return True and the count strings
            for string, count in count_tmp.items():
                if count == len(self.apis):
                    self.matched = True
                    self.count_strings = count_tmp

    def create_string(self):
        if self.count_strings == "":
            return
        # Sort strings by highest occurrence
        sort = sorted(self.count_strings, key=self.count_strings.get, reverse=True)
        name = ""
        for each in sort:
            # ignore Wide or Ascii
            if each.upper() == "A" or each.upper() == "W":
                continue
            # Convert to CamelCase for easier reading and space
            tmp = each[0].upper() + each[1:]
            name += str(tmp)
        self.func_name = name

"""
Wrapper Credit
    * Branko Spasojevic originally provided the wrapper code
    * Daniel Plohmann through his python magic added it to IDAScope
        * See /idascope/core/SemanticIdentifier.py line 456 (as of 2014/08/05 )
    * I just expanded on it for this example.
"""

class Wrappers():

    def __init__(self):
        self.func_name = ""

    def wrapper_test(self, func_addr):
        """
        identifies wrapper functions
        returns a tupple of ( function to be called, type
        either a sub_wrapper or api_wrapper
        """
        flags = GetFunctionFlags(func_addr)
        # ignore library functions
        if flags & FUNC_LIB or flags & FUNC_THUNK:
            return None
        dism_addr = list(FuncItems(func_addr))
        length = len(dism_addr)
        if length > 0x20:
            return None
        call = 0  # stores count calls
        test = 0  #
        op = ''
        op_addr = ""
        op_type = 0
        # loop through all instructions in function.
        # ends after the last instruction is processed
        for line in dism_addr:
            m = GetMnem(line)
            if m == 'call':
                call += 1
                if call == 2:
                    return None
                op_addr = GetOperandValue(line , 0)
                op_type = GetOpType(line,0)
                # if op_type is 2 API call
                op = GetOpnd(line,0)
            if m == 'jmp':
                temp = GetOperandValue(line,0)
                # test if JMP address is within the function
                if temp not in dism_addr:
                    call += 1
                    if call == 2:
                        return None
                    op_addr = GetOperandValue(line , 0)
                    op_type = GetOpType(line,0)
                    op = GetOpnd(line,0)
            if m == 'cmp' or m == 'test':
                test += 1
                # not a wrapper function if a lot of test and cmp logic
                if test == 3:
                    return None
        # remove junk strings
        if "ds:" in op:
            op = op.replace("ds:",'')
        # ignore name mangled code
        if "[" in op or "$" in op or "?" in op or "@" in op:
            return None
        # a function that calls another function
        # thunk functions are treated as apis
        if op_type == 7:
            if GetFunctionFlags(op_addr) & FUNC_THUNK:
                return (op, 'api_wrapper')
            else:
                return (op, 'sub_wrapper')
        if op_type == 2:
            return (op, 'api_wrapper')
        if op_type == 6:
            return (op, 'api_wrapper')

    def is_name_used(self, addr):
        # do not rename the same function
        if LocByName(self.func_name) == GetFunctionAttr(addr, FUNCATTR_START):
            return None
        # if function name does not exist use generated name
        if LocByName(self.func_name) == BADADDR:
            return None
        # function name exists, rename it "func" will be "func_2"
        else:
            count = 2
            self.func_name += "_" + str(count)
            while LocByName(self.func_name) != BADADDR:
                self.func_name = self.func_name[:-2] + "_" + str(count)
                count += 1

    def rename_wrapper(self, addr, func_stats):
        func_addr = GetFunctionAttr(addr , FUNCATTR_START)
        if func_stats == None:
            return None
        # func_stats returns a tupple(name, type)
        # the type can be seen about 10 lines up
        api_name, api_type = func_stats
        renamer = ""
        if api_type == "sub_wrapper":
            self.func_name = "ws_" + api_name
        elif api_type == "api_wrapper":
            self.func_name = "w_" + api_name
        else:
            return None

    def run(self, addr):
        if self.rename_wrapper(addr, self.wrapper_test(addr)) is not None:
            self.is_name_used(addr)
            MakeName(GetFunctionAttr(addr, FUNCATTR_START), self.func_name)


############



s = SimilarFunctions()
s.monster_mash = True
s.run(here())
w = Wrappers()
w.run(here())


