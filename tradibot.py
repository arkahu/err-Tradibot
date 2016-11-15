# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 11:50:59 2016

Author: Arttu Huttunen, 2016
Oulu, Finland. <arttuhut@gmail.com>
"""

from errbot import BotPlugin, botcmd
import random, json
       
#vocabulary words are of class vocWord
class vocWord:
    """Stores a word and relations it has to other words."""
      
    def __init__(self, newWord):
        self.word = newWord
        self.occurrence = 1
        self.links = {'':0}

    #increase occurrence        
    def incOcc(self):
        if self.occurrence < 255:
            self.occurrence = self.occurrence + 1

    #decrease occurrence
    def decOcc(self):
         if self.occurrence > 0:
             self.occurrence = self.occurrence - 1
                   
    def linkWords(self, word, amount=1):
        if word != self.word:
            #if word is in links dictionary increase link strength
            if  word in self.links: #self.links.get(word) != None:
                self.links[word] = self.links[word] + amount
                if self.links[word] > 255:
                    self.links[word] = 255
            #if not in links replace lowest strength link with word
            else:
                if len(self.links) > 7:
                    del self.links[min(self.links, key=self.links.get)]
                self.links[word] = 1

    #reduce random link strength
    def decLinks(self):
        key = random.choice(list(self.links.keys()))
        if self.links[key] > 0:  
            self.links[key] = self.links[key] - 1
            
    def giveLink(self):
        keys = []
        values = []
        a=0
        for item in self.links.items():
            keys.append(item[0])
            a= a + item[1]
            values.append(a)
                
        rnd = random.randint(0,values[-1])
        b = 0        
        while b < len(self.links):
            if rnd < values[b]:
                return keys[b]
            b += 1
        else:
            return keys[-1]
            
    def dataToList(self):
        output = [self.word, self.occurrence, self.links]
        return output


class Tradibot(BotPlugin):
    """Tragic discussion bot -plugin bor Errbot. Tragic refers to the development process.
    The bot takes all messages posted to a channel and makes a vocabulary of
    the words, then semi-randomly talks back."""
    #Tragic discussion bot

#    def __init__(self, dummy=None):
#        self.vocabularyfile = 'vocabulary.dat.gz'
#        
#        #self.activity = 0
#        #self.muted = True
#        #self.enabled = False
#        #self.recent = []
#
#        #OR ?!?!?!?!
#        self['activity'] = 0    #0-255
#        self['muted'] = True     
#        self['enabled'] = False 
#        self['recent'] = ['']*8 #set by using: self['recent'][0]
#        
#        self['urge'] = 0  # the urge to talk 0-255

#    def __init__(self):
#        self.vocabularyfile = 'vocabulary.dat.gz'
#
#        self.activity = 1    #0-255
#        self.muted = True     
#        self.enabled = False 
#        self.recent = ['']*8 #set by using: self['recent'][0]
#        
#        #self.chatroom = self.build_identifier('???')
#        self.chatroom = self.query_room("#general") #*******SET #channel 
#        self.urge = 0  # the urge to talk 0-255
#        self['vocabulary'] = [vocWord('init')]


#Safer to make these non-persistent!   
   
    #Here are commands for adminstering the bot   
    @botcmd
    def tradibot(self, msg, args):    
        if args == 'mute':
            """No speaking."""
            self.muted = True
            return 'Tradibot muted'
            
        elif args == 'unmute':
            self.muted = False
            return 'Tradibot unmuted' 
            
        elif args == 'enable':
            self.enabled = True
            return 'Tradibot enabled'

        elif args == 'disable':
            """No word collecting or speaking."""
            self.enabled = False
            return 'Tradibot disabled'
           
        elif args == 'status':
            statusList = ['activity: ', str(self.activity), ' muted: ', 
                      str(self.muted), ' enabled: ', str(self.enabled), 'urge: ',
                        str(self.urge), 'dictionary size: ', str(len(self['vocabulary']))]
            statusList.extend(self.recent)
            state = ' '.join(statusList)
            return state

        elif args == 'talknow':
            """Bot talks now."""
            self.urge = 255
            self.speak()
            return 'I speak.'
            
        elif args == 'save':
            """Saves the vocabulary to a file."""
            data = []
            for item in self['vocabulary']:
                data.append(item.dataToList())
            with open(self.vocabularyfile, 'w') as outfile:
                json.dump(data, outfile) 
            return 'Vocabulary saved'
        
        elif args.split()[0] =='activity':
            """Sets the value how often the bot speaks. !tradibot activity 50"""
            self.activity = int(args.split()[1])
            if self.activity >255:
                self.activity = 255
            return 'Activity set to ' + self.activity
        
        elif args == 'initialize':
            """Initializes bot variables""" 
            #if the __init__ does not work, comment out and use this manually.
            self.vocabularyfile = 'vocabulary.txt'
    
            self.activity = 1    #0-255
            self.muted = True     
            self.enabled = False 
            self.recent = ['']*8 #set by using: self['recent'][0]
            
            #self.chatroom = self.build_identifier('???')
            self.chatroom = self.query_room("#general")
            self.urge = 0  # the urge to talk 0-255
            self['vocabulary'] = [vocWord('init')]
            return 'Initialized'
   
    #Actual logic starts here    
    
    def sanitize(self, word):
        #remove commands weblinks...
        if len(word) > 32:
            good = False
        elif word[0] == '!':
            good = False            
        elif word[:4] == 'www.':
            good = False
        elif word[:5] == 'http:':
            good = False
        elif word[:6] == 'https:':
            good = False         
        elif word[:4] == 'ftp:':
            good = False  
        elif word[:4] == 'ftp:':
            good = False         
        
        else:
            good = True        
        return good
    
    def speak(self):
        #if wants to speak
        sentence = ''
        vocab = self['vocabulary']
        topic = random.choice(self.recent)
        rnd = random.randint(0,255)
        while self.urge > rnd:
            self.urge = self.urge - 10
            if self.urge <0:
                self.urge = 0
            for item in vocab:
                if item.word == topic:
                    relation = item.giveLink()
                    sentence += relation +' '
                    topic = relation
                    break

        #talk to chat
        if sentence != '':                               
            self.send(self.chatroom, sentence,)
        #return sentence

 
    def vocUpdate(self, word):
        vocab = self['vocabulary']
        #vocabulary is vocab[vocWord(word1),vocWord(word2)]
        for index, item in enumerate(vocab):
            if word == item.word:
                item.incOcc()
                #sort by order of occurrence
                pos = index                
                while pos > 0:
                    if vocab[pos].occurrence > vocab[pos-1].occurrence:
                        vocab[pos],vocab[pos-1] = vocab[pos-1], vocab[pos]
                    pos = pos - 1                                    
                #links ...
                item.linkWords(self.recent[-1])
                item.linkWords(self.recent[-2])
                item.linkWords(self.recent[-3])
                item.linkWords(self.recent[-4])
                item.linkWords(self.recent[-5])
                item.linkWords(self.recent[-6])
                item.linkWords(self.recent[-7])
                item.linkWords(self.recent[-8])            
                break
        else:
            if len(vocab) >= 8192:
                vocab.pop(8001)
            vocab.append(vocWord(word))
            #links ...
            vocab[-1].linkWords(self.recent[-1])
            vocab[-1].linkWords(self.recent[-2])
            vocab[-1].linkWords(self.recent[-3])
            vocab[-1].linkWords(self.recent[-4])
            vocab[-1].linkWords(self.recent[-5])
            vocab[-1].linkWords(self.recent[-6])
            vocab[-1].linkWords(self.recent[-7])
            vocab[-1].linkWords(self.recent[-8])    

        #Randomly reduce some occurrence and links to keep balance
        vocab[random.randint(0, len(vocab)-1)].decOcc()
        #should sort also here... skip that
        for i in range(0,7):
            vocab[random.randint(0, len(vocab)-1)].decLinks

        self['vocabulary'] = vocab
 
    def callback_message(self, mess):
        if self.enabled:
            # sanitize word by word, add to vocabulary, add to recent, speak
            incoming_words = mess.body.split()
            for item in incoming_words:
                if self.sanitize(item):
                    self.vocUpdate(item)
                    del self.recent[0]
                    self.recent.append(item)
                    self.urge += self.activity
                    if self.urge > 255:
                        self.urge = 255
            if not self.muted:
                self.speak()
        
            