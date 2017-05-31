from parser import Parser

class Recognizer(object):
  def __init__(self, path_train, path_test, n=3):
    self.path_test = path_test
    self.path
    self.n = n
    self.parser = Parser(path_train)
    pass