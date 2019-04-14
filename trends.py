from collections import Counter

from db.mongo import GamesDatabase
from db.mongo import PricesDatabase


WEEKDAYS = {
    0: 'monday   ',
    1: 'tuesday  ',
    2: 'wednesday',
    3: 'thursday ',
    4: 'friday   ',
    5: 'saturday ',
    6: 'sunday   ',
}


def get_games_and_prices(system):
    games = GamesDatabase().load_all(
        filter={
            'system': system,
            'free_to_play': False
        }
    )

    prices = PricesDatabase().load_all(
        filter={
            'system': system
        }
    )

    return {game.id: game for game in games}, prices


def sales_trends(system):
    games, prices = get_games_and_prices(system)

    sales = Counter()

    weekdays = {
        'US': Counter(),
        'EU': Counter(),
        'JP': Counter(),
    }

    durations = {
        'US': Counter(),
        'EU': Counter(),
        'JP': Counter(),
    }

    for data in prices:
        if data.game_id not in games:
            continue

        game = games.get(data.game_id)

        for country, price in data.prices.items():
            if not price:
                continue

            if country not in ['US', 'EU', 'JP']:
                continue

            for sale in price.sales:
                sales.update([country])

                weekday = WEEKDAYS[sale.start_date.weekday()]
                weekdays[country][weekday] += 1

                diff = sale.end_date - sale.start_date
                days = diff.days

                if round(diff.seconds/60/60) == 24:
                    days += 1

                durations[country][days] += 1

    # - Weekdays -------------------------------------------------
    for country, counter in weekdays.items():
        print(f'\n{country}')

        total = sum(counter.values())

        for weekday, value in counter.most_common():
            p = 100 * value / total

            if p < 1:
                continue

            print(f' > {weekday} : {"◽️" * int(p)} ({p:0.2f}%)')

    # - Durations -------------------------------------------------
    for country, counter in durations.items():
        print(f'\n{country}')

        total = sum(counter.values())

        for duration, value in counter.most_common():
            p = 100 * value/total

            if p < 1:
                continue

            print(f' > {duration: <2} days : {"◽️" * int(p)} ({p:0.2f}%)')


sales_trends('Switch')

