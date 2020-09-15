import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from pprint import pprint
from cacheout import Cache
import robin_stocks as r

OPEN_POSITIONS = "Open positions"
CONFIRM = "Confirm"
CANCEL = "Cancel"
CLOSE = "Close"
BACK = "Back"
VIEW_POSITION = "VIEW_POSITION: {}"
SET_STOP_LOSS = "SET_STOP_LOSS"
SET_TAKE_PROFIT = "SET_TAKE_PROFIT"
CONFIRM_TAKE_PROFIT = "CONFIRM_TAKE_PROFIT"
CONFIRM_STOP_LOSS = "CONFIRM_STOP_LOSS"
CANCEL_STOP_LOSS = "CANCEL_STOP_LOSS"
CLOSE_POSITION = "CLOSE_POSITION"
CONFIRM_CLOSE_POSITION = "CONFIRM_CLOSE_POSITION"
BACK_BUTTON = "BACK: {}"

cache = Cache()
login = r.login('Tim.ward.0801@gmail.com', 'Jubjub0801!')

def get_positions():
  open_positions = cache.get(OPEN_POSITIONS)
  if open_positions == None:
    cache.set(OPEN_POSITIONS, r.get_open_stock_positions(), ttl=100)
    open_positions = cache.get(OPEN_POSITIONS)

  return open_positions

def get_open_positions_presentation():
  for position in get_positions():
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

def get_positions_2():
  return [{'position': 1, 'signal': 'EUR/USD','price': 1.31,'tp': 1.35,'sl': 1.30,'units': 1000},
  {'position': 2, 'signal': 'EUR/CAD','price': 1.24,'tp': 1.35,'sl': 1.11,'units': 500}]

def view_positions(update, context):
  buttons = []
  for position in get_open_positions_presentation():
    signal = position['name']
    symbol = position['symbol']
    buttons.append([
        InlineKeyboardButton(
          text=signal,
          callback_data=str(VIEW_POSITION.format(symbol)))])

  #add_back_button(buttons, BACK_BUTTON.format("MAIN"))
  buttons.append([InlineKeyboardButton(BACK, callback_data="GOD")])
  keyboard = InlineKeyboardMarkup(buttons)
  update.callback_query.edit_message_text(OPEN_POSITIONS, reply_markup=keyboard)
  return 3

def view_position(update, context):
  position = context.user_data['position'] if 'position' in context.user_data else None
  # if entering position view for the first time for this position
  if position is None:
    # Get position ID
    symbol = context.__dict__['matches'][0].string.replace('VIEW_POSITION: ','')
    print(symbol)
    print(next(get_open_positions_presentation())['symbol'])
    # Get position data
    position = next(x for x in get_open_positions_presentation() if x['symbol'] == symbol)

    # Set working position in user_data
    context.user_data['position'] = position


  # Create button options
  buttons = [[InlineKeyboardButton("Set SL", callback_data=SET_STOP_LOSS)],
            [InlineKeyboardButton("Set TP", callback_data=SET_TAKE_PROFIT)],
            [InlineKeyboardButton("Close", callback_data=CLOSE_POSITION)]]
  buttons = []
  add_back_button(buttons, BACK_BUTTON.format("POSITIONS"))

  # Create keyboard and callback
  keyboard = InlineKeyboardMarkup(buttons)
  msg = "Name: {}\nOpen: {}\nPrice: {}\nProfit: {}"\
    .format(position['name'], position['open'], position['price'], position['profit'])
  update.callback_query.edit_message_text(msg, reply_markup=keyboard)
  return 3

def set_stop_loss(update, context):
  update.callback_query.answer()
  update.callback_query.edit_message_text(text="Set stop loss")
  context.user_data['position']['SL'] = None
  return 3

def set_take_profit(update, context):
  update.callback_query.answer()
  update.callback_query.edit_message_text(text="Set take profit")
  context.user_data['position']['TP'] = None
  return 3

def close_position(update, context):
  buttons = []
  add_confirm_button(buttons, CONFIRM_CLOSE_POSITION)
  add_cancel_button(buttons)
  keyboard = InlineKeyboardMarkup(buttons)
  update.callback_query.edit_message_text("Close position?", reply_markup=keyboard)

def add_cancel_button(buttons):
  buttons.append([InlineKeyboardButton(CANCEL, callback_data=CANCEL_STOP_LOSS)])

def add_confirm_button(buttons, CONFIRMATION):
  buttons.append([InlineKeyboardButton(CONFIRM, callback_data=CONFIRMATION)])

def add_back_button(buttons, PATH):
  buttons.append([InlineKeyboardButton(BACK, callback_data=PATH)])

def modify_position(update, context):
  reply_text = ""
  buttons = []

  if 'SL' in context.user_data['position']:
    context.user_data['position']['SL'] = update.message.text
    add_confirm_button(buttons, CONFIRM_STOP_LOSS)
    reply_text = "You set the stop loss to {}".format(update.message.text)

  elif 'TP' in context.user_data['position']:
    context.user_data['position']['TP'] = update.message.text
    add_confirm_button(buttons, CONFIRM_TAKE_PROFIT)
    reply_text = "You set the take profit to {}".format(update.message.text)

  add_cancel_button(buttons)
  keyboard = InlineKeyboardMarkup(buttons)
  update.message.reply_text(reply_text, reply_markup=keyboard)

  return 3

def confirm_stop_loss(update, context):
  pprint(context.user_data)
  # ROBINHOOD LOGIC TO CHANGE STOP LOSS
  view_position(update, context)

def confirm_take_profit(update, context):
  pprint(context.user_data)
  # ROBINHOOD LOGIC TO CHANGE TAKE PROFIT
  view_position(update, context)

def confirm_close_position(update, context):
  # ROBINHOOD LOGIC TO CLOSE POSITION
  view_positions(update, context)

def handle_back(update, context):
  cmd = context.__dict__['matches'][0].string.split(": ")[-1]
  if cmd == 'POSITIONS':
    view_positions(update, context)

  elif cmd == "MAIN":
    print(context.__dict__['matches'][0].string)
    return 1


def get_callbacks(menu):
  return [CallbackQueryHandler(view_position, pattern='^' + VIEW_POSITION.format('') + '?'),
            CallbackQueryHandler(view_position, pattern='^' + CANCEL_STOP_LOSS + '$'),
            CallbackQueryHandler(confirm_stop_loss, pattern='^' + CONFIRM_STOP_LOSS + '$'),
            CallbackQueryHandler(confirm_close_position, pattern='^' + CONFIRM_CLOSE_POSITION + '$'),
            CallbackQueryHandler(confirm_take_profit, pattern='^' + CONFIRM_TAKE_PROFIT + '$'),
            CallbackQueryHandler(set_stop_loss, pattern='^' + SET_STOP_LOSS + '$'),
            CallbackQueryHandler(set_take_profit, pattern='^' + SET_TAKE_PROFIT + '$'),
            CallbackQueryHandler(close_position, pattern='^' + CLOSE_POSITION + '$'),
            CallbackQueryHandler(handle_back, pattern='^' + BACK_BUTTON.format('') + '?'),
            CallbackQueryHandler(menu, pattern='^' + "GOD" + '?'),
            MessageHandler(Filters.text & ~Filters.command, modify_position)]