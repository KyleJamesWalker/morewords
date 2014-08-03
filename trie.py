# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from string import uppercase


class TrieNode(object):
    # Note: Using __slots__ saves over 100MB of memory
    __slots__ = ('word', 'letter', 'value', 'children')

    def __init__(self, letter=None, value=0):
        '''
          Trie node implementation.
          Class Member Data:
            letter - Current letter.
            children - List of children.
            word - String of terminating word, None if not a word.
            value - Value of current trie node (cur letter + parents).
        '''
        self.word = None
        self.letter = letter
        self.value = value

        # Note: Using a list speeds up load time and access time, and almost
        #       zero change in runtime memory.
        self.children = [None] * len(uppercase)

    def get_child(self, letter):
        '''
          Gets requested child.
          Paramaters:
            letter - Next character to search for.
          Returns:
            TrieNode object for next requested letter.
            None if requested letter does not exist.
        '''
        return self.children[ord(letter) - ord('A')]


class Trie(object):
    def __init__(self, file_name):
        '''
          Trie tree, loads contents of passed file.
          Class Member Data:
            root - Root node of tree.
        '''
        self.letter_values = [
            1,      # A
            3,      # B
            3,      # C
            2,      # D
            1,      # E
            4,      # F
            2,      # G
            4,      # H
            1,      # I
            8,      # J
            5,      # K
            1,      # L
            3,      # M
            1,      # N
            1,      # O
            3,      # P
            10,     # Q
            1,      # R
            1,      # S
            1,      # T
            1,      # U
            4,      # V
            4,      # W
            8,      # X
            4,      # Y
            10,     # Z
        ]

        self.root = TrieNode()

        try:
            for cur_word in open(file_name):
                self.insert(cur_word.split(' ', 1)[0])
        except (IOError):
            print "Error Opening Word List"

    def insert(self, word):
        '''
          Insert a word into Trie.
          Paramaters:
            word - String of the word to add.
        '''
        node = self.root
        word = word.upper()

        value = 0

        for letter in word:
            let_idx = ord(letter) - ord('A')
            value += self.letter_values[let_idx]

            if node.children[let_idx] is None:
                # Create New Node
                node.children[let_idx] = TrieNode(letter, value)
            # Next Node
            node = node.children[let_idx]
        # No More to add set word to last node.
        node.word = word

    def contains(self, word):
        '''
          Search tree for specific word.
          Paramaters:
            word - String of word to search for.
          Returns:
            boolean: True if found, False if not found
        '''
        cur_node = self.root
        for char in word:
            cur_node = cur_node.get_child(char)
            if (cur_node is None):
                return False

        return True if cur_node.word is not None else False

    def get_words(self, letters, distance=0, _words=None, _cur=None):
        '''
            Find all words that can be spelled with passed letters.
            Parameters:
                letters: String of letters to spell with.
                distance: Int for allowed levenshtein. (TODO)
        '''

        # Seed recursive function
        seed = False
        if _words is _cur is None:
            if distance < 0 or distance > 2:
                raise ValueError("distance of {} unsupported".
                                 format(distance))
            seed = True
            letters = letters.upper()
            _words = set()
            _cur = self.root

        # Current Node is a word, add to set.
        if _cur.word:
            _words.add((_cur.word, _cur.value))

        # Distance Allowed try all paths
        if distance:
            for c in uppercase:
                next = _cur.get_child(c)
                if next:
                    self.get_words(letters,
                                   distance - 1,
                                   _words,
                                   next)

        # Try given letters
        for c in letters:
            next = _cur.get_child(c)
            if next:
                self.get_words(letters.replace(c, '', 1),
                               distance,
                               _words,
                               next)

        # Only return words on original call
        if seed:
            _words = list(_words)
            return sorted(_words, key=lambda x: (-x[1], x[0]))
