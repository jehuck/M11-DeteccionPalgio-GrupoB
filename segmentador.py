# -*- coding: utf-8 -*-
"""
Author: Jorge Huck
"""

import re
from nltk.tokenize import sent_tokenize, word_tokenize, TextTilingTokenizer

class Segmentador:
    """
    Segmentador de texto.
    """
    def __init__(self, text):
        self.text = text

    def sent_segmentation(self):
        """
        Segmenta el texto en oraciones.
        """
        return sent_tokenize(self.text)

    def para_segmentation(self):
        """
        Segmenta el texto en párrafos.
        """
        texto = self.text.split("\n\n")
        return list(filter(bool, texto))

    def word_segmentation(self):
        """
        Segmenta el texto en palabras.
        """
        return word_tokenize(self.text)

    def content_segmentation(self):
        """
        Implementa el algoritmo TextTiling para dividir el texto en segmentos de contenido coherente.
        """
        # Crear un TextTilingTokenizer
        tokenizer = TextTilingTokenizer()

        return tokenizer.tokenize(self.text)
    
    def sentence_segmentation(self, sentences_per_segment=3):
        """
        Segmenta el texto en segmentos de n oraciones.
        """
        segments = []
        current_segment = ""
        sentences = self.sent_segmentation()

        for sentence in sentences:
            current_segment += sentence
            if len(sent_tokenize(current_segment)) >= sentences_per_segment:
                segments.append(current_segment)
                current_segment = ""
        if current_segment:
            segments.append(current_segment)
        return segments