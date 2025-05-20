import os
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from flask import Request, Response
from movies_scraper import search_movies, get_movie

TOKEN = os.environ.get("TOKEN")
bot = Bot(token=TOKEN)

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

user_session = {}

def start(update, context):
    update.message.reply_text("Welcome! Send a movie name to search.")

def handle_text(update, context):
    chat_id = update.message.chat_id
    query = update.message.text
    movies, url_map = search_movies(query)

    if not movies:
        update.message.reply_text("No movies found.")
        return

    user_session[chat_id] = url_map

    reply = "Select a movie:\n"
    for movie in movies:
        reply += f"{movie['id']}: {movie['title']}\n"

    update.message.reply_text(reply)

def handle_movie_selection(update, context):
    chat_id = update.message.chat_id
    selected_id = update.message.text.strip()
    url_map = user_session.get(chat_id)

    if not url_map or selected_id not in url_map:
        update.message.reply_text("Invalid selection. Please search again.")
        return

    movie_details = get_movie(selected_id, url_map)

    if "error" in movie_details:
        update.message.reply_text(movie_details["error"])
        return

    caption = f"**{movie_details['title']}**"
    bot.send_photo(chat_id, photo=movie_details["image"], caption=caption, parse_mode="Markdown")

    for link in movie_details["links"]:
        bot.send_message(chat_id, text=link)

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.regex(r"^link\d+$"), handle_movie_selection))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

# Main Vercel handler
def handler(request: Request):
    if request.method == "POST":
        update = Update.de_json(request.get_json(), bot)
        dispatcher.process_update(update)
        return Response("ok", status=200)
    return Response("Method not allowed", status=405)
