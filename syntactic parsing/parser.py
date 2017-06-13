from reader import CNFTreeReader
from collections import defaultdict

RARE_TOKEN_THRESHOLD = 5


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
                localcounts[postag][newtoken] += self.unary_counts[syntag][newtoken]
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
            pi
