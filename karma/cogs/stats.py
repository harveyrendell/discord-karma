import re
import io

import logging
import discord

import matplotlib
import matplotlib.pyplot as plt
params = {
    "text.color" : "w",
    "ytick.color" : "w",
    "xtick.color" : "w",
    "axes.labelcolor" : "w",
    "axes.edgecolor" : "w"
}
plt.rcParams.update(params)

from discord.ext import commands

from itertools import accumulate

import karma.database as db

logger = logging.getLogger(__name__)

valid_types = ['all', 'given', 'received', 'bff', 'graph']

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, help='Get the BFF score for two users (Person 1 -> Person 2).')
    async def bff(self, ctx, uid1, uid2):

        await ctx.channel.trigger_typing()
        logger.info("Command invoked: bff")

        guild = ctx.guild
        pattern = re.compile(r'<@!?(?P<user_id>\d+)>')
        match = pattern.search(uid1)
        if match and guild.get_member(int(match.group('user_id'))):
            match_other = pattern.search(uid2)
            if match_other and guild.get_member(int(match_other.group('user_id'))):
                bff, bff_score, err = calculate_bff(match.group('user_id'), uid_to_calculate=match_other.group('user_id'))
                if err == None:
                     await ctx.send("The BFF score for **{}** with **{}** is **{:.2f}**. Wow! :sparkling_heart:".format(
                         get_username(match.group('user_id'), guild),
                         get_username(match_other.group('user_id'), guild),
                         bff_score
                     ))
                else:
                    await ctx.send(err)
            else:
                await ctx.send('Could not find user: {}'.format(key))
        else:
            await ctx.send('Could not find user: {}'.format(key))

    @commands.command(pass_context=True, help='Get stats for the server, or mention a user for specifics.\nValid types are {}'.format(valid_types))
    async def stats(self, ctx, type, *args):
        await ctx.channel.trigger_typing()
        guild = ctx.guild

        if type not in valid_types:
            await ctx.send('Invalid stats type *{}*, valid types are {}'.format(type, valid_types))
        else:
            if not args:
                logger.info("Command invoked: stats (server)")
                response, file = get_karma_breakdown_server(type, guild)
                if response == None:
                    await ctx.send("Nobody has received any karma, so no stats can be provided".format(key))
                else:
                    await ctx.send(file=file, embed=response)
            else:
                logger.info("Command invoked: stats (user) | {} {}".format(type, *args))
                for key in args:
                    pattern = re.compile(r'<@!?(?P<user_id>\d+)>')
                    match = pattern.search(key)
                    if match and guild.get_member(int(match.group('user_id'))):
                        response, file = get_karma_breakdown_user(match.group('user_id'), type, guild)
                        if response == None:
                            await ctx.send("User {} hasn't received any karma, so no stats can be provided".format(key))
                        else:
                            await ctx.send(file=file, embed=response)
                    else:
                        await ctx.send('Could not find user: {}'.format(key))

def build_ranking(list, direction, guild, max_value=3):
    result = ""
    for i, user in enumerate(list):
        if i >= max_value:
            break;
        result += "({}) **{}**\n".format(
            user["totals"][direction],
            get_username(user["discord_id"], guild)
        )
    return result if result != "" else "*No ranking available*"

def build_relo_ranking(list, direction, guild, max_value=3):
    result = ""
    sign = "+" if direction == "positive" else "-"
    for i, pair in enumerate(list):
        if i >= max_value:
            break;
        result += "({}) **{}** -> **{}**\n".format(
            sign + str(pair[1]["totals"][direction]),
            get_username(pair[0], guild),
            get_username(pair[1]["discord_id"], guild),
        )
    return result if result != "" else "*No ranking available*"

def get_karma_breakdown_server(type, guild):
    # Go and fetch every single person
    karma_list = db.get_all_karma()

    if not karma_list:
        return None, None

    sorted_karma = sorted(karma_list, key=lambda k: k.karma, reverse=True)

    raw = {}
    totals = {}
    breakdowns = {}
    dates = {}

    # For each person in the server, break it down into karma given / recieved
    for karma in karma_list:
        uid = karma.discord_id
        raw[uid] = {}
        given = db.get_karma_given_raw(uid)
        received = db.get_karma_received_raw(uid)
        raw[uid]["given"] = given,
        raw[uid]["received"] = received

        breakdowns[uid]= {}
        breakdowns[uid]["given"] = db.get_karma_given_breakdown(uid, given)
        breakdowns[uid]["received"] = db.get_karma_received_breakdown(uid, received)

        dates[uid] = {}
        dates[uid]["given"] = db.get_karma_given_dates(uid, given)
        dates[uid]["received"] = db.get_karma_given_dates(uid, received)

    # This code is a copy pasta of part of what is in the user break, so really they should be merged

    # Get for each current karma user how much they've given and taken away
    karma_users_given_totals = [ {
            "discord_id" : karma.discord_id,
            "totals" : db.get_karma_given_total(karma.discord_id)
        } for karma in karma_list ]
    karma_users_given_totals_nice = sorted(karma_users_given_totals, key=lambda user : user["totals"]["positive"], reverse=True)
    karma_users_given_totals_bulli = sorted(karma_users_given_totals, key=lambda user : user["totals"]["negative"], reverse=True)

    # Get for each current karma user how much they've received and had removed
    karma_users_received_totals = [ {
            "discord_id" : karma.discord_id,
            "totals" : db.get_karma_received_total(karma.discord_id)
        } for karma in karma_list ]
    karma_users_received_totals_nice = sorted(karma_users_received_totals, key=lambda user : user["totals"]["positive"], reverse=True)
    karma_users_received_totals_bulli = sorted(karma_users_received_totals, key=lambda user : user["totals"]["negative"], reverse=True)


    karma_users_given_top_nice = []
    karma_users_given_top_bulli = []
    # Get the top karma given for each person
    for uid, breakdown in breakdowns.items():
        if breakdown["given"]:
            karma_users_given_top_nice.append((uid, max(breakdown["given"], key=lambda user: user["totals"]["positive"])))
            karma_users_given_top_bulli.append((uid, max(breakdown["given"], key=lambda user: user["totals"]["negative"])))

    karma_users_given_top_nice = sorted(karma_users_given_top_nice, key=lambda pair : pair[1]["totals"]["positive"], reverse=True)
    karma_users_given_top_bulli = sorted(karma_users_given_top_bulli, key=lambda pair : pair[1]["totals"]["negative"], reverse=True)

    # Ready to build ...
    output = discord.Embed(
        title='Stats Summary for {}'.format(guild.name),
        colour=discord.Colour.purple()
    )
    img_file = None

    if (type in ['received', 'all']):
        top_score = get_username(sorted_karma[0].discord_id, guild);
        top_karma = sorted_karma[0].karma;
        text = "The current top karma user is **{}**, with **{}** karma.".format(top_score, top_karma)
        if len(sorted_karma) > 1:
            second_score = get_username(sorted_karma[1].discord_id, guild)
            second_karma = sorted_karma[1].karma
            diff = top_karma - second_karma
            text += " **{}** is **{}** karma behind them, with **{}** karma.".format(second_score, diff, second_karma)

        output.add_field(
            name='Karma Collector :crown:',
            value=text,
            inline=False
        )

        rec_positive_ranking =  build_ranking(karma_users_received_totals_nice, "positive", guild)
        rec_negative_ranking =  build_ranking(karma_users_received_totals_bulli, "negative", guild)

        output.add_field(
            name='Karma Climb :chart_with_upwards_trend: (most karma gained rank)',
            value=rec_positive_ranking,
            inline=True
        )

        output.add_field(
            name='Karma Crash :chart_with_downwards_trend: (most karma lost rank)',
            value=rec_negative_ranking,
            inline=True
        )

        output.add_field(
            name='Karma Companions :heart_eyes: / Karma Killers :skull:',
            value='For information about karma recieved / removed, please see the mirrored given stats.',
            inline=False
        )

    if (type in ['given', 'all']):

        total_given_positive = 0
        total_given_negative = 0

        for total in karma_users_given_totals:
            total_given_positive += total["totals"]["positive"]
            total_given_negative += total["totals"]["negative"]

        correct_sum = db.get_all_karma_events_count();
        sorted_totals = sorted(karma_users_given_totals, key=lambda user : user["totals"]["positive"] + user["totals"]["negative"], reverse=True)

        top_given_score = get_username(sorted_totals[0]["discord_id"], guild);
        top_given_total = sorted_totals[0]["totals"]["positive"] + sorted_totals[0]["totals"]["negative"]

        given_text = "**{}** has been given, and **{}** has been taken, making for a total of **{} +/- karma** distributed.\n".format(
            total_given_positive,
            total_given_negative,
            correct_sum
        )

        given_text += "**{}** has moved the most karma, with **{} +/- karma** (or **{:.2%}** of total karma transactions).".format(
            top_given_score,
            top_given_total,
            top_given_total / correct_sum
        )

        if len(sorted_totals) > 1:
            second_given_score = get_username(sorted_totals[1]["discord_id"], guild);
            second_given_total = sorted_totals[1]["totals"]["positive"] + sorted_totals[1]["totals"]["negative"]
            given_diff = top_given_total - second_given_total
            given_text += "\n**{}** is **{}** karma behind them, with with **{} +/- karma** (or **{:.2%}** of total karma transactions).".format(
                second_given_score,
                given_diff,
                second_given_total,
                second_given_total / correct_sum
            )

        output.add_field(
            name='Karma Circulator :repeat:',
            value=given_text,
            inline=False
        )

        given_positive_ranking =  build_ranking(karma_users_given_totals_nice, "positive", guild)
        given_negative_ranking =  build_ranking(karma_users_given_totals_bulli, "negative", guild)

        output.add_field(
            name='Karma Conferred :ok_woman: (most karma given rank)',
            value=given_positive_ranking,
            inline=True
        )

        output.add_field(
            name='Karma Clobbered :no_good: (most karma taken rank)',
            value=given_negative_ranking,
            inline=True
        )

        karma_contributions = build_relo_ranking(karma_users_given_top_nice, "positive", guild)
        karma_killed = build_relo_ranking(karma_users_given_top_bulli, "negative", guild)

        output.add_field(
            name='Karma Contributions :gift: (people who have given most karma to someone else)',
            value=karma_contributions,
            inline=True
        )

        output.add_field(
            name='Karma Killed :regional_indicator_f: (people who have taken most karma from someone else)',
            value=karma_killed,
            inline=True
        )

    if (type in ['bff', 'all']):
        # Get all BFFs
        # Not transitive so we have to do it this way
        top_friend = None
        top_friends_friend = None
        top_friend_score = 0
        positive_impact_cache = {}
        given_breakdown_cache = {}
        for uid in breakdowns.keys():
            given_breakdown_cache[uid] = breakdowns[uid]["given"]

        for karma in karma_list:
            name = get_username(karma.discord_id, guild)
            bff, bff_score, err = calculate_bff(karma.discord_id, given_breakdown_cache, positive_impact_cache)
            if err == None:
                if bff_score > top_friend_score:
                    top_friend = name
                    top_friend_score = bff_score
                    top_friends_friend = get_username(bff, guild)
        if top_friend_score == 0:
            # Wow, nobody has BFFs cause everyone is rude
            value = "Sorry, top BFF can't be calculated as there is no pair that has positively impacted each other."
        else:
            value = "The best BFF pair is **{}** and **{}**, with a whopping score of **{:.2f}**".format(top_friend, top_friends_friend, top_friend_score)
        output.add_field(
            name=':sparkling_heart: Karma BFF :sparkling_heart:',
            value=value,
            inline=False
        )

    if (type in ['graph', 'all']):
        graph_points = []
        karma_days = {}

        for karma in karma_list:
            user = guild.get_member(int(karma.discord_id))
            name = get_username(karma.discord_id, guild)
            received_dates = dates[karma.discord_id]["received"]

            if received_dates:
                for day in received_dates:
                    if day["date"] not in karma_days:
                        karma_days[day["date"]] = 0
                    karma_days[day["date"]] += day["diff"]["positive"] + day["diff"]["negative"]

                x_coords, y_coords = zip(*((point["date"], point["diff"]["positive"] - point["diff"]["negative"]) for point in received_dates))
                accumulated = list(accumulate(y_coords))
                graph_points.append((user, x_coords, accumulated))

        max_day = max(karma_days, key=karma_days.get)
        max_amount = karma_days[max_day]

        buffer = generate_graph(graph_points, 'Karma over time for server', True)
        img_file = discord.File(buffer, filename="stats.png")
        output.set_image(url="attachment://stats.png")

        output.add_field(
            name='Karma Chart :bar_chart:',
            value="Below is a graph of the karma over time for the server. The day with the biggest karma change was **{}** with **{}** karma +/-".format(max_day, max_amount),
            inline=False
        )

    return output, img_file

def get_username(uid, guild):
    user = guild.get_member(int(uid))
    return user.name if user != None else 'Unknown User :ghost:'

def get_karma_breakdown_user(uid, type, guild):
    me = guild.get_member(int(uid))

    given_raw = db.get_karma_given_raw(uid)
    received_raw = db.get_karma_received_raw(uid)

    if not received_raw:
        return None, None

    # Get the breakdown of who + and -d your karma
    given_breakdown = db.get_karma_given_breakdown(uid, given_raw)
    received_breakdown = db.get_karma_received_breakdown(uid, received_raw)

    # Order the breakdowns
    given_breakdown_nice = sorted(given_breakdown, key=lambda user: user["totals"]["positive"], reverse=True)
    given_breakdown_bulli = sorted(given_breakdown, key=lambda user: user["totals"]["negative"], reverse=True)

    received_breakdown_nice = sorted(received_breakdown, key=lambda user: user["totals"]["positive"], reverse=True)
    received_breakdown_bulli = sorted(received_breakdown, key=lambda user: user["totals"]["negative"], reverse=True)

    # Net gained and lost per day, on the days you received karma
    received_dates = db.get_karma_received_dates(uid, received_raw)

    # Get all the karma to figure out an overall ranking
    karma_list = db.get_all_karma()
    sorted_karma = sorted(karma_list, key=lambda k: k.karma, reverse=True)
    karma_position_list = [i for i,v in enumerate(sorted_karma) if v.discord_id == uid]
    karma_position = karma_position_list[0] + 1 if len(karma_position_list) > 0 else 0

    # Get for each current karma user how much they've given and taken away
    karma_users_given_totals = [ {
            "discord_id" : karma.discord_id,
            "totals" : db.get_karma_given_total(karma.discord_id)
        } for karma in karma_list ]
    karma_users_given_totals_nice = sorted(karma_users_given_totals, key=lambda user : user["totals"]["positive"], reverse=True)
    karma_users_given_totals_bulli = sorted(karma_users_given_totals, key=lambda user : user["totals"]["negative"], reverse=True)

    given = next((user for user in karma_users_given_totals if user["discord_id"] == uid), None)
    given_totals = given["totals"]

    # Get for each current karma user how much they've received and had removed
    karma_users_received_totals = [ {
            "discord_id" : karma.discord_id,
            "totals" : db.get_karma_received_total(karma.discord_id)
        } for karma in karma_list ]
    karma_users_received_totals_nice = sorted(karma_users_received_totals, key=lambda user : user["totals"]["positive"], reverse=True)
    karma_users_received_totals_bulli = sorted(karma_users_received_totals, key=lambda user : user["totals"]["negative"], reverse=True)

    received = next((user for user in karma_users_received_totals if user["discord_id"] == uid), None)
    received_totals = received["totals"]

    # Ready to build ...
    output = discord.Embed(
        title='Stats Summary for {}'.format(me.name),
        colour=discord.Colour.purple()
    )

    if (type in ['received', 'all']):
        output.add_field(
            name='Karma Collector :crown:',
            value="You've gained **{} karma**, and lost **{} karma**, making for a total of **{} karma**, putting you at overall position **#{}**.".\
                format(received_totals["positive"],
                    received_totals["negative"],
                    received_totals["positive"] - received_totals["negative"],
                    karma_position
                ),
            inline=False
        )

        output.add_field(
            name='Karma Climb :chart_with_upwards_trend: (karma gained rank)',
            value="Position: **#{}**".format(karma_users_received_totals_nice.index(received) + 1),
            inline=True
        )

        output.add_field(
            name='Karma Crash :chart_with_downwards_trend: (karma lost rank)',
            value="Position: **#{}**".format(karma_users_received_totals_bulli.index(received) + 1),
            inline=True
        )

        karma_companions = build_ranking(received_breakdown_nice, "positive", guild)
        karma_killers = build_ranking(received_breakdown_bulli, "negative", guild)

        output.add_field(
            name='Karma Companions :heart_eyes: (gave the most karma to you)',
            value=karma_companions,
            inline=True
        )

        output.add_field(
            name='Karma Killers :skull: (took the most karma from you)',
            value=karma_killers,
            inline=True
        )

    if (type in ['given', 'all']):
        output.add_field(
            name='Karma Circulator :repeat:',
            value="You've given **{} karma**, and taken **{} karma**, making for a total of **{} +/- karma** distributed".\
                format(given_totals["positive"],
                    given_totals["negative"],
                    given_totals["positive"] + given_totals["negative"],
                )
                + " (or **{:.2%}** of total karma transactions)".\
                    format((given_totals["positive"] + given_totals["negative"]) / db.get_all_karma_events_count()),
            inline=False
        )

        output.add_field(
            name='Karma Conferred :ok_woman: (karma given rank)',
            value="Position: **#{}**".format(karma_users_given_totals_nice.index(given) + 1),
            inline=True
        )

        output.add_field(
            name='Karma Clobbered :no_good: (karma taken rank)',
            value="Position: **#{}**".format(karma_users_given_totals_bulli.index(given) + 1),
            inline=True
        )

        karma_contributions = build_ranking(given_breakdown_nice, "positive", guild)
        karma_killed = build_ranking(given_breakdown_bulli, "negative", guild)

        output.add_field(
            name='Karma Contributions :gift: (you gave the most karma to)',
            value=karma_contributions,
            inline=True
        )

        output.add_field(
            name='Karma Killed :regional_indicator_f: (you took the most karma from)',
            value=karma_killed,
            inline=True
        )

    img_file = None
    if (type in ['bff', 'all']):
        # Get BFF
        bff, bff_score, err = calculate_bff(uid, { uid : given_breakdown })
        output.add_field(
            name=':sparkling_heart: Karma BFF :sparkling_heart:',
            value=err if err != None else "Your BFF is **{}**, with a BFF score of **{:.2f}**".format(get_username(bff, guild), bff_score),
            inline=False
        )

    if (type in ['graph', 'all']):
        # Graph time
        x_coords, y_coords = zip(*((point["date"], point["diff"]["positive"] - point["diff"]["negative"]) for point in received_dates))
        max_karma = max(y_coords)
        accumulated = list(accumulate(y_coords))

        buffer = generate_graph([(me, x_coords, accumulated)], 'Karma over time for {}'.format(me.name))
        img_file = discord.File(buffer, filename="stats.png")
        output.set_image(url="attachment://stats.png")

        output.add_field(
            name='Karma Chart :bar_chart:',
            value="Below is a graph of your karma over time." + ("" if max_karma <= 0 else " Your max karma earned on a day is **{}**. Wow!".format(max_karma)),
            inline=False
        )

    return output, img_file

def generate_graph(users_to_map, title, show_legend=False):
    fig, ax = plt.subplots(figsize=(7, 7))
    colours_used = {}

    for info in users_to_map:
        user, x_coords, y_coords = info

        if user is None:
            hexcolour = '#99AAB5'
            name = 'Unknown User'
        else:
            hexcolour = '#%02x%02x%02x' % user.colour.to_rgb()
            if hexcolour == '#000000':
                hexcolour = '#99AAB5'
            name = user.name

        if hexcolour in colours_used:
            colours_used[hexcolour] = [(value + 1) * 2 for value in colours_used[hexcolour]]
        else:
            colours_used[hexcolour] = [1, 0]

        line, = ax.plot(x_coords, y_coords, color=hexcolour, label=name)
        line.set_dashes(colours_used[hexcolour])

    ax.set(xlabel='Time', ylabel='Karma Total', title=title)
    ax.grid()

    if show_legend:
        legend = ax.legend(bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=3)
        for text in legend.get_texts():
            text.set_color("black")

    ax.set_facecolor('#36393f')
    fig.patch.set_facecolor('#36393f')

    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.canvas.print_png(buffer)
    buffer.seek(0)

    return buffer

def calculate_bff(uid, given_cache=None, positive_impact_cache=None, uid_to_calculate=None):
    # First, get a list of people you have positively impacted
    if given_cache == None:
        given_cache = {}
    if positive_impact_cache == None:
        positive_impact_cache = {}

    if uid not in given_cache:
        given_cache[uid] = db.get_karma_given_breakdown(uid)
    if uid not in positive_impact_cache:
        positive_impact_cache[uid] = db.get_karma_positive_impact(uid, given_cache[uid])

    # If this list is empty, slam them for being rood
    if not positive_impact_cache[uid]:
        return None, 0, "Sorry, your BFF score can't be calculated as {} positively impacted anyone's karma.".format(
            "you haven't" if uid_to_calculate == None else "the first user hasn't"
        )

    uid_sum = sum([(user["totals"]["positive"] - user["totals"]["negative"]) for user in positive_impact_cache[uid]])

    if uid_to_calculate != None:
        # Calculating for a specific user
        user_impact = next((user for user in positive_impact_cache[uid] if user["discord_id"] == uid_to_calculate), None)
        if user_impact == None:
            # You haven't impacted them
            return None, 0, "Sorry, your BFF score can't be calculated, as you haven't positively impacted the other user."

        user_given = db.get_karma_given_breakdown(uid_to_calculate)
        user_positive =  db.get_karma_positive_impact(uid_to_calculate, user_given)

        if not user_positive:
            return None, 0, "Sorry, your BFF score can't be calculated, as the other user hasn't positively impacted anyone's karma."

        user_impact_you = next((user for user in user_positive if user["discord_id"] == uid), None)
        if user_impact_you == None:
            return None, 0, "Sorry, your BFF score can't be calculated, as the other user hasn't positively impacted you."
        else:
            # Nuke everyone else from the positive_impact_cache for the next loop
            positive_impact_cache[uid] = [user_impact]

    discord_id = None
    bff_score = 0

    for user in positive_impact_cache[uid]:
        if user["discord_id"] not in given_cache:
            given_cache[user["discord_id"]] = db.get_karma_given_breakdown(user["discord_id"])
        if user["discord_id"] not in positive_impact_cache:
            positive_impact_cache[user["discord_id"]] = db.get_karma_positive_impact(user["discord_id"], given_cache[user["discord_id"]])

        impact_uid = next((user for user in positive_impact_cache[user["discord_id"]] if user["discord_id"] == uid), None)
        if impact_uid != None:
            this_sum =sum([(user["totals"]["positive"] - user["totals"]["negative"]) for user in positive_impact_cache[user["discord_id"]]])
            this_score = (user["totals"]["positive"] - user["totals"]["negative"]) / uid_sum * 70 + (impact_uid["totals"]["positive"] - impact_uid["totals"]["negative"]) / this_sum * 40

            if this_score > bff_score:
                bff_score = this_score
                discord_id = user["discord_id"]

    if discord_id is None:
        return None, 0, "Sorry, your BFF score can't be calculated as nobody has positively impacted you."
    else:
        return discord_id, bff_score, None

# The setup function below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Stats(bot))
