import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from pprint import pprint

SEARCH_SIGNAL = "SEARCH_SIGNAL"
SEARCH_SIGNAL_RESULT = "SEARCH_SIGNAL_RESULT"

def view_stocks(update, context):
  buttons = [[InlineKeyboardButton("Search signal", callback_data=SEARCH_SIGNAL)]]

  buttons.append([InlineKeyboardButton("Back", callback_data="GOD")])
  keyboard = InlineKeyboardMarkup(buttons)
  update.callback_query.edit_message_text("What would you like to do", reply_markup=keyboard)
  return 2

def search_signal(update, context):
  update.callback_query.answer()
  update.callback_query.edit_message_text(text="Search for a signal")
  context.user_data['signal'] = None
  return 2

def search_signal_result(update, context):
  print(2)
  pprint(context.user_data)
  # ROBINHOOD LOGIC TO CHANGE STOP LOSS
  view_stocks(update, context)

def search(update, context):
  print(1)
  context.user_data['signal'] = update.message.text
  print(context.user_data)
  search_signal_result(update, context)


def get_callbacks(menu):
  return [CallbackQueryHandler(search_signal, pattern='^' + SEARCH_SIGNAL + '?'),
          CallbackQueryHandler(search_signal_result, pattern='^' + SEARCH_SIGNAL_RESULT + '?'),
          MessageHandler(Filters.text & ~Filters.command, search),
          CallbackQueryHandler(menu, pattern='^' + "GOD" + '?')]