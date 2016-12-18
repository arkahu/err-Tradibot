# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 11:50:59 2016

Author: Arttu Huttunen, 2016
Oulu, Finland.
Version 0.83
"""

from errbot import BotPlugin, botcmd
import random, json
import tradibot_conf
       
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

    #links this word to another word                   
    def linkWords(self, word, amount=1):
        if word != self.word:
            #if word is in links dictionary increase link strength
            if  word in self.links: #self.links.get(word) != None:
                self.links[word] = self.links[word] + amount
                if self.links[word] > 255:
                    self.links[word] = 255
            #if not in links replace lowest strength link with word
            else:
                if len(self.links) > 15:  #at max 16 links
                    del self.links[min(self.links, key=self.links.get)]
                self.links[word] = 1

    #reduce random link strength
    def decLinks(self):
        key = random.choice(list(self.links.keys()))
        if self.links[key] > 0:  
            self.links[key] = self.links[key] - 1
    
    #gives randomly a link, weighted by the link strengths        
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
    
    #makes a list of the data for -save to file- purpose       
    def dataToList(self):
        output = [self.word, self.occurrence, self.links]
        return output


class Tradibot(BotPlugin):
    """Tragic discussion bot -plugin bor Errbot. Tragic refers to the development process.
    The bot takes all messages posted to a channel and makes a vocabulary of
    the words, then semi-randomly talks back."""
    #Tragic discussion bot

#Safer to make these non-persistent!   
#
#    def activate(self):
#        """Initializes bot variables""" 
#        #if the __init__/activate does not work, comment out and initialize manually.
#        self.vocabularyfile = 'vocabulary.txt'
#
#        self.activity = 1    #0-255
#        self.muted = True     
#        self.enabled = False 
#        self.recent = ['']*8 #set by using: self['recent'][0]
#        
#        self.chatroom = self.build_identifier('#general')
#        #self.chatroom = self.query_room("#general")     #*******SET #channel
#        self.urge = 0  # the urge to talk 0-255
#        self['vocabulary'] = [vocWord('init')]
#        super().activate()

   
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
            self.urge = 65535
            self.speak()
            return 'I have spoken.'
            
        elif args == 'save':
            """Saves the vocabulary to a file."""
            data = []
            for item in self['vocabulary']:
                data.append(item.dataToList())
            with open(tradibot_conf.vocabularyfile, 'w') as outfile:
                json.dump(data, outfile) 
            return 'Vocabulary saved'
        
        elif args.split()[0] =='activity':
            """Sets the value how often the bot speaks, max 65535. !tradibot activity 4"""
            self.activity = int(args.split()[1])
            if self.activity >65535:
                self.activity = 65535
            return 'Activity set to ' + str(self.activity)
            
        elif args.split()[0] =='silence':
            """Sets the value how fast bot becomes silent. !tradibot silence 40"""
            self.silence = int(args.split()[1])
            if self.silence >65535:
                self.silence = 65535
            elif self.silence == 0:
                self.silence = 1 #will not stop talking with 0
            return 'Silence set to ' + str(self.silence)            
            

        
        elif args == 'initialize':
            """Initializes bot variables.""" 
            #if the __init__/activate does not work, comment out and use this manually.
            self.vocabularyfile = tradibot_conf.vocabularyfile
    
            self.activity = 256    #0-65535
            self.silence = 2048
            self.muted = True     
            self.enabled = False
            self.recent = ['']*16 #set by using: self['recent'][0]
            
            self.chatroom = self.build_identifier(tradibot_conf.chatroom)
            #self.chatroom = self.query_room(tradibot_conf.chatroom)
            self.urge = 0  # the urge to talk 0-65535
            return 'Initialized'
            
        elif args == 'new_vocabulary':
            """Resets the vocabulary."""
            self['vocabulary'] = [vocWord('init')]
            return 'New vocabulary initialized'
            
        elif args == 'load_vocabulary':
            """Loads words from file to vocabulary."""
            with open(tradibot_conf.vocabularyfile, 'r') as file:
                data=json.load(file)
            vocab =  self['vocabulary']
            #add new words from file to vocabulary
            for word in data:
                for curvoc in vocab:
                    if word[0] == curvoc.word:
                        break
                else:
                    if len(vocab) >= 8191:
                        vocab.pop()
                        vocab.insert(8000,vocWord(word))
                        vocab[8000].occurrence = word[1]
                        vocab[8000].links = word[2]                        
                    else:
                        vocab.append(vocWord(word))
                        vocab[-1].occurrence = word[1]
                        vocab[-1].links = word[2]
                        
            #sort by occurrence
            pos = len(vocab) - 1
            while pos > 0:
                if vocab[pos].occurrence > vocab[pos-1].occurrence:
                    vocab[pos],vocab[pos-1] = vocab[pos-1], vocab[pos]
                pos = pos - 1 
                        
            self['vocabulary'] = vocab
            return 'Loaded vocabulary file'
        
        else:
            return '''Valid parameters are: initialize, status, mute, unmute,
            enable, disable, activity 250, silence 2000, save, new_vocabulary,
            load_vocabulary'''
            
   
    #Actual logic starts here    
   
    def speak(self, sentence = ''):
        #if wants to speak
        vocab = self.vocab
        topic = random.choice(self.recent)
        rnd = random.randint(0,65535)
        while self.urge > rnd:
            self.urge = self.urge - self.silence
            if self.urge < 0:
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

 
    def vocUpdate(self, word):
        vocab = self.vocab
        #vocabulary is vocab[vocWord(word1),vocWord(word2)]
        #if old word
        for item in vocab:
            if word == item.word:
                item.incOcc()                                   
                #link current to recent, i.e. word in voc gets a link to recent
                for rec in self.recent:
                    item.linkWords(rec)
                    #link recent to current, i.e. recent linked to word at hand
                    #find recent and link
                    for rcnt in vocab:
                        if rcnt.word == rec:
                            rcnt.linkWords(word)
                            break
                break
        #if new word, insert near end
        else:
            if len(vocab) >= 8192:
                point = 8000
                vocab.pop()
                vocab.insert(point,vocWord(word))
            else:
                vocab.append(vocWord(word))
                point = len(vocab) -1
            #links ...
            for rec in self.recent:
                vocab[point].linkWords(rec)
                for rcnt in vocab:
                    if rcnt.word == rec:
                        rcnt.linkWords(word)
                        break  

        #if vocabulary size is over something, keep balance
        if vocab[0].occurrence > 200:
            #Randomly reduce some occurrence and links to keep balance
            random.choice(vocab).decOcc()
            for i in range(0,32):
                random.choice(vocab).decLinks()

        self.vocab = vocab

 
    def callback_message(self, mess):
        if self.enabled:
            #skip commands completely and too long messages
            if not mess.body.startswith(tradibot_conf.ignore_commands):
                self.vocab = self['vocabulary']  #RAM copy of vocab
                if len(mess.body) <  1000:
                    # sanitize word by word, add to vocabulary, add to recent, speak
                    incoming_message = mess.body.lower()
                    incoming_words = incoming_message.split()
                    for item in incoming_words:
                        if len(item) < 32:
                            if not item.startswith(tradibot_conf.forbidden_words):
                                if item.endswith(tradibot_conf.remove_chars):
                                    item = item[:-1]
                                self.vocUpdate(item)
                                del self.recent[0]
                                self.recent.append(item)
                                self.urge += self.activity
                                if self.urge > 65535:
                                    self.urge = 65535

                    #sort by order of occurrence
                    vocab = self.vocab
                    pos = len(vocab) - 1                
                    while pos > 0:
                        if vocab[pos].occurrence > vocab[pos-1].occurrence:
                            vocab[pos],vocab[pos-1] = vocab[pos-1], vocab[pos]
                        pos = pos - 1
                    self.vocab = vocab                              

                    if not self.muted:
                        self.speak()
                        
                #too long message is skipped
                else:
                    if not self.muted:
                        self.speak('tl;dr ')
                self['vocabulary'] = self.vocab

