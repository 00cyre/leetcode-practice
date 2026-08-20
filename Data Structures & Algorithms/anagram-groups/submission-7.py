class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        #hashmap with sorted string by letter where key = sorted letters, and values is array of the original strings, it will already be saved in order anyways.
        #{letter: 0 for letter in t}
        hmap = {}
        for word in strs:
            index = "".join(sorted(word))
            if index in hmap:
                hmap[index].append(word)
            else:
                hmap[index] = [word]
        return [v for i,v in hmap.items()]