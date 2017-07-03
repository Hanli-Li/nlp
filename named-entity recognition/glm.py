from collections import defaultdict
import util


class GLM(object):
    def __init__(self):
        self.params = None

    def local_score(tag2, tag1, tag, word, idx, pi, params):
        features = local_features(tag2, tag1, tag, word, idx)
        score = pi[idx - 1][tag2][tag1]
        for feature in features:
            score += params.get(feature, 0)
        return score

    def local_features(tag2, tag1, tag, word):
        features = []
        features.append("TRIGRAM" + ":" + tag2 + ":" + tag1 + ":" + tag)
        features.append("TAG" + ":" + word + ":" + tag)
        return features

    def train(trainfile):
        params = defaultdict(float)
        sentences = util.sentence_iterator(util.file_iterator(trainfile))
        for sentence in sentences:
            sent, tags = zip(*sentence)
            perceptron(list(sent), list(tags), params)

    def perceptron(sentence, tags, params, iter_num=5):
        for i in xrange(iter_num):
            z = viterbi(sentence, params)
            if z != tags:
                fxz = global_features(sentence, z)
                fxy = global_features(sentence, tags)
                for f in fxz:
                    params[f] -= 1
                for f in fxy:
                    params[f] += 1
    
    def global_features(sentence, tags):
        features = []
        tags = ["*" , "*"] + tags
        for i in xrange(len(sentence)):
            features.append(local_features(tags[i], tags[i + 1], tags[i + 2], sentence[i]))
            

if __name__ == '__main__':
    tag('tag.model', 'gene.counts', 'gene.dev')
