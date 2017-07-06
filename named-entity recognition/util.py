NUMERIC = "_NUMERIC_"
WITHNUM = "_WITHNUM_"
ALLCAPS = "_ALLCAPS_"
LASTCAP = "_LASTCAP_"
RARE = "_RARE_"
STOP = "STOP"
START = "*"


def file_iterator(path):
    with open(path, "r") as file:
        l = file.readline()
        while l:
            line = l.strip()
            if line:
                fields = line.split(" ")
                token = fields[0]
                if len(fields) > 1:
                    tag = fields[-1]
                    yield (token, tag)
                else:
                    yield token
            else:
                yield None
            l = file.readline()


def sentence_iterator(file_iterator):
    sentence = []
    for item in file_iterator:
        if not item:
            if sentence:
                yield sentence
                sentence = []
            else:
                raise StopIteration
        else:
            sentence.append(item)

    if sentence:
        yield sentence


def train_get_ngram(sentence_iterator, n):
    for sent in sentence_iterator:
        sent_ex = (n - 1) * [(None, START)]
        sent_ex.extend(sent)
        sent_ex.extend([(None, STOP)])

        for i in xrange(2, len(sent_ex)):
            yield sent_ex[i - 2 : i + 1]


def map_to_pseudo_word(token):
    #return RARE
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
        return NUMERIC
    elif num > 0 and alpha:
        return WITHNUM
    elif caps == len(token):
        return ALLCAPS
    elif token[-1].isupper():
        return LASTCAP
    return RARE


def read_params(param_file):
    mu = {}
    with open(param_file, "r") as f:
        l = f.readline()
        while l:
            line = l.strip().split(" ")
            key = line[0]
            val = line[1]
            mu[key] = float(val)
            l = f.readline()
    return mu
