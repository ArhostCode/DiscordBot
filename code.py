from langdetect import detect
from translate import Translator
import apiai,json,configparser, requests, discord # Import necessary libraries
settings = configparser.ConfigParser() 
config = configparser.ConfigParser()        # Creating configs readers

settings.read("work_settings.ini")
config.read("config.ini")                   # Read configs from files

APIKEY = config["DialogFlow"]["api_key"]
TOKEN = config["Discord"]["token"]          # Set Discord Token an DialogFlow apikey from files

translator = Translator(to_lang="ru")       # Creating Translator




#Bot class
class BotDiscord(discord.Client):
    
    #Discord function
    async def on_typing(self,channel,user,when):
        pass

    async def on_ready(self):
        print("ready")
        
    
    async def on_message(self,message):

        # Check: author is bot?
         if message.author.bot:
            return

        # Get content and channel from message
        channel = message.channel
        ms = message.content


        if message.content.__len__()>250:
            await channel.send("Замолчи, пожалуйста, "+message.author.name+ ", хватит спамить!")
       
        if set("йцукенгшщзхъфывапролджэячсмитьбю").isdisjoint(ms.lower()) == True:  #Fast ru checker
            ms = translator.translate(message.content)
        print(settings["Chat"]["is_translate"])
        if settings["Chat"]["is_translate"] == "True":
            await channel.send(ms)
        
        if ms.lower().rfind("!дата") != -1:
            response = requests.get("http://worldtimeapi.org/api/timezone/Europe/Moscow")
            print(response.json()["datetime"])
            await channel.send(str(response.json()["datetime"])[0:10])
        elif ms.lower().rfind("!время") != -1:
            response = requests.get("http://worldtimeapi.org/api/timezone/Europe/Moscow")
            print(str(response.json()["datetime"])[11:19])
            await channel.send(str(response.json()["datetime"])[11:19])
        elif ms.lower().rfind("!помощь") != -1:
            await channel.send("""
            Список моих комманд:
              !время ----------- узнать время
              !дата ------------ узнать дату
              !помощь ---------- для получения помощи
              !перевод --------- для включения и отключения автопереводчика
              !чат ------------- для включения и отключения автоответчика
            """)
        elif ms.lower().rfind("!перевод") != -1:
            if settings["Chat"]["is_translate"] == "True":
                settings["Chat"]["is_translate"] = "False"
                await channel.send("Перевод отключен")
            else:
                settings["Chat"]["is_translate"] = "True"
                await channel.send("Перевод включен")
        elif ms.lower().rfind("!чат") != -1:
            if settings["Chat"]["is_chat"] == "True":
                settings["Chat"]["is_chat"] = "False"
                await channel.send("Ответчик отключен")
            else:
                settings["Chat"]["is_chat"] = "True"
                await channel.send("Ответчик включен")
        else:
            if settings["Chat"]["is_chat"] == "True":
                request = apiai.ApiAI(APIKEY).text_request()
                request.lang = 'ru' 
                print(ms)
                request.query = ms
                responseJson = json.loads(request.getresponse().read().decode('utf-8'))
                response = responseJson['result']['fulfillment']['speech']
                if response.__len__() > 0:
                    await channel.send(response)
                else:
                    channel.send("Извини, я тебя не понимаю введи !помощь для ознакомления с моими возможностями")
           
   

# Run bot with token TOKEN
if __name__ == "__main__":
    bot = BotDiscord()
    bot.run(TOKEN)
