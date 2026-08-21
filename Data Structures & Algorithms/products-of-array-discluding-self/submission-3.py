class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        #create array with length of nums where all numbers are 1
        # [1] * (len(nums))
        #init prefix, and iterate through array using range/enum
        #this is a delayed for loop, you first define the product of the index
        #and then later you actually calculate the product of the current index
        #that way the next time it runs it will always set the product of i to be the result of the previous iteration.
        #set product to be equal to prefix, then add the multiplication of current index to the original prefix variable
        #that way you will iterate through the array and have calculated all the prefixes of the array
        #postfixes is the same logic, but you walk from right to left, since then it will be behind but in the opposite direction
        prd = [1] * (len(nums))

        prefix = 1
        for i in range(len(nums)):
            prd[i] = prefix
            prefix *= nums[i]
        postfix = 1
        for i in range(len(nums)-1,-1,-1):
            prd[i] *= postfix
            postfix *= nums[i]
        return prd