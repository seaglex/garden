class Solution(object):
    def wordBreak(self, s, wordDict):
        """
        :type s: str
        :type wordDict: List[str]
        :rtype: List[str]
        """
        single_word_mat = self.get_single_mat(s, wordDict)
        words_mat = self.build_mat(s, single_word_mat)
        results = []
        Solution.get_all_lists(words_mat, len(s)-1, [None] * len(s), 0, results)
        return results

    def get_single_mat(self, s, wordDict):
        word_set = set(wordDict)
        num = len(s)
        single_word_mat = [[False]*num for _ in range(num)]
        for n in range(num):
            for m in range(n+1, num+1):
                if s[n:m] in word_set:
                    single_word_mat[n][m-1] = True
        return single_word_mat

    def build_mat(self, s, single_word_mat):
        num = len(s)
        words_mat = [[] for __ in range(num)]
        for iend in range(0, num):
            if single_word_mat[0][iend]:
                words_mat[iend].append((0, s[0:iend+1]))
            for th_iend in range(0, iend):
                if words_mat[th_iend] and single_word_mat[th_iend+1][iend]:
                    words_mat[iend].append((th_iend+1, s[th_iend+1:iend+1]))
        return words_mat

    @staticmethod
    def get_all_lists(words_mat, iend, partial, p_num, results):
        for beg, word in words_mat[iend]:
            if not beg:
                result = [None] * (p_num + 1)
                result[0] = word
                for n in range(1, p_num + 1):
                    result[n] = partial[p_num - n]
                results.append(' '.join(result))
                continue
            partial[p_num] = word
            Solution.get_all_lists(words_mat, beg-1, partial, p_num + 1, results)
        return


s = Solution()
print(s.wordBreak("catsanddog", ["cat", "cats", "and", "sand", "dog"]))
print(s.wordBreak("aaaaa", ["a", "aa", "aaa", "aaaa", "aaaaa"]))