from collections import Counter
from datetime import datetime

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

    games_c = Counter()
    sales = Counter()

    oldest = {
        'US': datetime.utcnow(),
        'EU': datetime.utcnow(),
        'JP': datetime.utcnow(),
    }

    weekdays = {
        'US': Counter(),
        'EU': Counter(),
        'JP': Counter(),
    }

    hours = {
        'US': Counter(),
        'EU': Counter(),
        'JP': Counter(),
    }

    durations = {
        'US': Counter(),
        'EU': Counter(),
        'JP': Counter(),
    }

    full_prices = {
        'US': Counter(),
        'EU': Counter(),
        'JP': Counter(),
    }

    __prices = {
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

            games_c.update([country])

            full_prices[country].update([f'{price.currency} {price.full_price:04.0f}'])

            for sale in price.sales:

                if sale.start_date < oldest.get(country):
                    oldest[country] = sale.start_date

                __prices[country][round(price.full_price)] += 1

                sales.update([country])

                weekday = WEEKDAYS[sale.start_date.weekday()]
                weekdays[country].update([weekday])

                hours[country].update([sale.start_date.hour])

                diff = sale.end_date - sale.start_date
                days = diff.days

                if round(diff.seconds/60/60) == 24:
                    days += 1

                durations[country].update([days])

    # - Oldest ---------------------------------------------------
    for country, date in oldest.items():
        print(f'{country}: {date}')

    print()

    # - Games ---------------------------------------------------
    for country, count in games_c.items():
        print(f'{country}: {count}')

    print()

    # - Sales ---------------------------------------------------
    for country, count in sales.items():
        print(f'{country}: {count}')

    print()

    # - Weekdays -------------------------------------------------
    for country, counter in weekdays.items():
        print(f'\n{country}')

        total = sum(counter.values())

        for weekday, value in counter.most_common():
            p = 100 * value / total

            if p < 1:
                continue

            print(f' > {weekday} : {"◽️" * (int(p) // 2)} ({p:0.2f}%)')

    # - Hours -------------------------------------------------
    for country, counter in hours.items():
        print(f'\n{country}')

        total = sum(counter.values())

        for hour, value in counter.most_common():
            p = 100 * value / total

            if p < 1:
                continue

            print(f' > {hour:02d}:00hs : {"◽️" * int(p)} ({p:0.2f}%)')

    # - Durations -------------------------------------------------
    for country, counter in durations.items():
        print(f'\n{country}')

        total = sum(counter.values())

        for duration, value in counter.most_common():
            p = 100 * value/total

            if p < 1:
                continue

            print(f' > {duration:02d} days : {"◽️" * int(p)} ({p:0.2f}%)')

    # - Full Prices -------------------------------------------------

    for country, counter in __prices.items():
        print(f'\n{country}')

        total = sum(counter.values())

        for duration, value in counter.most_common():
            p = 100 * value/total

            if p < 1:
                continue

            print(f' > {duration:04d} : {"◽️" * (int(p/2))} ({p:0.2f}%)')


sales_trends('Switch')

