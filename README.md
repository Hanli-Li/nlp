# nlp

This repository is based on Natural Language Processing by Michael Collins at Columbia University. There are three independent tasks: named-entity recognition, syntactic parsing, machine translation.

## named-entity recognition

The goal of this task is to identify gene entities in biological text. Two models are explored here, one is Trigram Hidden Markov Model (HMM), the other is Global Linear Model (GLM). 

HMM models the joint probability of a sentence and a tag sequence. Under the independence assumption of HMM, a joint probability is factorized as products of transition probabilities and emmission probabilities. These probabilities are actually parameters of the model, and their MLEs are derived based on counts from the training corpus.

GLM has three components. A function that generates possible output structures GEN(x) given an input x; a d-dimensional global feature vector f(x,y); and a d-dimensional weight vector v. In our case, x is a sentence and y ∈ GEN(x) is a possible tag sequence. And feature vector f(x,y) can be represented as a sum of local feature vectors over each history and tag pair at each location in a sentence. The weight vector v is our parameter here, and is estimated by perceptron algorithm.

Given the models and corresponding parameters, the tag sequence of a new sentence is decoded by Viterbi algorithm which is implemented in tagger.py

## syntactic parsing

The goal of this task is to train a probabilistic context-free grammar (PCFG) for syntactic parsing. PCFG is defined as a tuple G = (N, Σ, S, R, q), where N is the set of non-terminals, Σ is the vocabulary, S is a root symbol, R is a set of rules, and q is the rule parameters. We will assume that the grammar is in Chomsky normal form (CNF). This means all rules in R will be either binary rules X → Y1 Y2 where X, Y1, Y2 ∈ N or unary rules X → Z where X ∈ N and Z ∈ Σ.

Generally, the annotated [parse tree](https://en.wikipedia.org/wiki/Parse_tree#Constituency-based_parse_trees) is not in Chomsky normal from. To conform to CNF, two transformations are applied here. The first is to collapse illegal unary rules of the form X → Y → Z to X + Y → Z, where X, Y ∈ N and Z ∈ Σ. The second is to split n-ary rules X → Y1 Y2 Y3 into right branching binary rules X → Y1 X and X → Y2 Y3, where X, Y1, Y2, Y3 ∈ N. In our datasets, each CNF tree is represented as a recursive, multi-dimensional JSON array.

One limitation of common parse tree is its strong independence assumption, that is, rules are generated independently of their parent non-terminals. To condition on parent non-terminals, each non-terminal is augmented with the symbol of its parent, this transformation is called vertical markovization. The previous transformation is then applied to make trees conform to CNF.

The MLEs of unary and binary rule parameters are derived based on counts from the training corpus. With a PCFG in CNF, the parse tree of a new sentence is generated by CKY algorithm.

## machine translation

The goal of this task is to implement two translation models, IBM model 1 and IBM model 2, and apply these models to predict English/Spanish word alignments. Both models estimate the conditional probability p of a foreign sentence and an alignment given a particular English sentence and the length of the foreign sentence. The alignment is a map of word indices between an English sentence and foreign sentence pair, where each foreign word is mapped to the most likely English word under translation models.

Under the independence assumption of IBM models, p is factorized into products of translation probabilities t and alignment probabilities q, and their MLEs are obtained through the EM algorithm. The difference between IBM model 1 and IBM model 2 is that the former model takes q parameters to be uniform over all words in the English sentence paired with each foreign sentence. The EM algorithm for IBM model 2 is sensitive to initialization, depending on the initial values of parameters, it may converge to different local optima of the log-likelihood function. However, for IBM model 1, the EM algorithm is guaranteed to converge to the global optimum. Therefore, the general training procedure is to first obtain the MLEs of t parameters with the EM algorithm for IBM model 1. And then estimate parameters of IBM Model 2 with another round of the EM algorithm. This time, t parameters are initialized with MLEs of IBM model 1, and q parameters are initialized by random values.

Finally, this task also explores alignments growing process that serves as a crucial first step to extract a lexicon for phrase-based translation.
