import locale
import logging
import datetime as dt
from datetime import datetime

import telegram.ext

from notion.managers.homework.homeworkManager import HomeworkManager
from settings import Settings
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


def get_groups():
    today_mid = datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)
    groups = [
        {
            "label": "Vencidas",
            "ref": datetime.now()
        },
        {
            "label": "Hoy",
            "ref": today_mid
        },
        {
            "label": "Mañana",
            "ref": today_mid + dt.timedelta(days=1)
        }
    ]
    for i in range(2, 8):
        ref = today_mid + dt.timedelta(days=i)
        groups.append({
            "label": ref.strftime('%A').capitalize(),
            "ref": ref
        })
    return groups


def get_time_group(due: datetime, last_group_index: int, groups: list):
    if last_group_index is None:
        return None

    for i in range(last_group_index, len(groups)):
        if due <= groups[i]["ref"]:
            return i
    return None


async def homeworks(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    undone_list = HomeworkManager(chat_id).query_undone()
    msg = ''
    last_group_index = 0
    groups = get_groups()
    for i, hw in enumerate(undone_list):
        group_index = get_time_group(hw.due, last_group_index, groups)
        if group_index != last_group_index or i == 0:
            last_group_index = group_index
            label = groups[group_index]["label"] if group_index is not None else "Futuras"
            msg += f'\n`----------| `*_{label}_*` |----------`\n'

        msg += hw.to_markdown() + '\n'

    await context.bot.send_message(chat_id=chat_id, parse_mode="MarkdownV2", text=msg)


async def command_homeworks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await homeworks(context, chat_id)


async def job_homeworks(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await homeworks(context, job.chat_id)


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    reminder = Settings(chat_id).get_reminder_time()
    #today = dt.datetime.today().replace(hour=reminder.tm_hour, minute=reminder.tm_min, tzinfo=dt.timezone(dt.timedelta(hours=-6)))
    today = dt.datetime.now().replace(tzinfo=dt.timezone(dt.timedelta(hours=-6))) + dt.timedelta(seconds=10)
    context.job_queue.run_repeating(job_homeworks, dt.timedelta(days=1), first=today, name=str(chat_id), chat_id=chat_id)

    await update.effective_message.reply_text(f"Next reminder at {today}")


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    application = ApplicationBuilder().token(Settings.bot_token()).build()
    application.add_handler(CommandHandler('homeworks', command_homeworks))
    application.add_handler(CommandHandler('set_timer', set_timer))

    application.run_polling()
