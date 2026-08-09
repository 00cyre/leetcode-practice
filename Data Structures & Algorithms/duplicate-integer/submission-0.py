class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        values = set()
        for n in nums:
                values.add(n);
        if len(values) == len(nums):
            return False
        return True