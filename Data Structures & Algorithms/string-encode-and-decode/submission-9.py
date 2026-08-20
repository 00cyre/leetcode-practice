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

            # Find the delimiter after the length
            while s[j] != "#":
                j += 1

            length = int(s[i:j])

            # Move past "length#"
            i = j + 1

            # Extract exactly `length` characters
            res.append(s[i:i + length])

            # Move to the next encoded string
            i += length

        return res
