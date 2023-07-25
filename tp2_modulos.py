import os
import numpy as np
import nltk
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN

# Importo las librerías necesarias para procesar los textos
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

import re




class CleanText():
    
    def __init__(self, text, language="english"):
        
        self.text = text
        self.language = language
        self.clean_text = None
        self.remove_spec_text = None
        self.remove_stop_text = None
        self.lemma_text = None

        self.SPECIAL_CHARACTERS = []

        self.SPECIAL_CHARACTERS.extend(map(chr, range(0, 32)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(33, 48)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(58, 65)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(91, 97)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(123, 225)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(226, 233)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(234, 237)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(238, 241)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(242, 243)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(244, 250)))
        self.SPECIAL_CHARACTERS.extend(map(chr, range(251, 880)))

        nltk.download('punkt')
    
    def removePatterns(self):
        
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
        )
        self.text = str(self.text)
        self.clean_text = self.text.lower()
        self.clean_text = re.sub(r"\s{2,}", " ", self.clean_text)
        self.clean_text = re.sub(r"\n", " ", self.clean_text)
        self.clean_text = re.sub(r"\d+", " ", self.clean_text)
        self.clean_text = re.sub(r"^\s+", " ", self.clean_text)
        self.clean_text = re.sub(r"\s+", " ", self.clean_text)
        
        for a, b in replacements:
            self.clean_text = self.clean_text.replace(a, b).replace(a.upper(), b.upper())
        
        return self.clean_text
    
    def removeSpecChars(self):
        
        remove_patterns = self.removePatterns()
        tokens = list(word_tokenize(remove_patterns))
        clean_tokens = tokens.copy()
        for i in range(len(clean_tokens)):
            for special_character in self.SPECIAL_CHARACTERS:
                clean_tokens[i] = clean_tokens[i].replace(special_character, '')            
            
        clean_tokens = [token for token in clean_tokens if token]        
        self.remove_spec_text = " ".join(clean_tokens)        
        
        return self.remove_spec_text       
    
    def RemoveStopText(self):
        
        st = ["'", "!", '"', "#", "$", "%", "&", "*", "+", "-", ".", "/", "<", "=", '>', "?",
          "@", "[", "\\", "]", "^", "_", '`', "{", "|", "}", '~']
        
        sw = stopwords.words(self.language) + st
        text = list(word_tokenize(self.removeSpecChars()))
        text = [w for w in text if not w in sw]
        self.remove_stop_text = " ".join(text)
        
        return self.remove_stop_text
    
    def lemmatizeText(self):
        
        lemmatizer = WordNetLemmatizer()
        list_lemma_text = []
        tokens = word_tokenize(self.RemoveStopText())
        
        for token in tokens:
            lemmetized_word = lemmatizer.lemmatize(token)
            list_lemma_text.append(lemmetized_word)
        
        self.lemma_text = " ".join(list_lemma_text)
        
        return self.lemma_text
    

