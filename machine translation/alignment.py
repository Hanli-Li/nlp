from model import IBMModel, IBM_1_2


class Finder(object):
    def __init__(self):
        self.model = IBM_1_2()
        self.ordered = None
        self.reversed = None
        self.alignments = None
        self.directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def align(self, train_e, train_f, test_e, test_f):
        print "p(f|e)..."
        self.model.train(train_e, train_f)
        self.ordered = self.model.align(test_e, test_f)

        print "p(e|f)..."
        self.model.train(train_f, train_e)
        self.reversed = self.model.align(test_f, test_e, reverse=True)

    def grow(self):
        self.alignments = {}
        for k in xrange(1, len(self.reversed) + 1):
            self.alignments[k] = []
            set_o = set(self.orderd[k])
            set_r = set(self.reversed[k])

            inter = set_o & set_r
            uni = set_o | set_r
            diff = uni - inter

            paired_e = set([v[0] for v in inter])
            paired_f = set([v[1] for v in inter])

            """
            max_f = list_o[-1][1]
            max_e = list_r[-1][0]

            unpaired_f = set(range(1, max_f + 1)) - paired_f
            unpaired_e = set(range(1, max_e + 1)) - paired_e
            """
            add_on = []
            for v in diff:
                if v[0] in paired_e and v[1] in paired_f:
                    continue

                for nbr in self.__get_neighbors(v):
                    if nbr in inter:
                        add_on.append(v)
                        break

            self.alignments.extend(list(inter))
            self.alignments.extend(add_on)
            self.alignments.sort(key=lambda x : x[1])

    def __get_neighbors(self, grid):
        neighbors = []
        for direction in self.directions:
            neighbors.add((grid[0] + direction[0], grid[1] + direction[1]))
        return neighbors

    def write_alignments(self, output_file):
        with open(output_file, "w") as o:
            for k in xrange(1, len(self.alignments) + 1):
                for v in self.alignments[k]:
                    o.write("%s %s %s\n" % (k, v[0], v[1]))


if __name__ == '__main__':
    finder = Finder()
    finder.align("corpus.en", "corpus.es", "dev.en", "dev.es")
    finder.grow()
    model.write_alignment("alignments2.key")










