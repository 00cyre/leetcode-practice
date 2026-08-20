from _collections_abc import dict_keys
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        s1_def = {letter: 0 for letter in s}
        s2_def = {letter: 0 for letter in t}
        letter_count = []
        if len(s) != len(t):
            return False
        for v in [*s]:
            s1_def[v] = s1_def[v] + 1
        for v in [*t]:
            s2_def[v] = s2_def[v] + 1
        for k,v in s1_def.items():
            try:
                if(s2_def[k] != v):
                    return False
            except:
                return False
        return True
