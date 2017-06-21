from collections import defaultdict

NULL = "_NULL_"


class IBMModel(object):
    def __init__(self):
        self.t = defaultdict(lambda: defaultdict(float))
        self.q = defaultdict(float)

    def initialize(self, train_e, train_f):
        for e_sent, f_sent in IBMModel.corpora_iterator(train_e, train_f):
            fs = [NULL]
            es = [NULL]
            fs.extend(f_sent.split(" "))
            es.extend(e_sent.split(" "))
            m_k = len(fs) - 1
            l_k = len(es) - 1
            for i in xrange(1, len(fs)):
                for j in xrange(len(es)):
                    self.t[es[j]][fs[i]] = 0.0
                    self.q[(j, i, l_k, m_k)] = 1.0 / (l_k + 1)

        for e in self.t:
            for f in self.t[e]:
                self.t[e][f] = 1.0 / float(len(self.t[e]))

    def em(self, train_e, train_f, model1=True, max_iter=5):
        c = defaultdict(float)
        n = 0
        while n < max_iter:
            c.clear()
            print 'iteration', n
            """
            e-step
            """
            for e_sent, f_sent in IBMModel.corpora_iterator(train_e, train_f):
                fs = [NULL]
                fs.extend(f_sent.split(" "))
                m_k = len(fs) - 1

                es = [NULL]
                es.extend(e_sent.split(" "))
                l_k = len(es) - 1
                for i in xrange(1, m_k + 1):
                    partition = 0.0
                    for j in xrange(l_k + 1):
                        partition += self.q[(j, i, l_k, m_k)] * self.t[es[j]][fs[i]]
                    for j in xrange(l_k + 1):
                        delta = (self.q[(j, i, l_k, m_k)] * self.t[es[j]][fs[i]]) / partition
                        c[es[j]] += delta
                        c[(es[j], fs[i])] += delta
                        if not model1:
                            c[(j, i, l_k, m_k)] += delta
                            c[(i, l_k, m_k)] += delta
            """
            m-step
            """
            for e in self.t:
                for f in self.t[e]:
                    self.t[e][f] = c[(e, f)] / c[e]

            if not model1:
                for key in self.q:
                    self.q[key] = c[key] / c[key[1:]]
            n += 1

    def align(self, test_e, test_f, outfile):
        print "aligning..."
        corpora_iter = IBMModel.corpora_iterator(test_e, test_f)
        with open(outfile, "w") as o:
            k = 1
            for e_sent, f_sent in corpora_iter:
                fs = [NULL]
                fs.extend(f_sent.split(" "))
                m_k = len(fs) - 1

                es = [NULL]
                es.extend(e_sent.split(" "))
                l_k = len(es) - 1
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
                    o.write("%s %s %s\n" %(k, idx, i))
                k += 1

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


class IBM_1_2(IBMModel):
    def __init__(self, ibm1=True):
        super(IBM_1_2, self).__init__()
        self.ibm1 = ibm1

    def train(self, train_e, train_f):
        self.initialize(train_e, train_f)
        self.em(train_e, train_f)
        if not self.ibm1:
            self.em(train_e, train_f, model1=self.ibm1)


if __name__ == '__main__':
    model = IBM_1_2(ibm1=False)
    model.train("corpus.eng", "corpus.esp")
    model.align("dev.eng", "dev.esp", "alignment.key")