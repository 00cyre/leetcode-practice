class Solution:
#find flag, get whatever is behind, which is lenght, then use the pointer of hash to grab the string based on the amount of characters next, then cut off the original string for decode, and move the pointer forward

    def encode(self, strs: List[str]) -> str:
        res = ""
        for s in strs:
            res += f"{len(s)}#{s}"
        return res

    def decode(self, s: str) -> List[str]:
        i = 0
        res = []
        count = s[0:i-1]
        while i < len(s):
            j = i
            i = s.find("#",i)
            count = s[j:i]
            i += 1
            res.append(s[i:i+int(count)])
            i = i+(int(count))
        return res