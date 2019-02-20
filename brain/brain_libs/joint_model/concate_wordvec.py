import data_utils

vocabulary_path = 'data/hospital/in_vocab_10696.txt'

vocab, rev_vocab = data_utils.initialize_vocabulary(vocabulary_path)
vocab_, embedding = data_utils.load_fasttext('word_vector/wiki.zh_classical.vec', 100,
                                  299)


print(len(rev_vocab))
print(rev_vocab[:10])
print(len(vocab_))
print(vocab_[:10])
print(embedding[:10])

new_list = rev_vocab[:10] + vocab_[:10]
print(new_list)
