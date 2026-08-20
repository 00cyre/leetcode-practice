class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        hmap = {}
        for v in nums:
            if v not in hmap:
                hmap[v] = 0;
            hmap[v] += 1;
        slist = sorted(hmap.keys(), key=hmap.get, reverse=True)
        return slist[:k]