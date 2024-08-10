import json
from dataclasses import dataclass, asdict, is_dataclass
from typing import List
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
import os
from dotenv import load_dotenv
import random

load_dotenv()

api = os.getenv('TELEGRAM_BOT_TOKEN')
print(api)
bot = telebot.TeleBot(api)

ADMINS = ['strongnoy', 'HolyRam', 'gsora_1', 'azarovrom']
query_route = 'https://89.108.77.99:5001/api/'

class QuestionData:
    def __init__(self):
        self.title = None
        self.correct_answer = None
        self.wrong_answers = []


@dataclass
class Answer:
    id: int
    text: str
    isRight: bool


@dataclass
class Question:
    difficulty: 0
    text: str
    answers: List[Answer]

@dataclass
class Test:
    questions: List[Question]
    name: str


question_data = {}


def is_admin(user_id):
    return user_id in ADMINS


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if is_admin(message.from_user.username):
        button_create_question = InlineKeyboardMarkup()
        button_create_question.add(InlineKeyboardButton('Создать новый вопрос', callback_data='create_question'))
        bot.reply_to(message, 'Привет, ты админ, нажми на кнопку для добавления вопроса', reply_markup=button_create_question)
        button_create_test = InlineKeyboardMarkup()
        button_create_test.add(InlineKeyboardButton('Создать новый тест', callback_data='create_test'))
        bot.reply_to(message, 'Нажми на кнопку для создания', reply_markup=button_create_test)
    else:
        bot.reply_to(message, "прив, я эхо бот")

@bot.callback_query_handler(func=lambda call: call.data == 'create_test')
def callback_create_test(call):
    if not is_admin(call.from_user.username):
        bot.answer_callback_query(call.id, "У вас нет прав для выполнения этой команды.")
        return
    else:
        bot.send_message(call.message.chat.id, 'Напиши заголовок теста', reply_markup=ForceReply())
        bot.register_next_step_handler(call.message, get_test_title)


def get_test_title(message):
        test = Test(name=message.text, questions=[])
        bot.send_message(message.chat.id, 'Введи количество вопросов')
        bot.register_next_step_handler(message, create_questions, test=test)

def create_questions(message, test):
    amount_of_questions = message.text
    while amount_of_questions > 0:
        create_question(message)






@bot.callback_query_handler(func=lambda call: call.data == "create_question")
def callback_create_question(call):
    if not is_admin(call.from_user.username):
        bot.answer_callback_query(call.id, "У вас нет прав для выполнения этой команды.")
        return
    else:
        create_question(call.message)

def create_question(message):
    bot.send_message(message.chat.id, 'Напиши заголовок вопроса', reply_markup=ForceReply())
    bot.register_next_step_handler(message, get_question_title)

def get_question_title(message):
    title = message.text
    user_id = message.from_user.id
    question_data[user_id] = QuestionData()
    question_data[user_id].title = title

    bot.send_message(message.chat.id, "Напишите правильный ответ на вопрос", reply_markup=ForceReply())
    bot.register_next_step_handler(message, get_correct_answer)


def get_correct_answer(message):
    correct_answer = message.text
    user_id = message.from_user.id
    question_data[user_id].correct_answer = correct_answer

    bot.send_message(message.chat.id, "Напишите три неправильных ответа через ;", reply_markup=ForceReply())
    bot.register_next_step_handler(message, get_wrong_answers)


'''Метод обёртка для получения неправильных ответов'''
def get_wrong_answer_wrapper(message):
    wrong_answers_text = message.text
    wrong_answers = [answer.strip() for answer in wrong_answers_text.split(';')]
    if len(wrong_answers) != 3:
        bot.reply_to(message, "Напишите ровно три ответа")
        bot.register_next_step_handler(message, get_wrong_answer_wrapper)

    user_id = message.from_user.id
    question_data[user_id].wrong_answers = wrong_answers
    answers = []
    answers.append(Answer(id=0, text=question_data[user_id].correct_answer, isRight=True))
    for i in range(3):
        ans = Answer(id=0, text=question_data[user_id].wrong_answers[i], isRight=False)
        answers.append(ans)
    random.shuffle(answers)
    question = Question(text=question_data[user_id].title, difficulty=0, answers=answers)

    question_dict = dataclass_to_dict(question)
    question_json = json.dumps(question_dict, ensure_ascii=False, indent=4)
    return question_json

def get_wrong_answers(message):
    send_post_request(get_wrong_answer_wrapper(message), f'{query_route}Question/create-question' )

def send_post_request(json, route):
    response = requests.post(route, data=json,
                             headers={'Content-Type': 'application/json'}, verify=False)
def dataclass_to_dict(obj):
    if isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    elif is_dataclass(obj):
        return asdict(obj)
    else:
        return obj
@bot.message_handler(commands=['getquestion'])
def get_question(message):
    try:
        question_id = message.text.split()[0]
    except IndexError:
        bot.reply_to(message, "Укажите id вопроса")
        return
    try:
        response = requests.get('https://localhost:5001/')
        response.raise_for_status()
        data = response.json()
        question = data.get('question', 'нет вопроса')
        answer = data.get('answers', 'net')
        res = ''
        bot.reply_to(message, res)
    except requests.exceptions as e:
        bot.reply_to(message, f"Ошибка {e}")



@bot.message_handler(commands=['getRandomQuestion'])

def get_random_question(message):
    '''Запрос получения случайного вопроса к АПИ'''
    try:
        response = requests.get(f'{query_route}Question/get-question-random', verify=False)
        response.raise_for_status()
        string = response.json()
        string = json.dumps(string)
        data = json.loads(string)
        temp = [Answer(**answer) for answer in data['answers']]
        question = Question(text=data['text'], difficulty=0, answers=temp)
        answers = []
        correct_id = int()
        for i in range(4):
            answers.append(temp[i].text)
            if temp[i].isRight:
                correct_id = i
        bot.send_poll(
            chat_id=message.chat.id,
            question=question.text,
            options=answers,
            is_anonymous=True,
            correct_option_id=correct_id,
            type='quiz'
        )
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Ошибка {e}")


bot.polling(none_stop=True, interval=30)
# @bot.message_handler(content_types=['text'])
# def echo(message):
#     bot.reply_to(message, message.text)
#
# @bot.message_handler(content_types=['audio', ' document', 'photo', 'video', 'sticker', 'voice'])
# def ignore(message):
#     bot.reply_to(message, 'только текст' )
