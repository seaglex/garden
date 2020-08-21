class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        num_indices = {}
        for i, n in enumerate(nums):
            if n not in num_indices:
                num_indices[n] = [i]
            else:
                num_indices[n].append(i)
        for i, n in enumerate(nums):
            m = target - n
            if m not in num_indices or (m == n and len(num_indices[m]) == 1):
                continue
            if m == n:
                return [i, num_indices[m][1]]
            return [i, num_indices[m][0]]
        return [0, 0]


print(Solution().twoSum([2, 7, 11], 9))