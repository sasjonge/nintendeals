from datetime import datetime

from bot.submissions.common import SEPARATOR
from bot.submissions.common import footer
from bot.submissions.common import header
from commons.config import COUNTRIES
from commons.emoji import EXP_TODAY
from commons.emoji import EXP_TOMORROW
from commons.emoji import GEM
from commons.emoji import NEW
from commons.emoji import NINTENDO
from commons.emoji import PLAYERS
from commons.emoji import STAR
from commons.emoji import WARNING
from commons.keys import CURRENCY
from commons.keys import CURRENCY_CODE
from commons.keys import DIGITS
from commons.keys import FLAG
from commons.keys import ID
from commons.keys import NAME
from commons.keys import REGION
from commons.util import format_float


def make_row(game, country, price, sale, disable_url=False, **kwargs):
    now = datetime.utcnow()

    title = game.titles.get(country[REGION], game.title)

    if game.published_by_nintendo:
        title = f'{NINTENDO} {title}'

    if game.hidden_gem:
        title = f'{title} {GEM}'

    if len(title) > 27:
        title = f'{title[:26]}…'.replace(' …', '…')

    if not disable_url:
        if game.websites.get(country[ID]):
            title = '[{}]({})'.format(title, game.websites.get(country[ID]))

    new = (now - sale.start_date).days < 1

    if not kwargs.get('disable_formatting', False):
        bold = '**' if new else ''
    else:
        bold = ''

    emoji = NEW if new else ''

    time_left = sale.end_date - now
    formatted_time = sale.end_date.strftime('%b %d')

    if time_left.days > 0:
        days = time_left.days

        if days < 2:
            emoji = EXP_TOMORROW
    else:
        hours = round(time_left.seconds / 60 / 60)

        if hours <= 24:
            emoji = EXP_TODAY

        if hours > 0:
            formatted_time = f'{formatted_time} ({hours}h)'
        else:
            minutes = round(time_left.seconds / 60)
            formatted_time = f'{formatted_time} ({minutes}m)'

    country_price = price.prices[country[ID]]
    sale_price = format_float(sale.sale_price, country[DIGITS])

    full_price = format_float(country_price.full_price, country[DIGITS])

    if not kwargs.get('disable_full_prices', False):
        full_price = f' ~~{full_price}~~'
    else:
        full_price = ''

    wishlisted = game.wishlisted if game.wishlisted else ''
    metascore = game.scores.metascore if game.scores.metascore != '-' else ''
    userscore = game.scores.userscore if game.scores.userscore != '-' else ''

    if kwargs.get('disable_players'):
        return f'{bold}{title}{bold}|{emoji}|{formatted_time}|' \
               f'{country[CURRENCY]}{sale_price}{full_price}|`{sale.discount}`|' \
               f'{metascore}|{userscore}|' \
               f'{wishlisted}'
    else:
        return f'{bold}{title}{bold}|{emoji}|{formatted_time}|' \
            f'{country[CURRENCY]}{sale_price}{full_price}|`{sale.discount}`|' \
            f'{game.players}|{metascore}|{userscore}|' \
            f'{wishlisted}'


def make_tables(games, prices, system, country, **kwargs):
    now = datetime.utcnow()

    header = [
        f'Title | - | Expiration | {country[CURRENCY]} ({country[CURRENCY_CODE]}) | % | {PLAYERS} | MS | US | {STAR}',
        '--- | :---: | --- | :---: | :---: | :---: | :---: | :---: | :---:'
    ]

    if kwargs.get('disable_players'):
        header[0] = header[0].replace(f' {PLAYERS} |', '')
        header[1] = header[1][:-8]

    new_sales = []
    week_sales = []
    current_sales = []

    games_on_sale = 0

    for game_id, game in games.items():
        if game.system != system:
            continue

        nsuid = game.nsuids.get(country[REGION])

        if not nsuid:
            continue

        price = prices.get(nsuid)

        if not price:
            continue

        country_price = price.prices[country[ID]]

        if not country_price:
            continue

        latest_sale = country_price.active

        if not latest_sale:
            continue

        days = (now - latest_sale.start_date).days

        if kwargs.get('disable_soon_to_expire', False):
            time_left = latest_sale.end_date - now

            if time_left.days < 2:
                continue

        if days < 1:
            row = make_row(game, country, price, latest_sale,
                           disable_url=kwargs.get('disable_new_urls', False), **kwargs)
            new_sales.append(row)
        elif now.strftime("%V") == latest_sale.start_date.strftime("%V"):
            row = make_row(game, country, price, latest_sale,
                           disable_url=kwargs.get('disable_new_urls', False), **kwargs)
            week_sales.append(row)
        else:
            row = make_row(game, country, price, latest_sale,
                           disable_url=kwargs.get('disable_current_urls', False), **kwargs)
            current_sales.append(row)

        games_on_sale += 1

    return header + new_sales + week_sales, header + current_sales, games_on_sale


def generate(games, prices, system, country):
    country = COUNTRIES[country]

    disabled_urls = False
    disable_full_prices = False
    disable_players = False

    modifiers = {}

    for modifier in ['unused', 'disable_formatting', 'disable_current_urls', 'disable_new_urls', 'disable_full_prices', 'disable_players', 'disable_soon_to_expire']:
        modifiers[modifier] = True

        week_sales, current_sales, total_sales = make_tables(games, prices, system, country, **modifiers)

        size = len(''.join(week_sales)) + len(''.join(current_sales))

        if modifier in ['disable_current_urls', 'disable_new_urls']:
            disabled_urls = True

        if modifier in ['disable_full_prices']:
            disable_full_prices = True

        if modifier in ['disable_players']:
            disable_players = True

        if size < 39000:
            break

    title = f'{country[FLAG]} {country[ID]} ▪️ Current Nintendo {system} eShop deals'

    content = [
        f'#{country[NAME]}: {total_sales} deals\n'
    ]

    content.extend(header(system, country[ID], disable_players=disable_players))

    if len(week_sales) > 2:
        content.append(f'##Deals of this week: {len(week_sales) - 2} deals\n')
        content.extend(week_sales)
    else:
        content.append('##No new deals :(')

    content.append(SEPARATOR)
    content.append(f'##Active deals: {len(current_sales) - 2} deals\n')
    content.extend(current_sales)

    content.append('')

    if any((disabled_urls, disable_full_prices, disable_players)):
        content.append(f'{WARNING} some information is missing to fit eveything into reddit\'s 40k character limit\n')

        content.append('')

        if disabled_urls:
            content.append('* urls')
        if disable_full_prices:
            content.append('* full prices')
        if disable_players:
            content.append('* number of players')

    content.append('')

    content.extend(footer(system, country[ID]))

    return title, '\n'.join(content), len(week_sales) - 2, total_sales
