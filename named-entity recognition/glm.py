from collections import defaultdict
from tagger import Tagger
import util

STOP = "STOP"
SUFFIX_LEN = 3


class GLM(Tagger):
    def __init__(self, param_file=None):
        super(GLM, self).__init__()
        self.params = None
        if param_file:
            self.params = util.read_params(param_file)

    def train(self, trainfile, iter_num=6):
        self.params = defaultdict(float)
        for i in xrange(iter_num):
            for sentence in util.sentence_iterator(util.file_iterator(trainfile)):
                sent, tags = zip(*sentence)
                self.perceptron(list(sent), list(tags))

    def perceptron(self, sentence, tags):
        z = self.viterbi(sentence)
        fxz = self.global_features(sentence, z)
        fxy = self.global_features(sentence, tags)
        for f in fxz:
            self.params[f] -= fxz[f]
        for f in fxy:
            self.params[f] += fxy[f]

    def local_features(self, tag2, tag1, tag, word):
        features = []
        features.append(self.__trigram(tag2, tag1, tag))
        features.append(self.__word_tag(word, tag))
        features.extend(self.__suffix(word, tag))
        return features

    def __trigram(self, tag2, tag1, tag):
        return "TRIGRAM:{}:{}:{}".format(tag2, tag1, tag)

    def __word_tag(self, word, tag):
        return "TAG:{}:{}".format(word, tag)

    def __suffix(self, word, tag):
        features = []
        for i in xrange(1, SUFFIX_LEN + 1):
            if i > len(word):
                continue
            suffix = word[-i:]
            features.append("SUFFIX:{}:{}:{}".format(suffix, i, tag))
        return features


    def global_features(self, sentence, tags):
        features = defaultdict(int)
        tags = ["*" , "*"] + tags
        for i in xrange(len(sentence)):
            local_features = self.local_features(tags[i], tags[i + 1], tags[i + 2], sentence[i])
            for f in local_features:
                features[f] += 1
        features[self.__trigram(tags[-2], tags[-1], STOP)] += 1
        return features

    def local_score(self, tag2, tag1, tag, word, score):
        if tag == STOP:
            score += self.params.get(self.__trigram(tag2, tag1, tag), 0)
        else:
            features = self.local_features(tag2, tag1, tag, word)
            for feature in features:
                score += self.params.get(feature, 0)
        return score

if __name__ == '__main__':
    #tagger = GLM(param_file="tag.model")
    tagger = GLM()
    tagger.train("gene.train")
    tagger.tag("gene.dev", "gene.counts")
