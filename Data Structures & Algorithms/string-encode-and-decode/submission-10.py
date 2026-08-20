class Solution:

    def encode(self, strs: List[str]) -> str:
        res = ""
        
        for s in strs:
            res += f"{len(s)}#{s}"

        return res

    def decode(self, s: str) -> List[str]:
        res = []
        i = 0

        while i < len(s):
            j = i
            while s[j] != "#":
                j += 1
            count = int(s[i:j])
            i = j + 1
            word = s[i:i+count]
            res.append(word)

            i += count
        return res
