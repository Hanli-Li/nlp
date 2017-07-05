from collections import defaultdict
from tagger import Tagger
import util

STOP = "STOP"
START = "*"
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
            print 'iteration ' + str(i + 1)
            for sent in util.sentence_iterator(util.file_iterator(trainfile)):
                sentence, tags = zip(*sent)
                self.__perceptron(list(sentence), list(tags))
        # self.__write_params()

    def __perceptron(self, sentence, tags):
        z = self.viterbi(sentence)
        if z != tags:
            fxz = self.__feature_vec(sentence, z)
            fxy = self.__feature_vec(sentence, tags)
            for f in fxz:
                self.params[f] -= fxz[f]
            for f in fxy:
                self.params[f] += fxy[f]

    def __write_params(self, param_file="suffix_tagger.model"):
        with open(param_file, "w") as p:
            for k, v in self.params.iteritems():
                p.write("{} {}\n".format(k, v))

    def __local_features(self, tag2, tag1, tag, word):
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
                break
            suffix = word[-i:]
            features.append("SUFFIX:{}:{}:{}".format(suffix, i, tag))
        return features

    def __feature_vec(self, sentence, tags):
        vector = defaultdict(int)
        tags = [START , START] + tags
        for i in xrange(len(sentence)):
            features = self.__local_features(tags[i], tags[i + 1], tags[i + 2], sentence[i])
            for f in features:
                vector[f] += 1
        vector[self.__trigram(tags[-2], tags[-1], STOP)] += 1
        return vector

    def local_score(self, tag2, tag1, tag, word, score):
        if tag == STOP:
            score += self.params.get(self.__trigram(tag2, tag1, tag), 0)
        else:
            features = self.__local_features(tag2, tag1, tag, word)
            for f in features:
                score += self.params.get(f, 0)
        return score


if __name__ == '__main__':
    #tagger = GLM(param_file="tag.model")
    tagger = GLM()
    tagger.train("gene.train")
    tagger.tag("gene.dev", "gene.counts")
