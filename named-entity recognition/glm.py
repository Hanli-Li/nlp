from collections import defaultdict
import util


STOP = "STOP"
SUFFIX_LEN = 3

class GLM(object):
    def __init__(self):
        self.params = None

    def train(self, trainfile):
        self.params = defaultdict(float)
        sentences = util.sentence_iterator(util.file_iterator(trainfile))
        for sentence in sentences:
            sent, tags = zip(*sentence)
            self.perceptron(list(sent), list(tags))

    def perceptron(self, sentence, tags, iter_num=5):
        for i in xrange(iter_num):
            z = viterbi(sentence, self.params)
            if z != tags:
                fxz = self.global_features(sentence, z)
                fxy = self.global_features(sentence, tags)
                for f in fxz:
                    self.params[f] -= 1
                for f in fxy:
                    self.params[f] += 1

    def local_features(self, tag2, tag1, tag, word):
        features = []
        features.append(self.__trigram_feature(tag2, tag1, tag))
        features.append(self.__word_tag_feature(word, tag))
        features.extend(self.__suffix_features(word, tag))
        return features

    def __trigram_feature(self, tag2, tag1, tag):
        return "TRIGRAM:{}:{}:{}".format(tag2, tag1, tag)

    def __word_tag_feature(self, word, tag):
        return "TAG:{}:{}".format(word, tag)

    def __suffix_features(self, word, tag):
        features = []
        for i in xrange(1, SUFFIX_LEN + 1):
            if i > len(word):
                continue
            suffix = word[-i:]
            features.append("SUFFIX:{}:{}:{}".format(suffix, i, tag))
        return features

    def global_features(self, sentence, tags):
        features = []
        tags = ["*" , "*"] + tags
        for i in xrange(len(sentence)):
            features.extend(self.local_features(tags[i], tags[i + 1], tags[i + 2], sentence[i]))
        features.append(self.__trigram_feature(tags[-2], tags[-1], STOP))

    def local_score(self, tag2, tag1, tag, word, idx, pi):
        score = pi[idx - 1][tag2][tag1]
        if tag == STOP:
            score += self.params.get(self.__trigram_feature(tag2, tag1, tag))
        else:
            features = self.local_features(tag2, tag1, tag, word)
            for feature in features:
                score += self.params.get(feature, 0)
        return score


    

            
