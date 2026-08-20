class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        pxrdcs = [1] * (len(nums))
        prefix = 1
        for i in range(len(nums)):
            pxrdcs[i] = prefix
            prefix *= nums[i]
        postfix = 1
        for i in range(len(nums)-1,-1,-1):
            pxrdcs[i] *= postfix
            postfix *= nums[i]
        return pxrdcs
