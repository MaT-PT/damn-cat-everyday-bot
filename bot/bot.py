#!/usr/bin/env python3

from __future__ import annotations

import logging
from argparse import ArgumentParser
from datetime import UTC
from io import BytesIO
from os import getenv
from typing import TYPE_CHECKING

from aiocron import crontab  # type: ignore[import-untyped]
from dotenv import load_dotenv
from telegram import MessageEntity, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler
from telegram.helpers import escape_markdown

from .imglib import generate_image
from .utils import LogLevel

if TYPE_CHECKING:
    from telegram.ext._utils.types import BD, BT, CCT, CD, JQ, UD

TARGET_CHANNEL = "@DamnCatEveryDay"

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING
)
LOGGER = logging.getLogger(__name__)


async def post_init(app: Application[BT, CCT, UD, CD, BD, JQ]) -> None:
    bot = app.bot
    name = " ".join(n for n in (bot.first_name, bot.last_name) if n)
    print(f"Bot initialized: {name} ({bot.name}) [{bot.link}]")


async def post_stop(app: Application[BT, CCT, UD, CD, BD, JQ]) -> None:
    print("Bot was stopped, shutting down...")


async def post_shutdown(app: Application[BT, CCT, UD, CD, BD, JQ]) -> None:
    print("Bot was shut down successfully")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is None:
        return
    # with open("img/welcome-cat.png", "rb") as photo:
    #     await chat.send_photo(
    #         photo=photo,
    #         caption="Hello! This bot posts on @DamnCatEveryDay every day.",
    #     )
    await chat.send_photo(
        photo="AgACAgQAAxkDAAMLaV06jEuXmUWSw27QclYflIa1VIUAAlAMaxscUOhSE5qC1shXweoBAAMCAAN3AAM4BA",
        caption="Hello! This bot posts on @DamnCatEveryDay every day.",
    )


async def handle_error(update: object | None, context: ContextTypes.DEFAULT_TYPE) -> None:
    error = context.error
    LOGGER.error("Exception while handling update: %s", update, exc_info=error)
    if isinstance(update, Update):
        message = update.effective_message
        if message is not None:
            err_msg = (
                "_An unknown error occurred._"
                if error is None
                else "_An error occurred:_\n\n"
                f"`{escape_markdown(str(error), version=2, entity_type=MessageEntity.CODE)}`"
            )
            await message.reply_text(err_msg, parse_mode=ParseMode.MARKDOWN_V2, do_quote=True)


def main() -> None:
    parser = ArgumentParser(description="Damn Cat Everyday Bot")
    parser.add_argument(
        "-t", "--token", type=str, help="Telegram bot token (overrides BOT_TOKEN env variable)"
    )
    parser.add_argument(
        "-c", "--channel", type=str, default=TARGET_CHANNEL, help="Telegram channel username"
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=LogLevel,
        default=LogLevel.WARNING,
        help="Set the logging level (default: WARNING)",
    )
    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level.value)

    bot_token: str | None = args.token or getenv("BOT_TOKEN")
    if bot_token is None:
        raise ValueError(
            "No --token given and BOT_TOKEN environment variable is not set (you can use a .env file)"
        )
    target_channel: str = args.channel
    if not (
        target_channel.startswith("@")
        or "t.me/" in target_channel
        or target_channel.removeprefix("-").isdigit()
    ):
        target_channel = "@" + target_channel
    LOGGER.info("Using target channel: %s", target_channel)

    print("Building bot...")
    app = (
        Application
        .builder()
        .token(bot_token)
        .concurrent_updates(16)
        .http_version("2")
        .get_updates_http_version("2")
        .post_init(post_init)
        .post_stop(post_stop)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_error_handler(handle_error, block=False)
    app.add_handler(CommandHandler("start", start, block=False))

    async def print_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        print(update)

    app.add_handler(MessageHandler(None, print_msg, block=False))

    @crontab("0 8 * * *", tz=UTC)  # At 08:00 AM every day
    async def daily_post_task() -> None:
        chat = await app.bot.get_chat(target_channel)
        LOGGER.info("Generating daily image...")
        image = generate_image()
        iofile = BytesIO()
        image.save(iofile, format="PNG")
        iofile.seek(0)
        LOGGER.info("Posting daily image...")
        await chat.send_photo(photo=iofile)
        LOGGER.info("Posted daily image to %s (%d)", target_channel, chat.id)

    print("Starting bot...")
    app.run_polling()
    print("Goodbye!")


if __name__ == "__main__":
    main()
