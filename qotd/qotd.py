"""
Display some quotes from Wikiquote.
"""

import re
import datetime

import sopel.config.types as config
from sopel import module, tools

class QotdSection(config.StaticSession):
    """
    Base section for configuring qotd module.
    """
    translate_quote = config.ChoiceAttribute(
        'translate_quote',
        ['true', 'on', '1', 'false', 'off', '0'],
        'true'
    )
    language_subdomain = config.ValidatedAttribute(
        'language_subdomain',
        str,
        default='fr'
    )
    enabled = config.ChoiceAttribute(
        'enabled',
        ['true', 'on', '1', 'false', 'off', '0'],
        'true'
    )
    publishing_time = config.ValidatedAttribute(
        'publishing_time',
        lambda str_value: datetime.datetime.strptime(
            "1900-01-01 {}".format(str_value),
            "%Y-%m-%d %H:%M:%S").time(),
        default='09:00:00')

def setup(bot):
    bot.config.define_section("qotd", QotdSection)
    bot.memory['qotd'] = tools.SopelMemory()

def configure(config):
    config.define_section("qotd", QotdSection)
    config.qotd.configure_setting(
        'translate_quote',
        'Does not return the original quote but a translated one. (default: true)'
    )
    config.qotd.configure_setting(
        'language_subdomain',
        'Fetch quotes from this subdomain of wikiquote. (default: fr)'
    )
    config.qotd.configure_setting(
        'enabled',
        'Does the bot must send the quote of the day at a given time.'
    )
    config.qotd.configure_setting(
        'publishing_time',
        'Time at which send the qotd. (format: HH:MM:SS)'
    )

def get_qotd(bot):
    if (not bot.memory['qotd'].contains('qotd') or
            (datetime.datetime.now() - bot.memory['qotd']['lastQotdTime'] >
             datetime.timedelta(days=1))
       ):

        qotd_page_content = tools.url(
            "https://{}.wikiquote.org/api/rest_v1/page/html/Modèle:Citation_du_jour".format(
                bot.config.qotd.language_subdomain
            )
        )
        content_matching = re.match(
            qotd_page_content,
            r'<i>(?P<qotd>.+)</i>(?P<author>.+)'
        )
        if content_matching:
            bot.memory['qotd']['qotd'] = {
                'quote': content_matching.group('qotd'),
                'author': content_matching.group('author')
            }
            bot.memory['qotd']['lastQotdTime'] = datetime.datetime.now()

    return bot.memory['qotd']['qotd']



@module.command('qotd')
@module.example('.qotd')
def qotd_command(bot, trigger):
    qotd = get_qotd(bot)
    bot.say(bot.config.qotd.format_string.format(
        quote=qotd['quote'],
        author=qotd['author'],
        url=None
    ))

@module.command('wikiquote')
def random_quote_command(bot, trigger):
    pass
