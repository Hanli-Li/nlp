from collections import defaultdict
import util

RARE_TOKEN_THRESHOLD = 5
STOP = "STOP"

class Reader(object):
    def __init__(self, path, n=3):
        self.path = path
        self.n = n
        self.token_counts = defaultdict(int)
        self.pair_counts = defaultdict(int)
        self.ngram_counts = [defaultdict(int) for i in xrange(self.n)]

    def get_raw_counts(self):
        ngram_iterator = util.train_get_ngram(\
            util.sentence_iterator(\
                util.file_iterator(self.path)))

        for ngram in ngram_iterator:
            tags = zip(*ngram_pair)[1]
            for i in xrange(1, self.n):
                self.ngram_counts[i][tags[-1 - i:]] += 1

            if tags[-2] == "*":
                self.ngram_counts[self.n - 2][tags[0 : -1]] += 1

            if ngram_pair[-1][0]:
                self.ngram_counts[0][tags[-1]] += 1
                self.pair_counts[ngram[-1]] += 1
                self.token_counts[ngram[-1][0]] += 1

class HMM(Reader):
    def __init__(self, path, n=3):
        super(Processor, self).__init__(path, n)
        self.tags = set()
        self.tokens = set()
        self.rare_tokens = set()
        self.emission_params = {}
        self.transition_params = {}

    def train(self):
        super(Processor, self).get_raw_counts()
        self.__get_vocabulary()
        self.__get_rare_tokens()
        self.with_pseudo_words()
        self.calculate_params()

    def __get_vocabulary(self):
        for token, tag in self.pair_counts:
            self.tags.add(tag)
            self.tokens.add(token)

    def __get_rare_tokens(self):
        for k in token_counts:
            if token_counts[k] < RARE_TOKEN_THRESHOLD:
                self.rare_tokens.add(k)

    def with_pseudo_words(self):
        if not self.tags or not self.tokens or not self.rare_tokens:
            self.preprocess()

        localcounts = defaultdict(int)
        for token, tag in pair_counts:
            if token in self.rare_tokens:
                token = util.map_to_pseudo_word(token)
            localcounts[(token, tag)] += 1
        self.pair_counts = localcounts

    def calculate_params(self):
        self.__get_emission_params()
        self.__get_transition_paras()

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

class Tagger(Processor):
    def __init(self, train_path, n=3):
        super(Tagger, self).__init__(train_path, n)

    def tag_sentences(self. test_path):
        sentences = util.sentence_iterator(util.file_iterator(test_path))
        for sent in sentences:
            tags = self.__get_tags(sent)

    def __get_tags(self, sentence):
        """
        viterbi algorithm
        """
        n = len(sentence)
        pi = [{} for j in xrange(n + 1)]
        pi[0]["*"] = {"*": 1}
        pi[1]["*"] = {}
        for v in self.tags:
            pi[1]["*"][v] = -1

        for j in xrange(2, n + 1):
            for u in self.tags:
                pi[j][u] = {}
                for v in self.tags:
                    pi[j][u][v] = -1

        parent_tag = [{} for i in xrange(n + 1)]
        for j in xrange(1, n + 1):
            x = sentence[j - 1]
            if x not in self.tokens or x in self.tokens:
                x = util.map_to_pseudo_word(x)

            back_tags = self.tags
            if j <= 2:
                back_tags = ["*"]

            for u in pi[j]:
                for v in pi[j][tag_u]:
                    for w in back_tags:
                        pi_temp = 0
                        if (x, v) in self.emission_params:
                            pi_temp = pi[j - 1][w][u] * self.transition_params[(w, u, v)] * self.emission_params[(x, v)]
                        if pi_temp > pi[j][u][v]:
                            pi[j][u][v] = pi_temp
                            parent_tag[j][(u, v)] = w

        prev_tags = ["*"]
        if n > 1:
            prev_tags = self.tags

        tag_seq = ["" for j in xrange(n + 1)]
        max_pi = -1
        for u in prev_tags:
            for v in self.tags:
                pi_temp = pi[n][u][v] * self.transition_params[(STOP, u, v)]
                if pi_temp > max_pi:
                    max_pi = pi_temp
                    tag_seq[n - 1] = u
                    tag_seq[n] = v

        if n == 1:
            return tag_seq[1]

        for j in range(n - 2, 0, -1):
            tag_seq[j] = parent_tag[j + 2][tuple(tag_seq[j + 1 : j + 3])]

        return tag_seq[1:]