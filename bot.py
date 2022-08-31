import nextcord
from MyAnimeList import User, DiscordUser
from nextcord.ext import commands, tasks

bot = commands.Bot()


@bot.event
async def on_ready():
    check_myanimelist.start()
    print("Bot Is Active")


@bot.slash_command(description="Add user to track!")
async def track(
    interaction: nextcord.Interaction, username: str, discord_id: str = None
):
    discord_id = int(discord_id)
    if discord_id == None:
        discord_id = interaction.user.id
    if User.check_if_user_exists(username):
        DiscordUser(username, discord_id)
        User(username).save_data()
        await interaction.send(f"Tracking {username}", ephemeral=True)
    else:
        await interaction.send(f"User with {username} not found", ephemeral=True)


@bot.slash_command(description="Remove user")
async def remove(interaction: nextcord.Interaction, username: str):
    DiscordUser.remove_user(username)
    await interaction.send(f"Removed {username}", ephemeral=True)

@tasks.loop(seconds=300)
async def check_myanimelist():
    channel = bot.get_channel(877235557502181487)
    all_embeds = compare_all_users()
    for embed in all_embeds:
        await channel.send(embed=embed)


def compare_all_users() -> list:
    all_embeds = []
    
    for x in DiscordUser.load():
        username = str(x["username"]).capitalize()
        user = User(x["username"])
        data = user.compare_data()

        if data != []:
            for item in data:

                anime_title = item["anime_title"]
                subject = item["subject"]
                anime_img = item["anime_img"]
                new_value = item["new_value"]
                old_value = item["old_value"]

                if subject == "status":
                    if new_value == 1:
                        desc = "watching"
                    elif new_value == 2:
                        desc = "done with"
                    elif new_value == 3:
                        desc = "on-hold with"
                    elif new_value == 4:
                        desc = "droping"
                    else:
                        desc = "planing to watch"

                    title = f"{anime_title} | Changed Status"
                    full_desc = f"{username} is {desc} {anime_title}"

                    embed = nextcord.Embed(
                        title=anime_title,
                        description=full_desc,
                        color=nextcord.Color.green(),
                    )
                    embed.set_image(anime_img)
                    all_embeds.append(embed)

                elif subject == "num_watched_episodes":

                    if new_value > old_value:
                        epi_watched = new_value - old_value
                        full_desc = f"{username} has watched {epi_watched} episodes | from {old_value} to {new_value}"

                    title = f"{anime_title} | {old_value} ->  {new_value}"
                    embed = nextcord.Embed(
                        title=title,
                        description=full_desc,
                        color=nextcord.Color.green(),
                    )
                    embed.set_image(anime_img)
                    all_embeds.append(embed)

                elif subject == "score":

                    title = f"{anime_title} | New Score {new_value}"
                    full_desc = f"{username} has changed the score of {anime_title} from  {old_value} to {new_value}"
                    embed = nextcord.Embed(
                        title=anime_title,
                        description=full_desc,
                        color=nextcord.Color.green(),
                    )
                    embed.set_image(anime_img)
                    all_embeds.append(embed)

            user.save_data()

    return all_embeds


if __name__ == "__main__":
    # Enter own discord bot token
    bot.run("Discord bot token")
