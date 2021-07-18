#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler
import logging

import os

TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

def start(update, context):
    """ This is a command callback for the /start command """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hola majete! Usa /set_reminder para configurar un recordatorio")

def notify_reminder(context):
    """ Notifies the given reminder given by the context. This is a job callback """
    job = context.job
    message = job.context['message']
    chat_id = job.context['chat_id']
    context.bot.send_message(chat_id=chat_id, text=f"Recuerda: {message}")

def set_reminder(update, context):
    """ Configures a reminder so that it will be called by the job queue when it expires """
    try:
        timeout_min = int(context.args[0])
        job_context = {
            'message': ' '.join(context.args[1:]),
            'chat_id': update.effective_chat.id
        }
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"He configurado un recordatorio en {timeout_min} minutos!")
        context.job_queue.run_once(notify_reminder, timeout_min * 60, context=job_context)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"Lo siento, no he entendido tu peticion:\n{e}")

class Command():
    def __init__(self, name, handler, description=None):
        self._name = name
        self._handler = CommandHandler(self._name, handler)
        self._description = description if description is not None else ''

    @property
    def name(self):
        """ Returns the command name """
        return self._name

    @property
    def description(self):
        """ Returns the description of the current command """
        return self._description

    def register(self, dispatcher):
        """ Registers the command with the given dispatcher """
        dispatcher.add_handler(self._handler)

class Commands():
    def __init__(self, updater):
        self._commands = []
        self._updater = updater

    def add(self, name, handler, description=None):
        """ Adds a command to the list of commands """
        command = Command(name, handler, description)
        self._commands.append(command)

    def register_all(self):
        """ Registers all commands in the dispatcher and informs the telegram bot
            service about available commands """
        dispatcher = self._updater.dispatcher
        bot = self._updater.bot
        commands = []
        for command in self._commands:
            command.register(dispatcher)
            commands.append((command.name, command.description))
        bot.set_my_commands(commands=commands)

def main():
    """ Runs the program for the bot """
    updater = Updater(token=TOKEN, use_context=True)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    commands = Commands(updater)
    commands.add('start', start, 'Comienza la ejecucion del bot')
    commands.add('help', start, 'Muestra la ayuda del bot')
    commands.add('set_reminder', set_reminder, 'Configura un recordatorio. El primer argumento '
        'es el timeout en minutos. El resto es el mensaje del recordatorio')
    commands.register_all()

    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()
