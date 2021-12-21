from flair.data import Sentence
from flair.models import SequenceTagger

from flair.data import Corpus
from flair.datasets import CONLL_03
from flair.embeddings import WordEmbeddings, StackedEmbeddings, FlairEmbeddings

# 1. get the corpus
corpus: Corpus = CONLL_03()

# load tagger
tagger = SequenceTagger.load("flair/ner-english")

# make example sentence
sentence = Sentence("George Washington went to Washington")

# predict NER tags
tagger.predict(sentence)

# print sentence
print(sentence)

# print predicted NER spans
print('The following NER tags are found:')
# iterate over entities and print
for entity in sentence.get_spans('ner'):
    print(entity)