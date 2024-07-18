import json
from dataclasses import dataclass, asdict, is_dataclass
from typing import List
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
import os
from dotenv import load_dotenv
import random

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