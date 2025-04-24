import hashlib
import os

ADJECTIVES_PATH = "english/adjectives.txt"
NOUNS_PATH = "english/nouns.txt"

class NameGenerator:
    _instance = None
    def __init__(self):
        self.adjectives = self.load_words(ADJECTIVES_PATH)
        self.nouns = self.load_words(NOUNS_PATH)

    def load_words(self, path):
        words = []
        path = os.path.join(os.path.dirname(__file__), path)
        with open(path, "r") as file:
            words = file.read().splitlines()
        return words

    def get_name(self, seed):
        hash_value = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        adjective = self.adjectives[hash_value % len(self.adjectives)].capitalize()
        noun = self.nouns[hash_value % len(self.nouns)].capitalize()
        return adjective + noun
    
    @staticmethod
    def get_instance():
        if NameGenerator._instance is None:
            NameGenerator._instance = NameGenerator()
        return NameGenerator._instance