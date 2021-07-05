
from flask import Flask, render_template, request, session, redirect, url_for
import numpy as np
import pandas as pd
import random
from random import choices
import sys


#Create app
app = Flask(__name__)
app.secret_key = 'UpdateToSecureKey'


#Initial arrays for the players responses
player_id_array = []
trial_no_array = []
wealth_array =[]
bet_array = []
side_array = []
result_array = []
outcome_array = []


#function that imitates a coin flip (1=heads with probability .55 and 2=tails with probability .45)
def flip():
    # np.random.seed(3621) #Reproducability
    heads_probability = .6
    tails_probability = 1- heads_probability
    value  = [1,2]
    prob = [heads_probability , tails_probability]
    R = choices(value , prob)
    outcome = int(R[-1])
    # print(tails_probability)
    # outcome = random.randint(1,2)
    return(outcome)



def save_to_csv():
    #Open dataframe
    #Create new row for player
    new_row = {'Trail_No': [trial_no_array[-1]],
        'Subject_ID': [player_id_array[-1]],
        'Wealth': [wealth_array[-1]],
        'Bet': [bet_array[-1]],
        'Side': [side_array[-1]],
        'Result': [result_array[-1]],
        'Outcome': [outcome_array[-1]]}



    df = pd.DataFrame(new_row)


    #Append row into the datframe
    df.to_csv('GameData.csv', mode='a', index=False, header=False)



#Render welcome Page
@app.route('/')
def welcome_function():
    return render_template('Index.html')


#Post ID, and randomly assign player to either the full or partial game
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        player_id = request.form['ID'] # input from the html form
        session['player_id'] = player_id
        path = np.random.choice(a = [1, 2], p = [0.5, 0.5])
        print("the path is", path)
        if path == 1:
            return redirect(url_for('partial_game_function'))
        else:
            return redirect(url_for('full_game_function'))
    else:
        return render_template('Index.html')

#######################################################################################
'''
This is the main function for the 'partial' game. It requires players to make a bet on which side of the
coin they think will appear next. A player can bet between 0.01 and all out their wealth per round.
They place an monetary amount and pick a side. If they correctly predict the outcome then we double
their bet and add it to their wealth. If they do not predict correctly we subtract their bet from
their current (ie. they lose their bet)
'''
#######################################################################################


# Set up main partial game page
@app.route('/Partial_Game_Page', methods=['GET'])
def partial_game_function():

    #Initial parameters & counters
    heads_counter = 0
    tails_counter = 0
    start_wealth = 100
    current_wealth = start_wealth
    total_trials = 20
    trial = 1
    multiplier = 2

    #create instance of an outcome (either heads or tails)
    outcome = int(flip())

    #Passing session values
    player_id = session["player_id"] # this is the real passing value
    session["player_id"] = player_id
    session["heads_counter"] = heads_counter
    session["tails_counter"] = tails_counter
    session["current_wealth"] = current_wealth
    session["trial"] = trial
    session["outcome"] = outcome
    session["multiplier"] = multiplier

    #used on the html page

    trial_flask = str(trial)
    current_wealth_flask = str(current_wealth)
    heads_counter_flask = str(heads_counter)
    tails_counter_flask = str(tails_counter)

    return render_template('Partial_Game_Page.html',
        trial_flask = trial_flask,
        current_wealth_flask = current_wealth_flask,
        heads_counter_flask =heads_counter_flask,
        tails_counter_flask = tails_counter_flask)


@app.route('/Partial_Game_Page', methods=['POST'])
def next_partial_game():
    print(session)
    total_trials = 20
    player_id = session["player_id"]
    heads_counter = session["heads_counter"]
    tails_counter = session["tails_counter"]
    current_wealth = session["current_wealth"]
    trial = session["trial"]
    outcome = session["outcome"]
    multiplier = session["multiplier"]
    result = ""
    print(session)
    #Retrieve player input from html form
    amount_bet = request.form.get('amount_bet')
    side_bet = request.form.get('side_bet')
    print(side_bet)

    wrong_input = False
    try:
        amount_bet = round(float(amount_bet), 2)
    except ValueError:
        wrong_input = True

    if wrong_input == True:
        message = "Please try again."
        color_code = 'red'
    elif amount_bet > current_wealth:
        message = "You do not have that much money. Please try again."
        color_code = 'red'
    elif amount_bet < 0.01:
        message = "You can not bet below £0.01. Please try again."
        color_code = 'red'
    else:
        amount_bet = round(float(amount_bet), 2)
        if outcome == 1 and (side_bet =="h"): #win
            heads_counter += 1
            result = (multiplier * amount_bet)
            net_result = result - amount_bet #net gain
            current_wealth = current_wealth + net_result
            message = f"The coin landed HEADS. You won £{net_result} this round." #f-string to display monetary amount won
            color_code = 'green'
        elif outcome == 2 and (side_bet =="h"): #lost
            tails_counter += 1
            result = amount_bet
            current_wealth = current_wealth - result
            message = f"The coin landed TAILS. You lost £{result} this round."
            color_code = 'red'
        elif outcome == 1 and (side_bet =="t"): #lost
            heads_counter += 1
            result = amount_bet
            current_wealth = current_wealth - result
            message = f"The coin landed HEADS. You lost £{result} this round."
            color_code = 'red'
        else: #win
            tails_counter += 1
            result = (multiplier * amount_bet)
            net_result = result - amount_bet #net gain
            current_wealth = current_wealth + net_result
            message = f"The coin landed TAILS. You won £{net_result} this round."
            color_code = 'green'



    #Append arrays for the round
    if result:
        try:
            player_id_array.append(player_id)
            trial_no_array.append(trial)
            wealth_array.append(current_wealth)
            bet_array.append(amount_bet)
            if side_bet == "t":
                side_array.append("Tail")
            else:
                side_array.append("Head")
            if outcome == 1:
                outcome_array.append("Head")
            else:
                outcome_array.append("Tail")
            result_array.append(result)
            save_to_csv()

            #start new round
            trial = trial + 1
        except:
            print("problem")

    #new outcome
    outcome = int(flip())
    print("outcome is ", outcome)
                ##Passing session values
    session["player_id"] = player_id
    session["heads_counter"] = heads_counter
    session["tails_counter"] = tails_counter
    session["current_wealth"] = current_wealth
    session["trial"] = trial
    session["outcome"] = outcome
    session["multiplier"] = multiplier

    #If the game has gone through all the trials or a players becomes bankrupt, redirect player 'End.html' page
    if trial > total_trials or current_wealth < 0.02:
        return render_template('End_Page.html')

    #for html
    trial_flask = str(trial)
    current_wealth_flask = str(current_wealth)
    heads_counter_flask = str(heads_counter)
    tails_counter_flask = str(tails_counter)
    message_flask = str(message)

    #Render template
    return render_template('Partial_Game_Page.html',
        trial_flask = trial_flask,
        current_wealth_flask = current_wealth_flask,
        heads_counter_flask =heads_counter_flask,
        tails_counter_flask = tails_counter_flask,
        color_code = color_code,
        message_flask = message_flask)


#######################################################################################
'''
This is the main function for the 'full' game. The players are required to bet all of their wealth in
each round. The net gain for each round (see below for more details) is then added to their wealth.
'''
#######################################################################################
# Set up main full game page
@app.route("/Full_Game_Page/")
def full_game_function():
    #Initial parameters & counters
    heads_counter = 0
    tails_counter = 0
    start_wealth = 100
    current_wealth = start_wealth
    total_trials = 20
    trial = 1
    multiplier = 2

    #create instance of an outcome (either heads or tails)
    outcome = int(flip())

    #Passing session values
    player_id = session["player_id"]
    session["player_id"] = player_id
    session["heads_counter"] = heads_counter
    session["tails_counter"] = tails_counter
    session["current_wealth"] = current_wealth
    session["trial"] = trial
    session["outcome"] = outcome
    session["multiplier"] = multiplier
    print("done")
    print("session")
    #used on the html page
    trial_flask = str(trial)
    current_wealth_flask = str(current_wealth)
    heads_counter_flask = str(heads_counter)
    tails_counter_flask = str(tails_counter)

    return render_template('Full_Game_Page.html',
        trial_flask = trial_flask,
        current_wealth_flask = current_wealth_flask,
        heads_counter_flask =heads_counter_flask,
        tails_counter_flask = tails_counter_flask)


@app.route("/Full_Game_Page", methods=['POST'])
def next_full_game():
    print(session)
    total_trials = 20
    player_id = session["player_id"]
    heads_counter = session["heads_counter"]
    tails_counter = session["tails_counter"]
    current_wealth = session["current_wealth"]
    trial = session["trial"]
    outcome = session["outcome"]
    multiplier = session["multiplier"]
    print("outcome before " , outcome)
    result=""

    #Retrieve player input from html form
    amount_bet = request.form.get('amount_bet') #player entered amount
    amount_bet1 = request.form.get('AutoAmountBet') #automatically updated field
    amount_bet = round(float(amount_bet), 2)
    amount_bet1 = round(float(amount_bet1), 2)
    print(amount_bet)
    print(amount_bet1)
    side_bet = request.form.get('side_bet') #player entered side
    side_bet1 = request.form.get('AutoSideBet') #automatically updated field

    print("side_bet is " , side_bet)
    #result is the net gain for the round
    #result = (the amount bet on winning side * multiplier)-the amount bet on the losing side
    if amount_bet > current_wealth:
        message = "You do not have that much money. Please try again."
        color_code = 'red'
    elif outcome == 1 and (side_bet =="heads"):
        print("done")
        heads_counter += 1
        result = (multiplier * amount_bet) #amount_bet = on heads & amount_bet1 = on tails
        net_result = result - (amount_bet + amount_bet1) #net result for the round
        abs_net = round(abs(net_result), 2) #absolute net gain/loss (for flask html variables) round to 2 decimal places
        current_wealth = current_wealth + net_result
        if net_result > 0:
            message = f"The coin landed HEADS. You won £{abs_net} this round." #f-string to display monetary amount won
            color_code = 'green'
        else:
            message = f"The coin landed HEADS. You lost £{abs_net} this round." #f-string to display monetary amount won
            color_code = 'red'
    elif outcome == 2 and (side_bet =="heads"):
        tails_counter += 1
        result = (multiplier * amount_bet1) #amount_bet = on heads & amount_bet1 = on tails
        net_result = result - (amount_bet1+amount_bet) #net gain for round
        abs_net = round(abs(net_result), 2)
        current_wealth = current_wealth + net_result
        if net_result > 0:
            message = f"The coin landed TAILS. You won £{abs_net} this round."
            color_code = 'green'
        else:
            message = f"The coin landed TAILS. You lost £{abs_net} this round."
            color_code = 'red'
    elif outcome == 1 and (side_bet =="tails"):
        heads_counter += 1
        result = (multiplier * amount_bet1) #amount_bet = on tails & amount_bet1 = on heads
        net_result = result - (amount_bet1 + amount_bet)
        abs_net = round(abs(net_result), 2)
        current_wealth = current_wealth + net_result
        if net_result > 0:
            message = f"The coin landed HEADS. You won £{abs_net} this round." #f-string to display monetary amount won
            color_code = 'green'
        else:
            message = f"The coin landed HEADS. You lost £{abs_net} this round." #f-string to display monetary amount won
            color_code = 'red'
    else:
        tails_counter += 1
        result = (multiplier * amount_bet) #amount_bet = on tails & amount_bet1 = on heads
        net_result = result - (amount_bet+amount_bet1)
        abs_net = round(abs(net_result), 2)
        current_wealth = current_wealth + net_result
        if net_result > 0:
            message = f"The coin landed TAILS. You won £{abs_net} this round."
            color_code = 'green'
        else:
            message = f"The coin landed TAILS. You lost £{abs_net} this round."
            color_code = 'red'

    #Append arrays for the round
    if result:
        player_id_array.append(player_id)
        trial_no_array.append(trial)
        wealth_array.append(current_wealth)
        bet_array.append(amount_bet)
        side_array.append(side_bet)
        if outcome == 1:
            outcome_array.append("Head")
        else:
            outcome_array.append("Tail")
        # outcome_array.append(outcome)
        result_array.append(result)
        save_to_csv()
        print(player_id_array)
        #start new round
        trial = trial + 1
        print("done")
    else:
        print("problem")

         #new outcome
    outcome = int(flip())
    print("outcome is " , outcome)
    #Passing ID session values
    session["player_id"] = player_id
    session["heads_counter"] = heads_counter
    session["tails_counter"] = tails_counter
    session["current_wealth"] = current_wealth
    session["trial"] = trial
    session["outcome"] = outcome
    session["multiplier"] = multiplier

    #If the game has gone through all the trials redirect player 'End.html' page
    if trial > total_trials:
        return redirect("End_Page.html")

    #for html
    trial_flask = str(trial)
    current_wealth_flask = str(current_wealth)
    heads_counter_flask = str(heads_counter)
    tails_counter_flask = str(tails_counter)
    message_flask = str(message)

    #Render template
    return render_template('Full_Game_Page.html',
        trial_flask = trial_flask,
        current_wealth_flask = current_wealth_flask,
        heads_counter_flask =heads_counter_flask,
        tails_counter_flask = tails_counter_flask,
        color_code = color_code,
        message_flask = message_flask
        )


#######################################################################################


#Run app
if __name__ == "__main__":
    app.run(host='0.0.0.0')
