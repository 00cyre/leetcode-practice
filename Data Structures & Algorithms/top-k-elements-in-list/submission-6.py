class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        hmap = {}
        for i in nums:
            if i not in hmap:
                hmap[i] = 0
            hmap[i] += 1
        lnums = sorted(hmap.keys(), key=hmap.get,reverse=True)
        return lnums[:k]