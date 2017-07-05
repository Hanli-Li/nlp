from collections import defaultdict
from tagger import Tagger
import util

RARE_TOKEN_THRESHOLD = 5
STOP = "STOP"
START = "*"


class Reader(object):
    def __init__(self, n=3):
        self.n = n
        self.token_counts = defaultdict(int)
        self.pair_counts = defaultdict(int)
        self.ngram_counts = [defaultdict(int) for i in xrange(self.n)]

    def get_raw_counts(self, file_path):
        ngram_iterator = util.train_get_ngram(
            util.sentence_iterator(
                util.file_iterator(file_path)), self.n)

        for ngram in ngram_iterator:
            tags = zip(*ngram)[1]
            for i in xrange(1, self.n):
                self.ngram_counts[i][tags[-1 - i:]] += 1

            if tags[-2] == START:
                self.ngram_counts[self.n - 2][tags[0:-1]] += 1

            if ngram[-1][0]:
                self.ngram_counts[0][tags[-1]] += 1
                self.pair_counts[ngram[-1]] += 1
                self.token_counts[ngram[-1][0]] += 1


class HMM(Reader, Tagger):
    def __init__(self, n=3, glm=False):
        Reader.__init__(self, n=n)
        Tagger.__init__(self, glm=glm)
        self.tags = set()
        self.tokens = set()
        self.emission_params = {}
        self.transition_params = {}

    def train(self, file_path):
        self.get_raw_counts(file_path)
        self.__with_pseudo_words()
        self.calculate_params()

    def __with_pseudo_words(self):
        localcounts = defaultdict(int)
        for token, tag in self.pair_counts:
            newtoken = token
            if self.token_counts[token] < RARE_TOKEN_THRESHOLD:
                newtoken = util.map_to_pseudo_word(token)
            localcounts[(newtoken, tag)] += self.pair_counts[(token, tag)]
            self.tags.add(tag)
            self.tokens.add(newtoken)
        self.pair_counts = localcounts

    def calculate_params(self):
        self.__get_emission_params()
        self.__get_transition_params()

    def __get_emission_params(self):
        for pair in self.pair_counts:
            self.emission_params[pair] = float(self.pair_counts[pair]) / float(self.ngram_counts[0][pair[-1]])

    def __get_transition_params(self):
        """
        use mle estimates directly
        """
        for ngram in self.ngram_counts[self.n - 1]:
            self.transition_params[ngram] = \
                float(self.ngram_counts[self.n - 1][ngram]) / float(self.ngram_counts[self.n - 2][ngram[:-1]])

    def local_score(self, tag2, tag1, tag, word, score):
        score *= self.transition_params.get((tag2, tag1, tag), 0)
        if tag != STOP:
            score *= self.emission_params.get((word, tag), 0)
        return score


if __name__ == '__main__':
    train_file = "gene.train"
    test_file = "gene.dev"
    output_file = "gene.counts"

    model = HMM()
    model.train(train_file)
    model.tag(test_file, output_file)