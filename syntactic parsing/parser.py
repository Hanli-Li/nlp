from reader import CNFTreeReader
from collections import defaultdict

RARE_TOKEN_THRESHOLD = 5
ROOT_TAG = "SBARQ"

class PCFG(CNFTreeReader):
    def __init__(self):
        super(PCFG, self).__init__()
        self.binary_params = None
        self.unary_params = None
        self.pos_tags = None
        self.syn_tags = None

    def derive_pcfg(self, file_path):
        super(PCFG, self).read_corpus(file_path)
        self.pos_tags = self.postag_counts.keys()
        self.syn_tags = self.syntag_counts.keys()
        self.__replace_with_pseudo_words()
        self.__calculate_binary_rule_params()
        self.__calculate_unary_rule_params()

    def __replace_with_pseudo_words(self):
        localcounts = {}
        for postag in self.unary_counts:
            localcounts[postag] = defaultdict(int)
            for token in self.unary_counts[postag]:
                newtoken = token
                if self.token_counts[token] < RARE_TOKEN_THRESHOLD:
                    newtoken = map_to_pseudo_word(token)
                localcounts[postag][newtoken] += self.unary_counts[postag][newtoken]
        self.unary_counts = localcounts

    def __calculate_binary_rule_params(self):
        self.binary_params = {}
        for syntag in self.binary_counts:
            self.binary_params[syntag] = {}
            for children in self.binary_counts[syntag]:
                self.binary_params[syntag][children] = float(self.binary_counts[syntag][children])\
                                                        / float(self.syntag_counts[syntag])

    def __calculate_unary_rule_params(self):
        self.unary_params = {}
        for postag in self.unary_counts:
            self.unary_params[postag] = {}
            for token in self.unary_counts[postag]:
                self.unary_params[postag][token] = float(self.unary_counts[postag][token])\
                                                    / float(self.postag_counts[postag])


class Parser(PCFG):
    def __init__(self):
        super(Parser, self).__init__()

    def parse(self, test_file):
        with open(test_file, "r") as f:
            l = f.readline()
            while l:
                line = l.strip()
                if line:
                    sentence = line.split(" ")
                    self.__parse_sentence(sentence)
                l = f.readline()

    def __parse_sentence(self, sent):
        """
        CKY parsing algorithm
        """
        n = len(sent)
        pi = {}

        for i in xrange(n):
            if sent[i] not in self.token_counts or self.token_counts[sent[i]] < RARE_TOKEN_THRESHOLD:
                sent[i] = map_to_pseudo_word(sent[i])
            for x in self.pos_tags:
                pi[(i, i, x)] = 0
                if sent[i] in self.unary_params[x]:
                    pi[(i, i, x)] = self.unary_params[x][sent[i]]

        bp = {}
        for l in xrange(2, n + 1):
            for i in xrange(n - l + 1):
                j = i + l - 1
                tags = self.syn_tags
                if l == n:
                    tags = ROOT_TAG
                for x in tags:
                    pi[(i, j, x)] = -1
                    for s in xrange(i, j):
                        for y, z in self.binary_params[x]:
                            pi_temp = 0
                            if (i, s, y) in pi and (s + 1, j, z) in pi:
                                pi_temp = self.binary_params[x][(y, z)] * pi[(i, s, y)] * pi[(s + 1, j, z)]
                            if pi_temp > pi[(i, j, x)]:
                                pi[(i, j, x)] = pi_temp
                                bp[(i, j, x)] = (s, y, z)

        return self.__reconstruct()

    def __reconstruct(self, bp, start, end, tag, sent):
        tree = [tag]
        if start == end:
            tree.append(sent[start])
            return tree

        (s, y, z) = bp[(start, end, tag)]
        left = self.__reconstruct(self, bp, start, s, y, sent)
        right = self.__reconstruct(self, bp, s + 1, end, z, sent)
        tree.append(left)
        tree.append(right)
        return tree
