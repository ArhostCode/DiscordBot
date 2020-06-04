from googletrans import Translator
import apiai,json,configparser, requests, discord # Import necessary libraries

config = configparser.ConfigParser()        # Creating configs readers

config.read("config.ini")                   # Read configs from files

APIKEY = config["DialogFlow"]["api_key"]
TOKEN = config["Discord"]["token"]          # Set Discord Token an DialogFlow apikey from files


#Discord Bot class
class BotDiscord(discord.Client):

    isTranslate = False
    isChatEnable = True

    def __init__(self):
        translator = Translator()         # Creating Translator

    def getDialogFlowAnswer(self,q:str):
        request = apiai.ApiAI(APIKEY).text_request()
        request.lang = 'ru' 
        request.query = q
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech']
        if response.__len__() > 0:
            return response
        else:
            return "Извини, я тебя не понимаю введи \"!помощь\" для ознакомления с моими возможностями"
           

    def getDate(self):
        response = requests.get("http://worldtimeapi.org/api/timezone/Europe/Moscow")
        print(response.json()["datetime"])
        return str(response.json()["datetime"])[0:10]
    def getTime(self):
        response = requests.get("http://worldtimeapi.org/api/timezone/Europe/Moscow")
        return str(response.json()["datetime"])[11:19]

    def activateTranslate(self):
        self.isTranslate  = True if not self.isTranslate else self.isTranslate
        return "Состояние переводчика изменено"
    def activateChat(self):
        self.isChatEnable  = True if not self.isChatEnable else self.isChatEnable
        return "Состояние ответчика изменено"
    def helper(self):
        return """
            Список моих комманд:
              !время ----------- узнать время
              !дата ------------ узнать дату
              !помощь ---------- для получения помощи
              !перевод --------- для включения и отключения автопереводчика
              !чат ------------- для включения и отключения автоответчика
            """
    command_list = {"!помощь":helper,"!дата":getDate,"!время":getTime,"!чат":activateChat,"!перевод":activateTranslate}

    def response(self,q:str):
        resp = ""
        q = self.translate(q)
        
        if q.split(" ")[0].lower() in self.command_list:            #Check command in message
            resp += self.command_list.get(q.split(" ")[0])(self)
            q = str(q.split(" ")[1:])

        if self.isTranslate:
            resp += "\n"+ q                                         #Send translated message if on translator function
        
        if q.__len__()>5:
            if self.isChatEnable:
                resp+=self.getDialogFlowAnswer(q)
        return resp

   
    def translate(self,q:str):
        if set("йцукенгшщзхъфывапролджэячсмитьбю").isdisjoint(q.lower()) == True:  #Fast lang checker
            return translator.translate([q], dest='ru')
        return q



    #Discord function
    async def on_typing(self,channel,user,when):        #Starts when any user typing
        pass
 
    async def on_ready(self):                           #Starts when bot connected to Discord
        print("Ready")
        
    
    async def on_message(self,message):                 #Starts when any user send message to chat

        
        # Check: author is bot?
        if message.author.bot:
            return

        # Get content and channel from message
        channel = message.channel
        ms = message.content
        
        #Check length message
        if message.content.__len__()>250:
            await channel.send("Замолчи, пожалуйста, "+message.author.name+ ", хватит спамить!")
        await channel.send(self.response(ms))

   

# Run bot with token TOKEN
if __name__ == "__main__":
    bot = BotDiscord()
    bot.run(TOKEN)
