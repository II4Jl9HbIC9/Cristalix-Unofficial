import hikari

bot = hikari.GatewayBot(token="MTE5MjgyMzA2MzQ5NTA0OTMyNw.GSrekc.Ee0l3yBzqQ343kk9zv9428XSFrP7yYS7d_nFYo")


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human:
        return

    me = bot.get_me()

    if me.id in event.message.user_mentions_ids:
        await event.message.respond("Нышыта")


bot.run()
