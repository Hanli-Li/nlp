import util

STOP = "STOP"

class Tagger(object):
    def __init__(self):
        self.tags = ["I-GENE", "O"]
        
    def tag(self, testfile, outfile):
        with open(outfile, "w+") as o:
            sentences = util.sentence_iterator(util.file_iterator(testfile))
            for sent in sentences:
                tags = self.viterbi(sent)
                for i in xrange(len(sent)):
                    o.write("%s %s\n" % (sent[i], tags[i]))
                o.write("\n")

    def viterbi(self, sentence):
        tags = list(self.tags)
        n = len(sentence)

        pi = [{} for i in xrange(n + 1)]
        bp = [{} for i in xrange(n + 1)]

        pi[0]['*'] = {'*': 0}
        pi[1]['*'] = {}
        for v in tags:
            pi[1]['*'][v] = -float('inf')

        for k in xrange(2, n + 1):
            for u in tags:
                pi[k][u] = {}
                for v in tags:
                    pi[k][u][v] = -float('inf')
                    bp[k][(u, v)] = None

        bp = [{} for i in xrange(n + 1)]
        for k in xrange(1, n + 1):
            x = sentence[k - 1]
            W = tags
            if k < 3:
                W = ['*']
            for u in pi[k]:
                for v in pi[k][u]:
                    for w in W:
                        pi_temp = self.local_score(w, u, v, x, pi[k - 1][w][u])
                        if pi_temp > pi[k][u][v]:
                            pi[k][u][v] = pi_temp
                            bp[k][(u, v)] = w

        tag_seq = [None for i in xrange(n + 1)]
        prev_tags = ['*']
        if n > 1:
            prev_tags = tags

        max_pi = -float('inf')
        for u in prev_tags:
            for v in tags:
                pi_temp = self.local_score(u, v, STOP, None, pi[n][u][v])
                if pi_temp > max_pi:
                    max_pi = pi_temp
                    tag_seq[n - 1] = u
                    tag_seq[n] = v

        for k in xrange(n - 2, 0, -1):
            tag_seq[k] = bp[k + 2][(tag_seq[k + 1], tag_seq[k + 2])]

        return tag_seq[1:]

    def local_score(self, tag2, tag1, tag, word, score):
        raise NotImplementedError