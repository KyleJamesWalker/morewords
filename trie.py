# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from string import uppercase


class TrieNode:
    def __init__(self, letter=None):
        '''
          Trie node implementation.
          Class Member Data:
            letter - Current letter.
            children - Map of children.
            word - String of terminating word, None if not a word.
        '''
        self.word = None
        self.letter = letter
        self.children = {}

    def insert(self, word):
        '''
          Insert a word into Trie.
          Paramaters:
            word - String of the word to add.
        '''
        node = self
        word = word.upper()

        for letter in word:
            if letter not in node.children:
                # Create New Node
                node.children[letter] = TrieNode(letter)
            # Next Node
            node = node.children[letter]
        # No More to add set word to last node.
        node.word = word

    def get_child(self, letter):
        '''
          Gets requested child.
          Paramaters:
            letter - Next character to search for.
          Returns:
            TrieNode object for next requested letter.
            None if requested letter does not exist.
        '''
        if letter in self.children:
            return self.children[letter]
        return None


class Trie ():
    def __init__(self, file_name):
        '''
          Trie tree, loads contents of passed file.
          Class Member Data:
            root - Root node of tree.
        '''
        self.root = TrieNode()

        try:
            for cur_word in open(file_name):
                self.root.insert(cur_word.split(' ', 1)[0])
        except (IOError):
            print "Error Opening Database"

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
            _words.add(_cur.word)

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
            _words.sort()
            return _words
