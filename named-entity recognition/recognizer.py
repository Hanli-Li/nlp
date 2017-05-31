from parser import Parser

class Recognizer(object):
  def __init__(self):
    self.train_set = None
    self.test_set = None
    self.validation
    self.tags = None

    self.emission_params = None
    self.transition_params = None

  def get_params(self, path, n=3):
    """
    use mle estimates directly
    """
    self.train_set = Parser(path)
    pair_dict, ngram_dict = self.train_set.get_raw_counts()
    self.tags = list(ngram_dict[0].keys())

    self.emission_params = {}
    for token, tag in pair_dict:
      self.emission_params[(token, tag)] = pair_dict[(token, tag)] * 1.0 / ngram_dict[0][tag]

    self.transition_params = {}
    for u, v, w in ngram_dict[n - 1]:
      self.transition_params[(w, u, v)] = ngram_dict[n - 1][(u, v, w)] * 1.0 / ngram_dict[n - 2][(u, v)]

  def recognize_tokens(self, path, n=3):
    self.test_set = Parser(path, with_tag=False)
    tag_seqs = []
    for sentence in self.test_set.sentences:
      tag_seqs.append(self.__generate_tags(sentence))
    self.test_set.tag_seqs = tag_seqs

  def __generate_tags(self, sentence):
    """
    viterbi algorithm
    """
    pi = [{} for i in xrange(len(sentence) + 1)]
    for i in xrange(len(pi)):
      pi_dict = pi[i]
      for tag_x in self.tags:
        pi_dict[tag_x] = {}
        for tag_y in self.tags:
          if i == 0:
            pi_dict[tag_x][tag_y] = 1
          else:
            pi_dict[tag_x][tag_y] = -1

    parent_tag = {}
    for i in xrange(1, len(sentence) + 1):
      for tag_v in self.tags:
        for tag_u in self.tags:
          for tag_w in self.tags:
            pi_temp = pi[i - 1][tag_w][tag_u] * self.transition_params[(tag_v, tag_w, tag_u)] * self.emission_params[(sentence[i - 1], tag_v)]
            if pi_temp > pi[i][tag_u][tag_v]:
              pi[i][tag_u][tag_v] = pi_temp
              parent_tag[(tag_u, tag_v)] = tag_w

    tag_seq = ["", ""]
    max_pi = -1
    for tag_v in self.tags:
      for tag_u in self.tags:
        pi_temp = pi[len(sentence)][tag_u][tag_v] * self.transition_params[("STOP", tag_u, tag_v)]
        if pi_temp > max_pi:
          max_pi = pi_temp
          tag_seq[0] = tag_u
          tag_seq[1] = tag_v

    while len(tag_seq) < len(sentence):
      tag_seq.insert(0, parent_tag[tuple(tag_seq[0:2])])

    return tag_seq

    def evaluate(self, path, n=3):
      self.validation = Parser(path)
      pass