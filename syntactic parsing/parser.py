from reader import CNFTreeReader
from collections import defaultdict

RARE_TOKEN_THRESHOLD = 5


class PCFG(CNFTreeReader):
    def __init__(self):
        super(PCFG, self).__init__()
        self.binary_params = defaultdict(int)
        self.unary_params = defaultdict(int)

    def derive_pcfg(self, file_path):
        super(PCFG, self).read_corpus(file_path)
        self.__replace_with_pseudo_words()
        self.__calculate_binary_rule_params()
        self.__calculate_unary_rule_params()

    def __replace_with_pseudo_words(self):
        localcounts = defaultdict(int)
        for syntag, token in self.unary_counts:
            newtoken = token
            if self.token_counts[token] < RARE_TOKEN_THRESHOLD:
                newtoken = map_to_pseudo_word(token)
            localcounts[(syntag, newtoken)] += self.unary_counts[(syntag, token)]
        self.unary_counts = localcounts

    def __calculate_binary_rule_params(self):
        for k in self.binary_counts:
            self.binary_params[k] = float(self.binary_counts[k]) / float(self.nonterminal_counts[k[0]])

    def __calculate_unary_rule_params(self):
        for k in self.unary_counts:
            self.unary_params[k] = float(self.unary_counts[k]) / float(self.nonterminal_counts[k[0]])


class Parser(PCFG):
    def __init__(self):
        super(Parser, self).__init__()

    def parse(self, test_file_path):
        with open(test_file_path, "r") as f:
            l = f.readline()
            while l:
                line = l.strip()
                if line:
                    sentence = line.split(" ")
                    self.__parse_sentence(sentence)
                l = f.readline()

    def __parse_sentence(self, sent):
        pass