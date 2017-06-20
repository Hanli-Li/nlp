from collections import defaultdict


def corpora_iterator(e_corpus, f_corpus):
    with open(e_corpus, "r") as e, open(f_corpus, "r") as f:
        le = e.readline()
        lf = f.readline()
        while le and lf:
            e_line = le.strip()
            f_line = lf.strip()
            yield e_line, f_line
            le = e.readline()
            lf = f.readline()

def em(train_e, train_f, output, max_iter=5):
    print "train..."
    # initialize

    t = defaultdict(lambda: defaultdict(int))
    for e_sent, f_sent in corpora_iterator(train_e, train_f):
        fs = f_sent.split(" ")
        es = ["NULL"]
        es.extend(e_sent.split(" "))
        for e in es:
            for f in fs:
                t[e][f] += 1

    for e in t:
        for f in t[e]:
            t[e][f] = 1.0 / float(len(t[e]))

    with open(output, "w") as o:
        for e in sorted(t):
            for f in sorted(t[e]):
                o.write('{e} {f} {t}'.format(e=e, f=f, t=t[e][f]))
                o.write('\n')

    #pairs = defaultdict(lambda: defaultdict(float))
    c = defaultdict(float)

    # em algorithm
    """
    n = 0
    while n < max_iter:
        print 'iteration', n
        for e_sent, f_sent in corpora_iterator(train_e, train_f):
            fs = f_sent.split(" ")
            m_k = len(fs)

            es = ["Null"]
            es.extend(e_sent.split(" "))
            l_k = len(es) - 1
            for i in xrange(1, m_k + 1):
                partition = 0.0
                for j in xrange(l_k + 1):
                    partition += t[es[j]][fs[i]]
                for j in xrange(l_k + 1):
                    delta = t[es[j]][fs[i]] / partition
                    #pairs[es[j]][fs[i]] += delta
                    c[es[j]] += delta
                    c[(es[j], fs[i])] += delta
                    #c[(j, i, l_k, m_k)] += delta
                    #c[(i, l_k, m_k)] += delta

        for e in t:
            for f in t[e]:
                t[e][f] = c[(e, f)] / c[e]
        n += 1
    """

    return t


def align(test_e, test_f, outfile, t):
    print "test..."
    corpora_iter = corpora_iterator(test_e, test_f)
    with open(outfile, "w") as o:
        k = 1
        for e_sent, f_sent in corpora_iter:
            fs = [""]
            fs.extend(f_sent.split(" "))

            es = ["Null"]
            es.extend(e_sent.split(" "))
            for i in xrange(1, len(fs)):
                idx = -1
                value = -1.0
                for j in xrange(len(es)):
                    if es[j] not in t or fs[i] not in t[es[j]]:
                        continue
                    if t[es[j]][fs[i]] > value:
                        value = t[es[j]][fs[i]]
                        idx = j
                o.write("%s %s %s\n" %(k, idx, i))
            k += 1


if __name__ == '__main__':
    t = em("corpus.en", "corpus.es", "model.params")
    #align("dev.en", "dev.es", "alignment.key", t)