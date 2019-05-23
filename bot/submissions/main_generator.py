from bot.submissions.common import SEPARATOR
from bot.submissions.common import footer
from bot.submissions.common import header

from commons.config import COUNTRIES
from commons.emoji import EMPTY
from commons.emoji import STAR
from commons.emoji import WARNING
from commons.keys import FLAG
from commons.keys import NAME
from commons.keys import REGION
from commons.keys import US, CH, NZ


def make_row(game, countries_with_sale, avg_discount):
    countries = []

    for country in COUNTRIES:
        countries.append(countries_with_sale.get(country, EMPTY))

        if country in [US, CH, NZ]:
            countries.append(' ')

    countries = ''.join(countries)

    title = game.title

    if len(title) > 35:
        title = f'{title[:34]}…'.replace(' …', '…')

    return f'{title}|{countries}|`{int(avg_discount)}`|{game.scores.metascore}|{game.scores.userscore}|{game.wishlisted}'


def make_table(games, prices, system):
    games = sorted(games.values(), key=lambda x: x.wishlisted, reverse=True)

    content = [
        f'Title | Countries/Regions | % | MS | US | {STAR} ',
        '--- | --- | :---: | :---: | :---: | :---:'
    ]

    for game in games[:30]:
        if game.system != system:
            continue

        if not game.wishlisted:
            continue

        countries = {}

        discounts = set()

        for country, details in COUNTRIES.items():
            nsuid = game.nsuids.get(details[REGION])

            if not nsuid:
                continue

            price = prices.get(nsuid)

            if not price:
                continue

            country_price = price.prices[country]

            if not country_price:
                continue

            latest_sale = country_price.active

            if not latest_sale:
                continue

            countries[country] = details[FLAG]

            discounts.add(latest_sale.discount)

        if len(countries):
            row = make_row(game, countries, sum(discounts) / len(discounts))
            content.append(row)

    if len(content) < 3:
        return None

    return '\n'.join(content)


def generate(games, prices, submissions, system):
    title = f'Current Nintendo {system} eShop deals'

    table = make_table(games, prices, system)

    content = []

    content.extend(header())

    content.append('> 💸 👉 PRICES AND SCORES IN THE LINKS AT THE BOTTOM 👈 💸')
    content.append('')

    if table:
        content.append('###Most wanted games on sale')
        content.append('')
        content.append(table)
        content.append(SEPARATOR)

    content.append('###For prices and more check your country/region post')
    content.append(f'> *{WARNING} There\'s a known bug on reddit mobile where links won\'t open correctly*')
    content.append('')

    content.append('-|new sales this week|total sales')
    content.append('---|:---:|:---:')

    for country, details in COUNTRIES.items():
        key = f'{system}/{country}'

        submission = submissions.get(key)

        if not submission:
            continue

        content.append(
            f'[{details[FLAG]} {details[NAME]}]({submission.url})|{submission.new_sales}|{submission.total_sales}'
        )

    content.extend(footer())

    return title, '\n'.join(content)
