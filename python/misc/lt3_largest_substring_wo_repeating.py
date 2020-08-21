class Solution(object):
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        last_poses = {}
        max_len = 0
        cur_beg = 0
        for n, c in enumerate(s):
            if c not in last_poses or last_poses[c] < cur_beg:
                last_poses[c] = n
                continue
            max_len = max(max_len, n - cur_beg)
            cur_beg = last_poses[c] + 1
            last_poses[c] = n
        max_len = max(max_len, len(s) - cur_beg)
        return max_len

s = Solution()
print(s.lengthOfLongestSubstring("pwwkew"))
print(s.lengthOfLongestSubstring("abba"))
print(s.lengthOfLongestSubstring("abcd"))
