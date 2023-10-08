import requests

# Bellow is the API setup and constants, these can be changed to make our betting different


def arbitrage_function(key, bet_amount):

    SPORT = 'upcoming'  # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

    REGIONS = 'us'  # uk | us | eu | au. Multiple can be specified if comma delimited

    MARKETS = 'h2h'  # h2h | spreads | totals. Multiple can be specified if comma delimited

    ODDS_FORMAT = 'decimal'  # decimal | american

    DATE_FORMAT = 'iso'  # iso | unix

    BET_SIZE = bet_amount

    KEY = key

    odds_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        params={
            'api_key': KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        }
    )

    # Check the response status code
    if odds_response.status_code == 200:
        # The request was successful, parse the JSON response
        odds_response = odds_response.json()
    else:
        return -1  # This will depend on your specific requirements.

    BOOKMAKER_INDEX = 0
    NAME_INDEX = 1
    ODDS_INDEX = 2
    FIRST = 0

    # This formats our event data into a format that works for calculating arbitrage betting opportunities

    class Event:
        def __init__(self, data):
            self.data = data
            self.sport_key = data['sport_key']
            self.id = data['id']

        def find_best_odds(self):
            num_outcomes = len(
                self.data['bookmakers'][FIRST]['markets'][FIRST]['outcomes'])
            self.num_outcomes = num_outcomes

            best_odds = [[None, None, float('-inf')]
                         for _ in range(num_outcomes)]

            bookmakers = self.data['bookmakers']
            for index, bookmaker in enumerate(bookmakers):
                if 'markets' not in bookmaker or not bookmaker['markets']:
                    continue
                markets = bookmaker['markets']
                if len(markets) <= FIRST or 'outcomes' not in markets[FIRST] or not markets[FIRST]['outcomes']:
                    continue
                outcomes = markets[FIRST]['outcomes']
                for outcome in range(num_outcomes):
                    if len(outcomes) <= outcome:
                        continue
                    bookmaker_odds = float(outcomes[outcome]['price'])
                    current_best_odds = best_odds[outcome][ODDS_INDEX]

                    if bookmaker_odds > current_best_odds:
                        best_odds[outcome][BOOKMAKER_INDEX] = bookmaker['title']
                        best_odds[outcome][NAME_INDEX] = outcomes[outcome]['name']
                        best_odds[outcome][ODDS_INDEX] = bookmaker_odds

            self.best_odds = best_odds
            return best_odds

        def arbitrage(self):
            total_arbitrage_percentage = 0
            for odds in self.best_odds:
                total_arbitrage_percentage += (1.0 / odds[ODDS_INDEX])

            self.total_arbitrage_percentage = total_arbitrage_percentage
            self.expected_earnings = (
                BET_SIZE / total_arbitrage_percentage) - BET_SIZE

            # if the sum of the reciprocals of the odds is less than 1, there is opportunity for arbitrage
            if total_arbitrage_percentage < 1:
                return True
            return False

        # converts decimal/European best odds to American best odds
        def convert_decimal_to_american(self):
            best_odds = self.best_odds
            for odds in best_odds:
                decimal = odds[ODDS_INDEX]
                if decimal >= 2:
                    american = (decimal - 1) * 100
                elif decimal < 2:
                    american = -100 / (decimal - 1)
                odds[ODDS_INDEX] = round(american, 2)
            return best_odds

        def calculate_arbitrage_bets(self):
            bet_amounts = []
            for outcome in range(self.num_outcomes):
                individual_arbitrage_percentage = 1 / \
                    self.best_odds[outcome][ODDS_INDEX]
                bet_amount = (BET_SIZE * individual_arbitrage_percentage) / \
                    self.total_arbitrage_percentage
                bet_amounts.append(round(bet_amount, 2))

            self.bet_amounts = bet_amounts
            return bet_amounts
    events = []
    for data in odds_response:
        events.append(Event(data))
    arbitrage_events = []
    for event in events:
        best_odds = event.find_best_odds()
        if event.arbitrage():
            arbitrage_events.append(event)
    if len(arbitrage_events) == 0:
        print("No arbitrage opportunities found.")
        return -1
    else:
        MAX_OUTCOMES = max([event.num_outcomes for event in arbitrage_events])
        ARBITRAGE_EVENTS_COUNT = len(arbitrage_events)

    for event in arbitrage_events:
        event.calculate_arbitrage_bets()
        event.convert_decimal_to_american()

    MAX_OUTCOMES = max([event.num_outcomes for event in arbitrage_events])
    ARBITRAGE_EVENTS_COUNT = len(arbitrage_events)

    arbitrage_events_data = []
    # Collect information about each arbitrage event
    for event in arbitrage_events:
        event_data = {
            'ID': event.id,
            'Sport Key': event.sport_key,
            'Expected Earnings': round(event.expected_earnings, 2),
            'Total Arbitrage Percentage': round(event.total_arbitrage_percentage, 8),
            'Best Odds': [],
        }

        for outcome, amount in zip(event.best_odds, event.bet_amounts):
            outcome_data = {
                'Bookmaker': outcome[BOOKMAKER_INDEX],
                'Name': outcome[NAME_INDEX],
                'Odds': outcome[ODDS_INDEX],
                'Bet Amount': round(amount, 2)
            }
            event_data['Best Odds'].append(outcome_data)
        arbitrage_events_data.append(event_data)
    return arbitrage_events_data
