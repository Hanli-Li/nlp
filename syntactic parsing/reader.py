import json
from collections import defaultdict


class CNFTreeReader(object):
    def __init__(self):
        self.token_counts = defaultdict(int)
        self.syntag_counts = defaultdict(int)
        self.postag_counts = defaultdict(int)
        self.unary_counts = defaultdict(lambda: defaultdict(int))
        self.binary_counts = defaultdict(lambda: defaultdict(int))

    def read_corpus(self, file_path):
        with open(file_path, "r") as f:
            l = f.readline()
            while l:
                line = l.strip()
                if line:
                    tree = json.loads(line)
                    self.__read_tree(tree)
                l = f.readline()

    def __read_tree(self, tree):
        if len(tree) == 2:
            postag = tree[0]
            token = tree[1]
            self.postag_counts[postag] += 1
            self.token_counts[token] += 1
            self.unary_counts[postag][token] += 1
        elif len(tree) == 3:
            syntag = tree[0]
            self.syntag_counts[syntag] += 1
            self.binary_counts[syntag][(tree[1][0], tree[2][0])] += 1
            self.__read_tree(tree[1])
            self.__read_tree(tree[2])

    def print_raw_counts(self):
        for k, v in self.syntag_counts.iteritems():
            print v, "NON-TERMINAL", k

        for k, v in self.postag_counts.iteritems():
            print v, "NON-TERMINAL", k

        for postag in self.unary_counts:
            for token, v in self.unary_counts[postag].iteritems():
                print v, "UNARY", postag, token

        for syntag in self.binary_counts:
            for child, v in self.binary_counts[syntag].iteritems():
                print v, "BINARY", syntag, child[0], child[1]


if __name__ == '__main__':
    tr = CNFTreeReader()
    tr.read_corpus("train.dat")
    tr.print_raw_counts()