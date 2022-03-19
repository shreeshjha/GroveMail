import pickle

class QSerializer:
    def __init__(self):
        self.elements = {}

    def add_element(self, name, obj):
        self.elements[name] = obj

    def encode(self):
        return pickle.dumps(self.elements)

    def decode(self, encoded_string):
        self.elements = pickle.loads(encoded_string) 

    def get_element(self, name):
        return self.elements[name]

    def get_element_names(self):
        return self.elements.keys()
    
    def clear(self):
        self.elements.clear()
        