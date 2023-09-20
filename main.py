import locale
import logging
import datetime as dt
from datetime import datetime

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


async def homeworks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    undone_list = HomeworkManager().query_undone()
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
        print(hw)
    await context.bot.send_message(chat_id=update.effective_chat.id, parse_mode="MarkdownV2", text=msg)
    return


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    application = ApplicationBuilder().token(Settings.get_appsettings()['botToken']).build()
    start_handler = CommandHandler('homeworks', homeworks)
    application.add_handler(start_handler)

    application.run_polling()
