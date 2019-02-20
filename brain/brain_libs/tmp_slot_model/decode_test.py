import os
import data_helper

sentence_file = "data/training_sentence.txt"
slot_file = "data/training_slot.txt"
sentence_training_file = "data/sentence_training.txt"
sentence_developing_file = "data/sentence_developing.txt"
slot_training_file = "data/slot_training.txt"
slot_developing_file = "data/slot_developing.txt"


class slot_decode(object):
    def __init__(self):
        (self.sentence_train,
        self.slot_train,
        self.sentence_dev,
        self.slot_dev,
        self.vocab_sentence,
        self.vocab_slot) = data_helper.prepare_data(
            "data",
            sentence_training_file,
            slot_training_file,
            sentence_developing_file,
            slot_developing_file,
            from_vocabulary_size=2000,
            to_vocabulary_size=2000,
            tokenizer=None)

    def decode(self):
        print(self.sentence_train)
