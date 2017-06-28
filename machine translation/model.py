from collections import defaultdict

NULL = "_NULL_"


class IBMModel(object):
    def __init__(self):
        self.t = None
        self.q = None

    def initialize(self, train_e, train_f):
        self.t = defaultdict(lambda: defaultdict(float))
        self.q = defaultdict(float)
        for e_sent, f_sent in IBMModel.corpora_iterator(train_e, train_f):
            es, m_k, fs, l_k = self.__split_sentences(e_sent, f_sent)
            for i in xrange(1, len(fs)):
                for j in xrange(len(es)):
                    self.t[es[j]][fs[i]] = 0.0
                    self.q[(j, i, l_k, m_k)] = 1.0 / (l_k + 1)

        for e in self.t:
            for f in self.t[e]:
                self.t[e][f] = 1.0 / float(len(self.t[e]))

    def em(self, train_e, train_f, ibm1=True, max_iter=5):
        c = defaultdict(float)
        n = 0
        while n < max_iter:
            c.clear()
            print 'iteration', n
            """
            e-step
            """
            for e_sent, f_sent in IBMModel.corpora_iterator(train_e, train_f):
                es, m_k, fs, l_k = self.__split_sentences(e_sent, f_sent)
                for i in xrange(1, m_k + 1):
                    partition = 0.0
                    for j in xrange(l_k + 1):
                        partition += self.q[(j, i, l_k, m_k)] * self.t[es[j]][fs[i]]
                    for j in xrange(l_k + 1):
                        delta = (self.q[(j, i, l_k, m_k)] * self.t[es[j]][fs[i]]) / partition
                        c[es[j]] += delta
                        c[(es[j], fs[i])] += delta
                        if not ibm1:
                            c[(j, i, l_k, m_k)] += delta
                            c[(i, l_k, m_k)] += delta
            """
            m-step
            """
            for e in self.t:
                for f in self.t[e]:
                    self.t[e][f] = c[(e, f)] / c[e]

            if not ibm1:
                for key in self.q:
                    self.q[key] = c[key] / c[key[1:]]
            n += 1

    def align(self, test_e, test_f, reverse=False):
        print "aligning..."
        alignments = {}
        corpora_iter = IBMModel.corpora_iterator(test_e, test_f)
        k = 1
        for e_sent, f_sent in corpora_iter:
            alignments[k] = []
            es, m_k, fs, l_k = self.__split_sentences(e_sent, f_sent)
            for i in xrange(1, len(fs)):
                idx = -1
                value = -1.0
                for j in xrange(len(es)):
                    if es[j] not in self.t or fs[i] not in self.t[es[j]] or (j, i, l_k, m_k) not in self.q:
                        continue
                    prob = self.q[(j, i, l_k, m_k)] * self.t[es[j]][fs[i]]
                    if prob > value:
                        value = prob
                        idx = j
                if not reverse:
                    alignments[k].append((idx, i))
                else:
                    alignments[k].append((i, idx))
            k += 1
        return alignments

    def __split_sentences(self, e_sent, f_sent):
        fs = [NULL]
        fs.extend(f_sent.split(" "))
        m_k = len(fs) - 1
        es = [NULL]
        es.extend(e_sent.split(" "))
        l_k = len(es) - 1
        return es, m_k, fs, l_k

    @staticmethod
    def write_alignments(alignments, outfile):
        with open(outfile, "w") as o:
            for k in xrange(1, len(alignments) + 1):
                for v in sorted(alignments[k], key=lambda x: x[1]):
                    o.write("%s %s %s\n" % (k, v[0], v[1]))

    @staticmethod
    def corpora_iterator(e_corpus, f_corpus):
        with open(e_corpus, "r") as e, open(f_corpus, "r") as f:
            le = e.readline()
            lf = f.readline()
            while le and lf:
                e_line = le.strip()
                f_line = lf.strip()
                if e_line and f_line:
                    yield e_line, f_line
                le = e.readline()
                lf = f.readline()
