# [ Music Kim Telegram Chatbot ]
# Made by : DuHyeok-Chang ( Tomray Pulmu )
# Github : https://www.github.com/ChangPulMu
# Release Version : 1.0
# More Information & Request For this Chatbot : 16906@naver.com

import telegram             # Telegram API
import logging              # Error Log 정보를 남기기 위한 Logging API
import pandas as pd         # CSV 파일을 읽고 다루기 위한 Pandas API
import unittest             # 공백 문자열을 '+" 문자로 바꾸기 위해 사용된 Unittest API

from khaiii import KhaiiiApi                                                                        # 형태소 분석기 Khaiii API
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler     # 갱신된 정보를 다루는 Updater 객체, 정해진 Command를 다루는 CommandHandler 객체, 메세지를 다루는 MessageHandler, Text를 필터링해주는 Filters 객체, 어떤 행위에 대한 사용자의 대답을 다루는 CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup                                     # Telegram Button Interface를 구현가능한 InlineKeyboardButton, InlineKeyboardMarkup 객체

my_token = '846490622:AAHzkPwpgOlnpJJKCn_5oWn3hcV4EIXl3-U'      # Telegram Music Kim Bot의 token 값
bot = telegram.Bot(token = my_token)                            # 해당 token으로 Bot 생성

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)    # 기본 Logging 형식을 설정

api = KhaiiiApi()                       # 형태소 분석기 KhaiiiApi()

sentiment_data = pd.read_csv("KoreanSample.csv", encoding='CP949')      # 감성어 기분석 사전인 KoreanSample.csv 파일을 CP949 인코딩 형식으로 읽어옴
music_data = pd.read_csv("SpotifyFeatures.csv")                         # Spotify Music Big Data인 SpotifyFeatures.csv 파일을 읽어옴
final_mdf = pd.read_csv("Ranged_SpotifyFeatures.csv")                   # Clustering된 Spotify Music Big Data인 Ranged_SpotifyFeatures.csv 파일을 읽어옴


def start(bot, update):     # Bot에 /start Command 입력 혹은 Bot에 처음 시작하기를 클릭할 때
    # Button Interface를 형성하기 위해 각 Button에 Callback Data를 연결시킨 후 Markup 해줌
    show_list = []
    show_list.append(InlineKeyboardButton("How to handle", callback_data="How to handle"))
    show_list.append(InlineKeyboardButton("Logic of this bot", callback_data="Logic of this bot"))
    show_list.append(InlineKeyboardButton("Thanks to", callback_data="Thanks to"))
    show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list) - 1))

    # 해당 Button Interface와 Default Start Response를 Bot 화면에 출력
    temp_start = "안녕하세요! Music Kim 챗봇에 오신것을 환영합니다!\n당신의 기분을 표현해서 해당 기분에 어울리는 음원을 추천받으세요~\nex) 행복 : Music Kim 챗봇이 행복한 당신의 기분과 어울리는 음원 추천!\n"
    update.message.reply_text(temp_start, reply_markup=show_markup)


def help(bot, update):      # Bot에 /help Command 입력 혹은 Bot Button Interface의 How to handle Button을 클릭했을 때
    # Music Kim Bot의 사용 설명을 Bot 화면에 출력
    temp_help = "Music Kim 챗봇을 사용하는 것은 어렵지 않습니다~\nStep1> 현재 나의 기분이 어떤지 생각한다\nStep2> 당신의 기분과 어울리는 단어 혹은 문장을 생각해낸다\nStep3> 해당 단어 혹은 문장을 Music Kim 챗봇에게 전달한다\nStep4> 해당 기분에 어울리는 음원을 추천받는다!\n\nStart 메뉴로 돌아가기 : /start\n"
    bot.sendMessage(update.message.chat_id, text=temp_help)

def logic(bot, update):     # Bot에 /logic Command 입력 혹은 Bot Button Interface의 Logic of this bot을 클릭했을 때
    # Music Kim Bot의 전체적인 흐름도와 논리를 Bot 화면에 출력
    temp_logic = "1> 챗봇은 사용자로부터 문장 혹은 단어를 입력받는다\n2> 받은 문장 혹은 단어를 Khaiii API 형태소 분석기를 통해 형태소 단위로 나눈다\n3> 문장이라면 문장의 핵심이라 할 수 있는 품사를 중심(단어는 기본적으로 품사)으로 Clustered된 감성어 기분석 사전을 비교하여 해당 단어의 특성을 도출한다\n4> 도출된 특성과 유사한 Clustered된 음원 데이터를 사용자에게 알려준다\n\nStart 메뉴로 돌아가기 : /start\n"
    bot.sendMessage(update.message.chat_id, text=temp_logic)

def thanks(bot, update):    # Bot에 /thanks Command 입력 혹은 Bot Button Interface의 Thanks to를 클릭했을 때
    # Music Kim Bot을 만드는데 도움을 주신 분들과 감사 말씀을 Bot 화면에 출력
    temp_thanks = "[ Thanks to ]\n음악이란 열정으로 뭉쳐 열심히 해준 우리 Music Kim 팀원들과 개발 방향성을 올바르게 잡아주신 김영종 교수님께 감사드립니다.\n\n[ License ]\nLicensed under the Apache License, Version 2.0 (the \"License\"), you may not use this file except in compliance with the License. You may obtain a copy of the License at\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nCopyright (c) 2008-2012, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData Development Team All rights reserved.\n\nStart 메뉴로 돌아가기 : /start\n"
    bot.sendMessage(update.message.chat_id, text=temp_thanks)

def change(bot, update):                # Bot에 Command외의 Message(감성어가 포함된 단어 혹은 문장)가 입력되었을 때
    tmp = update.message.text           # 최근 갱신된(사용자가 Bot에 Message 입력) Message를 받아옴

    for word in api.analyze(tmp):       # Message를 형태소 분석을 진행해서 띄어쓰기 단위로 word 변수에 저장되어 반복문을 돔

        i = 0

        while i < len(word.morphs):     # 형태소 단위로 반복문을 돔
            result = ""

            t = word.morphs[i].lex + '/' + word.morphs[i].tag                       # 감성어 기분석 사전의 형식대로 Parsing해줌
            tempdata = sentiment_data.loc[sentiment_data["ngram"].str[:] == t]      # 감성어 기분석 사전의 단어와 비교를 진행해 같은 단어를 임시 변수에 저장

            result = tempdata["SP/max.value"] + tempdata["Intensity/max.value"]     # 도출된 단어의 특성을 구별하기 쉽게 Parsing해줌

            final_result = result.loc[result.index.values]                          # Parsing된 특성만 임시 변수에 저장해줌(Clustering된 음원 데이터와의 비교를 위해)

            if not tempdata.empty and word.morphs[i].tag == "NNG":                  # 해당 형태소가 감성어 기분석 사전에 존재하며 품사 형식일 때 아래 문장들을 실행
                print("\n")
                print(update.message.chat_id)
                print("Message : " + word.morphs[i].lex)
                print("Attribute : " + final_result)
                print("\n")                                                         # 해당 형태소와 특성을 Server에서 확인하기 위한 출력

                # 해당 형태소의 특성과 유사한 특징을 가지는 Clustering된 음원 데이터들을 임시변수에 저장
                if final_result.item() == "POSHigh":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 1]        
                elif final_result.item() == "POSMedium":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 6]        
                elif final_result.item() == "POSLow":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 3]        
                elif final_result.item() == "NEUTHigh":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 4]        
                elif final_result.item() == "NEUTLow":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 2]        
                elif final_result.item() == "NEGHigh":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 7]        
                elif final_result.item() == "NEGMedium":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 0]        
                elif final_result.item() == "NEGLow":
                    music = final_mdf.loc[final_mdf["cluster_id"] == 5]  
                else:   # 유사한 특징을 가지는 음원 데이터가 없다면 다음 형태소로 넘어감
                    i += 1
                    bot.sendMessage(update.message.chat_id, text="조금 더 명확하게 말씀해주실래요?ㅜㅜ")
                    continue
            else:       # 해당 형태소가 감성어 기분석 사전에 존재하지 않으며 품사 형식 또한 아닐 때 다음 형태소로 넘어감
                i += 1
                bot.sendMessage(update.message.chat_id, text="조금 더 명확하게 말씀해주실래요?ㅜㅜ")
                continue

            # 유사한 특징을 가지는 음원 데이터들 중 어느정도 유명한 음원 데이터 하나를 무작위로 선택하여 임시 변수에 저장
            while(1):
                fin = music_data.loc[music_data.index.values == music.sample().index.values]
                if(fin["popularity"].real > 70):
                    break

            print(fin)  # 선택된 음원 데이터를 Server에서 확인하기 위한 출력
            
            # Youtube URL을 형성하기 위해 선택된 음원 데이터에서 URL에 활용할 특성의 공백을 '+'문자로 대체
            parse1 = fin["artist_name"].to_string(index=False).strip().replace(" ", "+")
            parse2 = fin["track_name"].to_string(index=False).strip().replace(" ", "+")

            # 사용자에게 선택된 음원 데이터의 정보(아티스트, 음원, 장르, 키, 박자, Youtube URL)를 Bot 화면에 출력
            gift = "아티스트 : " + fin["artist_name"] + "\n" + "음원 : "+ fin["track_name"] + "\n" +  "장르 : " + fin["genre"] + "\n" + "키 : " + fin["mode"] + " " + fin["key"] + "\n" + "박자 : " + fin["time_signature"] + "\n" + "Youtube URL : https://www.youtube.com/results?search_query=" + parse1 + "+" + parse2 + "\n\nStart 메뉴로 돌아가기 : /start"; 
            hap = "지금 당신의 기분에 어울리는 이런 음악은 어떠세요?" + "\n" + gift.loc[gift.index.values]

            i += 1

            update.message.reply_text(hap.item())


def error(bot, update):             # Error가 발생하였을 때 해당 Error의 정보를 출력하고 예외 처리를 함
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):      # Button Interface를 구현하기 위한 Bulid Up 메소드
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

    # Header, Footer Button을 상의하게 정의해줌
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)

    return menu

def callback_get(bot, update):      # Button Interface의 Button이 클릭되었을 때 각각의 Button에 대한 Callback 메소드를 정의
    # 'How to handle' Button이 클릭되었을 때 help command의 메소드와 같은 결과를 Bot 화면에 출력
    if update.callback_query.data == "How to handle":
        temp_data = "Music Kim 챗봇을 사용하는 것은 어렵지 않습니다~\nStep1> 현재 나의 기분이 어떤지 생각한다\nStep2> 당신의 기분과 어울리는 단어 혹은 문장을 생각해낸다\nStep3> 해당 단어 혹은 문장을 Music Kim 챗봇에게 전달한다\nStep4> 해당 기분에 어울리는 음원을 추천받는다!\n\n해당 정보는 /help 를 통해서도 확인가능합니다\nStart 메뉴로 돌아가기 : /start\n"
        bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, text=temp_data)
    # 'Logic of this bot' Button이 클릭되었을 때 logic command의 메소드와 같은 결과를 Bot 화면에 출력
    elif update.callback_query.data == "Logic of this bot":
        temp_data = "1> 챗봇은 사용자로부터 문장 혹은 단어를 입력받는다\n2> 받은 문장 혹은 단어를 Khaiii API 형태소 분석기를 통해 형태소 단위로 나눈다\n3> 문장이라면 문장의 핵심이라 할 수 있는 품사를 중심(단어는 기본적으로 품사)으로 Clustered된 감성어 기분석 사전을 비교하여 해당 단어의 특성을 도출한다\n4> 도출된 특성과 유사한 Clustered된 음원 데이터를 사용자에게 알려준다\n\n해당 정보는 /logic 을 통해서도 확인가능합니다\nStart 메뉴로 돌아가기 : /start\n"
        bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, text=temp_data)
    # 'Thanks to' Button이 클릭되었을 때 thanks command의 메소드와 같은 결과를 Bot 화면에 출력
    elif update.callback_query.data == "Thanks to":
        temp_data = "[ Thanks to ]\n음악이란 열정으로 뭉쳐 열심히 해준 우리 Music Kim 팀원들과 개발 방향성을 올바르게 잡아주신 김영종 교수님께 감사드립니다.\n\n[ License ]\nLicensed under the Apache License, Version 2.0 (the \"License\"), you may not use this file except in compliance with the License. You may obtain a copy of the License at\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nCopyright (c) 2008-2012, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData Development Team All rights reserved.\n\nStart 메뉴로 돌아가기 : /start\n"
        bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, text=temp_data)


def main():
    # Music Kim Bot의 Updater 객체를 정의
    updater = Updater(my_token)

    dp = updater.dispatcher

    # Command와 Message에 대한 Handler를 정의
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("logic", logic))
    dp.add_handler(CommandHandler("thanks", thanks))
    dp.add_handler(MessageHandler([Filters.text], change))

    # Button Interface의 Callback Handler를 정의
    dp.add_handler(CallbackQueryHandler(callback_get))
    
    # Error Handler를 정의
    dp.add_error_handler(error)
    
    # 갱신되는 사항을 마치 Loop을 돌리는 것처럼 받아옴
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
