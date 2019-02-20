"""Split data set into training and developing data

Usage:
    python3 split_data.py

Output:
    sentence_training.txt
    sentence_developing.txt
    slot_training.txt
    slot_developing.txt
"""

import random

sentence_file = "data/training_sentence.txt"
slot_file = "data/training_slot.txt"
sentence_training_file = "data/sentence_training.txt"
sentence_developing_file = "data/sentence_developing.txt"
slot_training_file = "data/slot_training.txt"
slot_developing_file = "data/slot_developing.txt"


def read_data(sentence_file, slot_file):
    with open(sentence_file, 'r', encoding='utf-8') as infile_sentence:
        with open(slot_file, 'r', encoding='utf-8') as infile_slot:
            sentence, slot = infile_sentence.readlines(), infile_slot.readlines()
    len_sentence = len(sentence)
    len_slot = len(slot)
    if len_sentence != len_slot:
        raise Exception('Length is not match!')
    return sentence, slot, len_sentence


def split_data(
        sentence_file,
        slot_file,
        sentence_training_file,
        sentence_developing_file,
        slot_training_file,
        slot_developing_file):
    sentence, slot, len_sentence = read_data(sentence_file, slot_file)
    num_dev = round(len_sentence/200)
    # Index for random sampling
    idx = random.sample(range(len_sentence), len_sentence)
    sentence_training = [sentence[i] for i in idx[:-num_dev]]
    with open(sentence_training_file, "w") as outfile:
        for line in sentence_training:
            outfile.write(str(line))
    sentence_developing = [sentence[i] for i in idx[-num_dev:]]
    with open(sentence_developing_file, "w") as outfile:
        for line in sentence_developing:
            outfile.write(str(line))
    slot_training = [slot[i] for i in idx[:-num_dev]]
    with open(slot_training_file, "w") as outfile:
        for line in slot_training:
            outfile.write(str(line))
    slot_developing = [slot[i] for i in idx[-num_dev:]]
    with open(slot_developing_file, "w") as outfile:
        for line in slot_developing:
            outfile.write(str(line))


if __name__ == '__main__':
        split_data(
            sentence_file,
            slot_file,
            sentence_training_file,
            sentence_developing_file,
            slot_training_file,
            slot_developing_file)
