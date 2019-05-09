from datetime import datetime

from commons.emoji import EXP_TODAY
from commons.emoji import EXP_TOMORROW
from commons.emoji import NEW
from commons.emoji import NINTENDO
from commons.emoji import STAR
from commons.settings import WEBSITE_URL

SEPARATOR = '\n___\n'


def header(system=None, country=None):

    header = []

    if system:
        header.append(f'>`{NEW} new` ')
        header.append(f'`{EXP_TOMORROW} expires tomorrow` ')
        header.append(f'`{EXP_TODAY} expires today` ')

    header.append(f'`{STAR} wishlist count` ')
    header.append(f'`{NINTENDO} published by nintendo`')
    header.append(SEPARATOR)

    if system:
        header.append(f'You can add games to your wishlist [HERE]({WEBSITE_URL}/wishlist/{system.lower()}/{country.lower()})')

    return header


def footer(system=None, country=None):
    now = datetime.utcnow()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    time = now.strftime("%H:%M UTC")

    footer = [
        SEPARATOR,
        '* Developed by /u/uglyasablasphemy',
        '  * [Switch Friend Code](https://nin.codes/uglyasablasphemy)',
        '  * [GitHub](https://github.com/federicocalendino/nintendeals)',
        '* [RES](https://redditenhancementsuite.com) is recommended for table sorting on desktop',
        '* If you have perfomance issues, you might want to check out:',
        '  * [Reddit is Fun](https://play.google.com/store/apps/details?id=com.andrewshu.android.reddit)',
        '  * [Apollo for Reddit](https://itunes.apple.com/us/app/apollo-for-reddit/id979274575)',
        SEPARATOR,
        f'Last update: [{timestamp}](https://google.com/search?q={time})',
        SEPARATOR
    ]

    if system:
        footer.append(f'{STAR} You can add games to your wishlist [HERE]({WEBSITE_URL}/wishlist/{system.lower()}/{country.lower()})')
    else:
        footer.append(f'{STAR} You can add games to your wishlist [HERE]({WEBSITE_URL})')

    return footer

