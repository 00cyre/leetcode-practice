class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        #iterate through all numbers twice, comparing each index agains the other.
        #second loop has to start from i + 1 otherwise it will start from the same index.

        for i, n in enumerate(nums):
            for i2 in range(i + 1, len(nums)):
                if nums[i] + nums[i2] == target:
                    return [i,i2]