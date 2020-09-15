import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

import positions
import watcher
from pprint import pprint

POSITIONS, STOCKS = [1, 2]
MENU_TEXT = "What would you like to do?"

def main_menu_keyboard():
  buttons = [[InlineKeyboardButton(text="View open positions", callback_data=str(POSITIONS))],
             [InlineKeyboardButton(text="View stocks", callback_data=str(STOCKS))]]
  return InlineKeyboardMarkup(buttons)

def menu(update, context):
  update.message.reply_text(MENU_TEXT, reply_markup=main_menu_keyboard())
  return 1

def main_menu(update, context):
  update.callback_query.edit_message_text(MENU_TEXT, reply_markup=main_menu_keyboard())
  return 1

def main():
  updater = Updater("1348466764:AAFSKyvcgaOK0kc2E1yXnGUSZH56k_knA8U", use_context=True)
  dp = updater.dispatcher

  conv_handler = ConversationHandler(
      entry_points=[CommandHandler('start', menu)],
      states={
        1: [CallbackQueryHandler(positions.view_positions, pattern='^' + str(POSITIONS) + '$'),
            CallbackQueryHandler(watcher.view_stocks, pattern='^' + str(STOCKS) + '$')],
        2: watcher.get_callbacks(main_menu),
        3: positions.get_callbacks(main_menu)
      },
      fallbacks=[],
  )
  dp.add_handler(conv_handler)

  updater.start_polling()

  updater.idle()


if __name__ == '__main__':
    main()