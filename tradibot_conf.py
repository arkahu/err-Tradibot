# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 22:30:43 2016

Configuration variables for Errbot plugin Tradibot
"""


chatroom = '#general'

vocabularyfile = 'vocabulary.txt'

#Ignore bot commands. All messages starting with any from this list are ignored.
ignore_commands = ('!',)

#Do not add to vocabulary words starting with any of these.
forbidden_words = ('!','http:','https:','www.','ftp:',)

#Remove characters from end of words, e.g. commas, and periods.
remove_chars = (',','.','?','!',)
