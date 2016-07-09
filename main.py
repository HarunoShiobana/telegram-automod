import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '206126857:AAH-E77120sBUc-929dHM-dvkfRdPu_RJCA'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

modmsg = ""

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'false',
                    'reply_to_message_id': str(message_id),
                    'parse_mode' : 'MARKDOWN',
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None
        
            logging.info('send response:')
            logging.info(resp)
            
        def replynomd(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'false',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                replynomd('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                replynomd('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            elif text == '/modmsg enable':
                global modmsg
                modmsg = "\n\n_I am a bot, and this action was performed automatically. Please contact the moderators of this subreddit if you have any questions or concerns._"
                reply("Mod message enabled")
            elif text == '/modmsg disable':
                global modmsg
                modmsg = ""
                reply("Mod message disabled")

        if getEnabled(chat_id):
            
            # Edit logic after this
            
            if "ayy" in text.lower().replace(" ", "").replace("\n", "") and not "ayylmao" in text.lower().replace(" ", "").replace("\n", ""):
                 reply('lmao' + modmsg)
            if "awoo" in text.lower().replace(" ", "").replace("\n", "") and not "don'tawoo" in text.lower().replace(" ", "").replace("\n", ""):
                reply(img=urllib2.urlopen('http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/5ee99c55-7448-46ec-b93b-b413265f5c28/md/1537338-1453704069550-image.jpg').read() + modmsg)
            if "xd" in text.lower():
                reply(img=urllib2.urlopen('https://pbs.twimg.com/media/ClE02SzVYAIq4gN.jpg').read() + modmsg)
            if "uwu" in text.lower().replace(" ", "").replace("\n", ""):
                reply(img=urllib2.urlopen('https://furnation.com/public/album_photo/0b/73/06/6669e_ac4e.jpg').read() + modmsg)
            if "keksimus" in text.lower() and not "keksimus maximus" in text.lower():
                reply("maximus" + modmsg)
            if "tbh fam" in text.lower():
                reply(u'\U0001F602\U0001F44C' + modmsg)
            if "bad automod" in text.lower() or "fuck you automod" in text.lower() or "fuck u automod" in text.lower():
                reply("u fukin wot m8, i'll rek you on wii party" + modmsg)
            if "morto" in text.lower():
                reply("rip" + modmsg)
            if text.lower() == "rip":
                reply(":c" + modmsg)
            if "nooo" in text.lower():
                reply(img=urllib2.urlopen('http://i.imgur.com/ASiQpMU.jpg').read() + modmsg)
            if "fixed" in text.lower().replace(" ", "").replace("\n", "") or "fixato" in text.lower().replace(" ", "").replace("\n", "") or "fix'd" in text.lower().replace(" ", "").replace("\n", ""):
                replynomd("https://youtu.be/_1d_yAFLn1c?t=2m40s" + modmsg)
            if "afamok" in text.lower():
                reply("Mammt" + modmsg)
            if "succ" in text.lower().replace(" ", "").replace("\n", "") or "pusi" in text.lower().replace(" ", "").replace("\n", "") or "pussy" in text.lower().replace(" ", "").replace("\n", ""):
                replynomd(img=urllib2.urlopen('http://static.deathandtaxesmag.com/uploads/2014/05/pussy.png').read() + modmsg)
            if "NANO" in text:
                replynomd('http://ci.memecdn.com/477/6742477.gif' + modmsg)
            if "aya" in text.lower().replace(" ", "").replace("\n", "") or "famale" in text.lower().replace(" ", "").replace("\n", ""):
                replynomd('http://i3.asn.im/Nichijou-_tcu1.gif' + modmsg)
            if "bestemmio" in text.lower():
                replynomd('http://i840.photobucket.com/albums/zz324/MikeyzDragon/Hakase/hakasepopcat.gif' + modmsg)
            if "dormo" in text.lower() or "nott" in text.lower():
                replynomd("Nott" + modmsg)
            if text.lower() == "il cazzo" or text.lower() == "le palle":
                reply("di zia Vittoria" + modmsg)
            if "r/" in text.lower() and not " r/" in text.lower():
                reply("http://reddit.com/" + text + modmsg)
            if text.lower() == "oh cazzo":
                reply("Un debian" + modmsg)
            
# Don't go any further

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
