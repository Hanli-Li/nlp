from collections import defaultdict

RARE_WORD_THRESHOLD = 5
STOPSIGN = "STOP"

class Parser(object):
  def __init__(self, path, n=3, with_tags=True):
    self.path = path
    self.n = n

    self.sentences = []
    self.tag_seqs = []
    self.token_dict = defaultdict(int)
    self.__initialize()
    self.__map_to_pseudo_words()

    self.emission_dict = None
    self.ngram_dict = None

  def __initialize(self):
    with open(self.path, "r") as f:
      l = f.readline()
      sent = []
      tags = (self.n - 1) * ["*"]
      while l:
        line = l.strip()
        if line:
          fields = line.split(" ")
          sent.append(fields[0])
          tags.append(fields[-1])
          self.token_dict(fields[0]) += 1
        elif sent:
          tags.append(STOPSIGN)
          self.sentences.append(sent)
          self.tag_seqs.append(tags)
          sent = []
          tags = (self.n - 1) * ["*"]

      if sent:
        tags.append(STOPSIGN)
        self.sentences.append(sent)
        self.tag_seqs.append(tags)

  def __map_to_pseudo_words(self):
    for sentence in self.sentences:
      for k in xrange(len(sentence)):
        if token_dict[sentence[k]] >= RARE_WORD_THRESHOLD:
          continue
        sentence[k] = self.__replace_token(sentence[k])

  def __replace_token(self, token):
    num = 0
    alpha = False
    caps = 0
    for char in token:
      if char.isdigit():
        num += 1
      elif char.isalpha():
        alpha = True
        if char.isupper():
          caps += 1

    if num == len(token):
      return "_NUMERIC_"
    elif num > 0 and alpha:
      return "_ALPHANUMERIC_"
    elif caps == len(token):
      return "_ALLCAPS_"
    elif token[-1].isupper():
      return "_LASTCAP_"
    return "_RARE_"

  def get_raw_counts(self):
    emission_dict = defaultdict(int)
    ngram_dict = [defaultdict(int) for i in xrange(self.n)]
    for i in xrange(len(self.sentences)):
      for j in xrange(len(self.sentences[i]) + 1):
        if j < len(self.sentences[i]):
          emission_dict[(sentences[i][j], tag_seqs[i][j + 2])] += 1
          ngram_dict[0][tag_seqs[i][j + 2]] += 1

        for k in xrange(1, self.n):
          ngram_dict[k][tuple(tag_seqs[i][j + 2 - k : j + 3])] += 1

    ngram_dict[self.n - 2][tuple((self.n - 1) * ["*"])] += len(self.sentences)
    return emission_dict, ngram_dict