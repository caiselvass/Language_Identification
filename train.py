import os
import re
from nltk.collocations import TrigramCollocationFinder
import json
import random

# Function to preprocess texts
def preprocess_text(text: str) -> str:
	new_text = ""
	sents = text.split('\n')
	for sent in sents:
		sent = sent.lower() # Lowercase
		sent = re.sub(r'\d', '', sent) # Remove digits
		sent = re.sub(r'\s+', ' ', sent) # Remove extra spaces
		sent = sent.strip() # Remove leading and trailing spaces
		if sent:
			new_text += sent + "  " # Add two spaces to separate sentences
	return new_text

# Load original texts
texts_original = {}
directory = os.fsencode('./original_langId')
for file in os.listdir(directory):
	filename = os.fsdecode(file)
	directoryname = os.fsdecode(directory)
	with open(directoryname + '/' + filename, 'r', encoding="utf-8") as file:
		data = file.read()
		texts_original[filename] = data

# Preprocess texts and save them in json files (one for train and one for test)
train, test = {}, {}
for file, text in texts_original.items():
	preprocessed_text = preprocess_text(text)
	if 'tst' in file:
		test[file[:3]] = [sentence for sentence in preprocessed_text.split("  ") if sentence] # Split sentences and remove empty strings
	else:
		train[file[:3]] = preprocessed_text

with open("./preprocessed_langId/train.json", "w") as train_file:
	json.dump(train, train_file)

with open("./preprocessed_langId/test.json", "w") as test_file:
	json.dump(test, test_file)
	
# Find trigrams and count unique characters for each language
trigrams, unique_chars = {}, {}
for language in train.keys():
	trigram_finder = TrigramCollocationFinder.from_words(train[language])
	tmp = {key: value for key, value in trigram_finder.ngram_fd.items() if value >= 5}
	
	trigrams[language] = tmp
	unique_chars[language] = len(set("".join("".join(a) for a in tmp.keys())))


trigrams_val, unique_chars_val = {}, {}

for language in train.keys():
	val_lang = train[language].split("  ")
	fold_size = len(val_lang)//3
	random.shuffle(val_lang)
	train_fold = val_lang[fold_size:]
	train_fold= "  ".join(train_fold)
	test_fold = val_lang[:fold_size]

	trigram_finder = TrigramCollocationFinder.from_words(train_fold)

	tmp = {key: value for key, value in trigram_finder.ngram_fd.items() if value > 5}
	tmp = {"".join(map(str, k)): v for k, v in tmp.items()}
	
	trigrams_val[language] = (tmp, test_fold)
	unique_chars_val[language] = len(set("".join("".join(a) for a in tmp.keys())))

# Convert trigrams to string in order to save the dictionary as a json file
def dict_trigramtuple_to_string(d: dict) -> dict:
	return {key: {"".join(k): v for k, v in value.items()} for key, value in d.items()}

# Save trigrams
with open("./weights/trigrams.json", "w") as trigrams_file:
	json.dump(dict_trigramtuple_to_string(trigrams), trigrams_file)

# Save unique_chars
with open("./weights/unique_chars.json", "w") as unique_chars_file:
	json.dump(unique_chars, unique_chars_file)

with open("./weights/validation_trigrams.json", "w") as validation_trigrams_file:
	json.dump(trigrams_val, validation_trigrams_file)

with open("./weights/validation_unique_chars.json", "w") as unique_chars_file_val:
	json.dump(unique_chars_val, unique_chars_file_val)