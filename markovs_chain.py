import numpy as np
from pprint import pprint
data = open('books/voyna-i-mir_utf-8.txt', encoding='utf8').read()

ind_words = data.split()

def make_pairs(ind_words):
    for i in range(len(ind_words) - 1):
        yield (ind_words[i], ind_words[i + 1])

pair = make_pairs(ind_words)

word_dict = {}
for word_1, word_2 in pair:
    if word_1 in word_dict.keys():
        word_dict[word_1].append(word_2)
    else:
        word_dict[word_1] = [word_2]

first_word = np.random.choice(ind_words)
chain = []
while first_word.islower():
    chain = [first_word]
    n_words = 3
    first_word = np.random.choice(ind_words)

    for i in range(n_words):
        chain.append(np.random.choice(word_dict[chain[-1]]))

print(' '.join(chain))