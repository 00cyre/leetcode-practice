from _collections_abc import dict_keys
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        s1_def = {letter: 0 for letter in s}
        s2_def = {letter: 0 for letter in t}
        
        #okay so what i want to do here is create a set for both so i will know exactly which letters there are. i will need to iterate through one once so i already know that both have the same size so i don't need to be worried about out-of-bounds indexes. i get the index, add both to both sets, and then i do the same iteration again. actually i can do a single iteration on both arrays, do the counting on each index, and add the counter to a new set. that way i will know exactly how many occurrences there are on each string in a single loop 
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
