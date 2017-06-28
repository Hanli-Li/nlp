from model import IBMModel


class IBM_1_2(IBMModel):
    def __init__(self, ibm1=False):
        super(IBM_1_2, self).__init__()
        self.ibm1 = ibm1

    def train(self, train_e, train_f):
        self.initialize(train_e, train_f)
        self.em(train_e, train_f)
        if not self.ibm1:
            self.em(train_e, train_f, ibm1=self.ibm1)


class Finder(object):
    def __init__(self):
        self.ordered = None
        self.reversed = None

    def align(self, train_e, train_f, test_e, test_f):
        model = IBM_1_2()
        print "p(f|e)..."
        model.train(train_e, train_f)
        self.ordered = model.align(test_e, test_f)

        print "p(e|f)..."
        model.train(train_f, train_e)
        self.reversed = model.align(test_f, test_e, reverse=True)

    def grow(self):
        print "growing..."
        alignments = {}
        for k in xrange(1, len(self.reversed) + 1):
            set_o = set(self.ordered[k])
            set_r = set(self.reversed[k])

            inter = set_o & set_r
            uni = set_o | set_r
            diff = uni - inter

            paired_e = set([v[0] for v in inter])
            paired_f = set([v[1] for v in inter])

            add_on = []
            for v in diff:
                if v[0] in paired_e and v[1] in paired_f:
                    continue

                for nbr in self.__get_neighbors(v):
                    if nbr in inter:
                        add_on.append(v)
                        break

            alignments[k] = list(inter)
            alignments[k].extend(add_on)
        return alignments

    def __get_neighbors(self, grid):
        neighbors = []
        for i in xrange(-1, 2):
            for j in xrange(-1, 2):
                neighbors.append((grid[0] + i, grid[1] + j))
        return neighbors


if __name__ == '__main__':
    model = IBM_1_2()
    model.train("corpus.en", "corpus.es")
    alignments = model.align("dev.en", "dev.es")
    IBMModel.write_alignments(alignments, "alignments.key")

    finder = Finder()
    finder.align("corpus.en", "corpus.es", "dev.en", "dev.es")
    growed_alignments = finder.grow()
    IBMModel.write_alignments(growed_alignments, "growed_alignments.key")
