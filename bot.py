from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import robin_stocks as r
import os
from pprint import pprint
import json
from cacheout import Cache


cache = Cache()

#login = r.login('Tim.ward.0801@gmail.com', 'Jubjub0801!')

updater = Updater(token='1348466764:AAFSKyvcgaOK0kc2E1yXnGUSZH56k_knA8U', use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

OPEN_POSITIONS = 'open_positions'

MAIN, SECOND, POSITIONS, TYPING_CHOICE, TYPING_REPLY = range(5)
ONE, TWO, THREE, FOUR = range(4)

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Positions", callback_data='positions'),
         InlineKeyboardButton("2", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Start handler, Choose a route",
        reply_markup=reply_markup
    )
    return MAIN

def start_over(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("1", callback_data=str(ONE)),
         InlineKeyboardButton("2", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Start handler, Choose a route",
        reply_markup=reply_markup
    )
    return MAIN

with open("debug.txt", "w") as text_file:
  text_file.write("{} - {} - {}".format(response.url, response.meta.get('_id'), response.body == ''))

def get_open_positions():
  open_positions = cache.get(OPEN_POSITIONS)
  if open_positions == None:
    cache.set(OPEN_POSITIONS, r.get_open_stock_positions(), ttl=100)
    open_positions = cache.get(OPEN_POSITIONS)

  return open_positions

def get_open_positions_presentation():
  for position in get_open_positions():
    result = {}
    instrument = r.request_get(position['instrument'])
    quote = r.request_get(instrument['quote'])
    result['price'] = float(quote['last_trade_price'])
    result['open'] = float(position['average_buy_price'])
    result['symbol'] = quote['symbol']
    result['name'] = instrument['name']
    result['quantity'] = float(position['quantity'])
    result['profit'] = round((result['price'] - result['open']) * result['quantity'], 2)

    yield result

def show_symbol(update, context):
  query = update.callback_query
  query.answer()
  position = next((position for position in get_open_positions_presentation() if position['symbol'] == query.data), None)

  if position == None: return

  query.edit_message_text(text="Name: {}\nOpen: {}\nCurrent: {}\nProfit: {}".format(
    position['name'], position['open'], position['price'], position['profit']))

  return MAIN

def god(update, context):
  user_data = context.user_data
  text = update.message.text
  category = user_data['choice']
  user_data[category] = text
  del user_data['choice']

  update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                            "{} You can tell me more, or change your opinion"
                            " on something.".format(facts_to_str(user_data)),
                            reply_markup=markup)

  return CHOOSING


def confirm_stop_loss(update, context):
  text = update.message.text
  context.user_data['choice'] = text
  update.message.reply_text(
      'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

  return MAIN

def set_stop_loss(update, context):
  query = update.callback_query
  keyboard = [[InlineKeyboardButton("Cancel", callback_data=str(THREE))]]
  reply_markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(
      text="Set stop loss for position",
      reply_markup=reply_markup)

  return TYPING_CHOICE

def position(update, context):
  query = update.callback_query
  query.answer()
  keyboard = [[InlineKeyboardButton("Set SL", callback_data='set_stop_loss')],
       [InlineKeyboardButton("Set TP", callback_data='set_take_profit')],
       [InlineKeyboardButton("CLOSE", callback_data='close')],
       [InlineKeyboardButton("BACK", callback_data='back')]]

  reply_markup = InlineKeyboardMarkup(keyboard)
  position = next((position for position in get_open_positions_presentation() if position['symbol'] == query.data), None)
  query.edit_message_text(
      text="Name: {}\nOpen: {}\nCurrent: {}\nProfit: {}".
      format(position['name'], position['open'], position['price'], position['profit']),
      reply_markup=reply_markup)

  return POSITIONS

def positions(update, context):
  open_positions = get_open_positions_presentation()
  query = update.callback_query
  query.answer()
  query.edit_message_text(
      text="Open positions",
      reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("{}: {}".format(x['symbol'], x['profit']),
          callback_data=x['symbol'])] for x in open_positions]))

  dispatcher.add_handler(CallbackQueryHandler(position,
    pattern="({})".format("|".join([x['symbol'] for x in open_positions]))))


  return POSITIONS



def main():

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN: [CallbackQueryHandler(positions, pattern='positions')],
            POSITIONS: [CallbackQueryHandler(set_stop_loss, pattern='set_stop_loss')],
            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               confirm_stop_loss)],
            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               god)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

main()