import random

# TODO: BNPR get doctrings on this then black and lint everything else

class InsultGenerator:
    def __init__(self, insults):
        self.insults = insults
    
    def generate(self):
        return random.choice(self.insults)


class InsultsFromFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.insults = self._load()

    def _load(self):
        with open(self.filepath) as f:
            content = f.readlines()
        clean_content = self.remove_newlines(content)
        return clean_content

    @staticmethod
    def remove_newlines(content):
        return [line.strip() for line in content]

    def __getitem__(self, key):
        return self.insults[key]

    def __len__(self):
        return len(self.insults)

       

insults_from_file = InsultsFromFile("./insults.txt")
insult_generator = InsultGenerator(insults=insults_from_file)


