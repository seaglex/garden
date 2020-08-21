class Solution(object):
    def findContentChildren(self, g, s):
        """
        :type g: List[int]
        :type s: List[int]
        :rtype: int
        """
        gs = sorted(g)
        ss = sorted(s)
        num_content = 0
        j = 0
        for i, child in enumerate(gs):
            while j < len(ss) and ss[j] < child:
                j = j + 1
            if j >= len(ss):
                return num_content
            num_content += 1
            j = j + 1
        return num_content

s = Solution()
print(s.findContentChildren([1,2,3], [1,1]))
print(s.findContentChildren([1,2], [1,2,3]))