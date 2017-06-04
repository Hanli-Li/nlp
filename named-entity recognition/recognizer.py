from parser import Parser


class Recognizer(object):
  def __init__(self):
    self.train_set = None
    self.test_set = None
    self.tags = None

    self.emission_params = None
    self.transition_params = None

  def get_params(self, path, n=3):
    """
    use mle estimates directly
    """
    self.train_set = Parser(path)
    self.train_set.map_to_pseudo_words()
    pair_dict, ngram_dict = self.train_set.get_raw_counts()
    self.tags = list(ngram_dict[0].keys())

    self.emission_params = {}
    for token, tag in pair_dict:
      self.emission_params[(token, tag)] = pair_dict[(token, tag)] * 1.0 / ngram_dict[0][tag]

    self.transition_params = {}
    for w, u, v in ngram_dict[n - 1]:
      self.transition_params[(v, w, u)] = ngram_dict[n - 1][(w, u, v)] * 1.0 / ngram_dict[n - 2][(w, u)]

  def tag_tokens(self, path, n=3):
    self.test_set = Parser(path, with_tags=False)
    
    tag_seqs = []
    for sentence in self.test_set.sentences:
      tag_seqs.append(self.__generate_tags(sentence))
    self.test_set.tag_seqs = tag_seqs

  def __generate_tags(self, sentence):
    """
    viterbi algorithm
    """
    n = len(sentence)
    pi = [{} for j in xrange(n + 1)]
    pi[0]["*"] = {"*": 1}
    pi[1]["*"] = {}
    for tag in self.tags:
      pi[1]["*"][tag] = -1

    for j in xrange(2, n + 1):
      for tag_x in self.tags:
        pi[j][tag_x] = {}
        for tag_y in self.tags:
          pi[j][tag_x][tag_y] = -1

    for j in xrange(n + 1):
      print pi[j]

    parent_tag = [{} for i in xrange(n + 1)]
    for j in xrange(1, n + 1):
      back_tags = self.tags
      if j <= 2:
        back_tags = ["*"]
      for tag_u in pi[j]:
        for tag_v in pi[j][tag_u]:
          for tag_w in back_tags:
            pi_temp = 0
            if (sentence[j - 1], tag_v) in self.emission_params:
              pi_temp = pi[j - 1][tag_w][tag_u] * self.transition_params[(tag_v, tag_w, tag_u)] * self.emission_params[(sentence[j - 1], tag_v)]
            if pi_temp > pi[j][tag_u][tag_v]:
              pi[j][tag_u][tag_v] = pi_temp
              parent_tag[j][(tag_u, tag_v)] = tag_w

    prev_tags = ["*"]
    if n > 1:
      prev_tags = self.tags

    tag_seq = ["" for j in xrange(n + 1)]
    max_pi = -1
    for tag_u in prev_tags:
      for tag_v in self.tags:
        pi_temp = pi[n][tag_u][tag_v] * self.transition_params[("STOP", tag_u, tag_v)]
        if pi_temp > max_pi:
          max_pi = pi_temp
          tag_seq[n - 1] = tag_u
          tag_seq[n] = tag_v

    if n == 1:
      return tag_seq[1]

    for j in range(n - 2, 0, -1):
      tag_seq[j] = parent_tag[j + 2][tuple(tag_seq[j + 1 : j + 3])]

    return tag_seq[1:]

if __name__ == "__main__":
  recognizer = Recognizer()
  recognizer.get_params("./gene.train")
  recognizer.tag_tokens("./test.dev")

  """
  f = file("gene_dev.p1.out", "w+")
  comp_set = Parser("./gene_key.dev")
  
  print len(comp_set.tag_seqs) == len(recognizer.test_set.tag_seqs)

  true_gene_tag_num = 0
  pred_gene_tag_num = 0
  common_gene_tag_num = 0
  for i in xrange(len(comp_set.tag_seqs)):
    print recognizer.test_set.tag_seqs[i]
    print comp_set.tag_seqs[i]
    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    for j in xrange(len(comp_set.tag_seqs[i])):
      if recognizer.test_set.tag_seqs[i][j] == "I-GENE":
        pred_gene_tag_num += 1
      if comp_set.tag_seqs[i][j] == "I-GENE":
        true_gene_tag_num += 1
      if recognizer.test_set.tag_seqs[i][j] == "I-GENE" and comp_set.tag_seqs[i][j] == "I-GENE":
        common_gene_tag_num += 1

      f.write("%s %s\n" %(comp_set.sentences[i][j], recognizer.test_set.tag_seqs[i][j]))
    f.write("\n")
  f.close()
  prec = common_gene_tag_num * 1.0 / pred_gene_tag_num
  rec = common_gene_tag_num * 1.0 / true_gene_tag_num
  fscore = (2 * prec * rec) / (prec + rec)
  print "Precision: %f" % prec
  print "Recall: %f" % rec
  print "F Score: %f" % fscore
  """