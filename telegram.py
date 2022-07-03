from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import sqlite3

updater = Updater("5404669963:AAFRnO8imZ1IaYiU3svUNPTktkxv2bzBAS4",
				use_context=True)

def start(update: Update, context: CallbackContext):
	update.message.reply_text(
		"Hello sir, Welcome to the Bot.Please write\
		/help to see the commands available.")

def help(update: Update, context: CallbackContext):
	update.message.reply_text("""
	/viewalerts - To get notified by nearby alerts
	""")

def viewalert_url(update: Update, context: CallbackContext):
	update.message.reply_text("Enter Your Location")

def notifier(update: Update, context: CallbackContext):
	locationp = update.message.location   #returns a GeoPoint class if the message is a location share message else returns None

	con = sqlite3.connect('tracker.db', check_same_thread=False)
	c = con.cursor()
	sql_command2 = f"SELECT * FROM Alerts;"
	c.execute(sql_command2)
	rows = c.fetchall()
	str=''
	for i in rows:
		from geopy import distance
		center_point = [{'lat': float(locationp.latitude), 'lng': float(locationp.longitude)}]
		test_point = [{'lat': float(i[2]), 'lng': float(i[3])}]
		radius = 5
		center_point_tuple = tuple(center_point[0].values())
		test_point_tuple = tuple(test_point[0].values())
		dis = distance.distance(center_point_tuple, test_point_tuple).km
		if dis<=radius:
			str = str + i[1] + '//' + 'location at ' + i[2] + ',' + i[3] + '\n'
	update.message.reply_text(str)
 
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('viewalerts', viewalert_url))
updater.dispatcher.add_handler(MessageHandler(Filters.location, notifier))

updater.start_polling()
updater.idle()