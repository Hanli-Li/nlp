# nlp

This repository is based on Natural Language Processing by Michael Collins at Columbia University. There are three independent tasks: named-entity recognition, syntactic parsing, machine translation.

## named-entity recognition

The goal of this task is to identify gene entities in biological text. Two models are explored here, one is Trigram Hidden Markov Model (HMM), the other is Global Linear Model (GLM). 

HMM models the joint probability of a sentence and a tag sequence. Under the independence assumption of HMM, a joint probability is factorized as products of transition probabilities and emmission probabilities. These probabilities are actually parameters of the model, and are estimated by MLEs derived based on counts from the training corpus.

GLM has three components. A function that generates possible output structures GEN(x) given an input x; a d-dimensional global feature vector f(x, y); and a d-dimensional weight vector v. Specifically, in our case, x is a sentence and y ∈ GEN(x) is a possible tag sequence. And feature vector f(x, y) can be represented as a sum of local feature vectors over each history and tag pair at each location in a sentence. The weight vector v is our parameter here, and is estimated by perceptron algorithm.

Given the models and corresponding parameters, the tag sequence of a new sentence is decoded by Viterbi algorithm which is implemented in tagger.py

## syntactic parsing

## machine translation

The goal of this task is to implement two translation models, IBM model 1 and IBM model 2, and apply these models to predict English/Spanish word alignments. Both models estimate the conditional probability of a foreign sentence f1 ... fm and an alignment a1 ... am given a particular English sentence e 1 · · · e l and length m



