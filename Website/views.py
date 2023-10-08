from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User, Api_Key, Event, Outcome
from . import db
from flask_login import current_user, login_required
from .utils import arbitrage

views = Blueprint('views', __name__)


@views.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', user=current_user)


@views.route('/')
def return_home():
    return redirect(url_for('views.home'))


@views.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account.html', user=current_user)


@views.route('/help', methods=['GET', 'POST'])
def help():
    return render_template('help.html', user=current_user)


@views.route('/arb-calc', methods=['GET', 'POST'])
def arb_calc():
    odds_values = []
    ev_values = []
    stakes = []
    arbitrage_percent = 0
    if request.method == 'POST':
        # Checks the odds boxes, if they are valid they are addded to odds_values
        for i in range(1, 11):  # Assuming you have up to 10 odds input fields
            odds_field_name = 'odds' + str(i)
            odds_value = request.form.get(odds_field_name)
            if odds_value == '':
                odds_value = None
            if odds_value is not None:
                if odds_value in range(-99, 99):
                    flash('Odds must be greater than 100 or less than -100',
                          category='error')
                    break
                else:
                    odds_values.append(float(odds_value))
        if len(odds_values) <= 1:
            flash('At least two odds required for arbitrage calculator',
                  category='error')
        else:
            for odd in odds_values:
                if odd >= 0:
                    decimal_odds = (odd / 100) + 1
                else:
                    decimal_odds = (100 / abs(odd)) + 1
                ev_values.append(decimal_odds)
            arb_value = sum(ev_values)
            stake = request.form.get('stake')
            if stake == '':
                flash('Stake cannot be empty', category='error')
            elif stake is not None:
                stake = float(stake)  # Convert the stake to a float
                if stake <= 0:
                    flash(
                        'Stake must be greater than 0, no empty stakes allowed', category='error')
                else:
                    ev_sum = sum(ev_values)
                    for ev in ev_values:
                        individual_stake = stake/(1+(ev/(ev_sum-ev)))
                        print(individual_stake)
                        stakes.append(round(individual_stake, 2))
                    arbitrage_percent = 0
                    for ev in ev_values:
                        arbitrage_percent += (1/ev)*100
                    arbitrage_percent = round(arbitrage_percent, 2)
            else:
                flash('Stake cannot be empty', category='error')

    return render_template('arb_calc.html', user=current_user, stakes=stakes, arbitrage_percent=arbitrage_percent)


@views.route('/account/api', methods=['GET', 'POST'])
def return_account_api():
    if request.method == 'POST':
        # Get the api_key from the form and the users current api_key if any
        api_key = request.form.get('api_key')
        current_user_key = Api_Key.query.filter_by(
            user_id=current_user.id).first()
        # Check proper length of api_key
        if len(api_key) != 32:
            flash('Invalid API key', category='error')
        # Checks if the key is the users first one and needs an user id to link it or if the user already has a key
        else:
            if current_user_key:
                current_user_key.text = api_key
                db.session.commit()
            else:
                new_key = Api_Key(text=api_key, user_id=current_user.id)
                db.session.add(new_key)
            db.session.commit()
            flash('API key updated successfully', category='success')
            return redirect(url_for('views.account'))
    return render_template('account_api.html', user=current_user)


@views.route('/bet-finder', methods=['GET', 'POST'])
@login_required
def betfinder():
    if request.method == 'POST':
        # Clear the users current events and outcomes from the database
        current_user_events = Event.query.filter_by(
            user_id=current_user.id).all()
        for event in current_user_events:
            current_event_outcomes = Outcome.query.filter_by(
                event_id=event.id).all()
            for outcome in current_event_outcomes:
                db.session.delete(outcome)
            db.session.delete(event)
        db.session.commit()
        # Get the current users API Key
        current_user_key = Api_Key.query.filter_by(
            user_id=current_user.id).first()
        # Get the current users bet_amount within the html form
        bet_amount = request.form.get('bet_amount')
        # Check that the bet_amount from the html form was filled with a correct value
        if bet_amount == '':
            bet_amount = 0
        bet_amount = int(bet_amount)
        if bet_amount > 50000 or bet_amount <= 0:
            flash('Invalid bet amount, place range from 0-50000', category='error')
        else:
            # Commit the users new bet_amount to the database
            current_user.bet_amount = bet_amount
            db.session.commit()
            # Check that the user has set an API key in the database
            if current_user_key is None:
                flash('No API key found for user', category='error')
            else:
                # Call the arbitrage function and pass in the users key and the users bet_amount
                arbitrage_events_data = arbitrage.arbitrage_function(
                    current_user_key.text, bet_amount)
                # Failed cases within the arbitrage_function
                if arbitrage_events_data == -1:
                    flash('No arbitrage events found', category='error')
                # Formats the data returned from the function into something the data base can add
                else:
                    for index, event_data in enumerate(arbitrage_events_data, start=0):
                        ID = arbitrage_events_data[index]['ID']
                        Sports_Key = arbitrage_events_data[index]['Sport Key']
                        Expected_Earning = arbitrage_events_data[index]['Expected Earnings']
                        Arbitrage_Percent = arbitrage_events_data[index]['Total Arbitrage Percentage']
                        # Adds the event information into the database
                        new_event = Event(match_id=ID, sports_key=Sports_Key, earnings=Expected_Earning,
                                          arbitrage_percent=Arbitrage_Percent, user_id=current_user.id)
                        db.session.add(new_event)
                        db.session.commit()
                        event_id = new_event.id
                        # Formats the outcome information into a good form for the database
                        for value in arbitrage_events_data[index]['Best Odds']:
                            Bookmaker = value['Bookmaker']
                            Name = value['Name']
                            Odds = value['Odds']
                            Bet_Amount = value['Bet Amount']
                            # Send each outcome into the database with a event_id to backtrack to its event
                            new_outcome = Outcome(
                                bookmaker=Bookmaker, name=Name, odds=Odds, bet_amount=Bet_Amount, event_id=event_id)
                            db.session.add(new_outcome)
                    db.session.commit()  # Commit after adding all events and outcomes
    return render_template('finder.html', user=current_user)
