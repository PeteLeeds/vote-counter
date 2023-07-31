import json
import re
import functools

tiebreak_list = {}

def get_multiline_input():
    items = []
    while True:
        line = input()
        if (line.upper() == 'DONE'):
            return items
        items.append(line)

def get_first_number(string):
    number_string = ""
    number_begun = False
    for i in range(len(string)):
        try:
            char = string[i]
            int(char)
            number_string += char
            number_begun = True
        except:
            if (number_begun):
                return int (number_string)
    if (number_string == ''):
        return 0
    return int(number_string)

def print_array_with_numbers(array):
    for i in range(len(array)):
        print(f"{i + 1} - {array[i]}")

def validate_int_response(response, min, max):
    while True:
        try:
            if (int(response) >= min and int(response) <= max):
                return int(response)
            else:
                raise Exception()
        except:
            response = input(f"Incorrect input. Please enter a number between {min} and {max}: ")
            

def get_key(vote, keys):
    likely_keys = []
    potential_keys = []
    for key in keys:
        if key.upper() in vote.upper() or vote.upper() in key.upper():
            # Definite match
            return key
        key_parts = re.split('-|–', key)
        key_added = False
        for part in key_parts:
            if key_added:
                continue
            if (len(part) <= 1):
                continue
            if (part.upper() in vote.upper()):
                likely_keys.append(key)
                key_added = True
                continue
    if len(likely_keys) == 1:
        return likely_keys[0]
    if len(likely_keys) > 1:
        return ask_for_clarification(vote, likely_keys, keys)
    else:
        # Need to dig further to find the correct answer
        vote_parts = re.split('-|–| |:|;|',vote)
        for key in keys:
            for part in vote_parts:
                if part.upper() in key.upper():
                    potential_keys.append(key)
                    break
        return ask_for_clarification(vote, potential_keys, keys)


def ask_for_clarification(vote, potential_keys, keys):
    print("There is some ambiguity regarding the following vote:\n"
            + vote
            + "\nPlease select the entry this corresponds to:")
    print_array_with_numbers(potential_keys)
    print("-1 - none of the above")
    response = input("Please select: ")
    if response != "-1":
        int_response = validate_int_response(response, 1, len(potential_keys))
        return potential_keys[int_response - 1]
    print("Please select which entry this relates to: ")
    print_array_with_numbers(keys)
    response = input("Please select: ")
    int_response = validate_int_response(response, 1, len(keys))
    return keys[int_response - 1]

def add_to_tiebreak_list(name, score, count):
    if not name in tiebreak_list:
        tiebreak_list[name] = [[score, count]]
    elif not [score, count] in tiebreak_list[name]:
        tiebreak_list[name].append([score, count])


def sort_scores(x, y):
    if (x[1]['points'] != y[1]['points']):
        return x[1]['points'] - y[1]['points']
    score_set = set(x[1]['votes'] + y[1]['votes'])
    sorted_score_set = sorted(score_set, reverse=True)
    for score in sorted_score_set:
        x_appearances = x[1]['votes'].count(score)
        y_appearances = y[1]['votes'].count(score)
        add_to_tiebreak_list(x[0], score, x_appearances)
        add_to_tiebreak_list(y[0], score, y_appearances)
        if (x_appearances != y_appearances):
            return x_appearances - y_appearances
    return 0

def get_tiebreak_string(item):
    if not item in tiebreak_list:
        return ''
    sorted_tiebreak_list = sorted(tiebreak_list[item], key=lambda x:x[0])
    sorted_tiebreak_list.reverse()
    tiebreak_string = ''
    for val in sorted_tiebreak_list:
        if len(tiebreak_string) != 0:
            tiebreak_string += ', '
        tiebreak_string += f"{val[1]} x {val[0]}"
    return f"({tiebreak_string})"


# Initialise file
try:
    score_file = open("points.json", "r")
    raw_data = score_file.readlines()
    current_json_state = json.loads(raw_data[0])
    score_file.close()
except:
    score_file = open("points.json", "w")
    score_file.close()
    current_json_state = {}

response = 0

while (response != '-1'):
    print('Point Counter')
    current_keys = list(current_json_state.keys())
    print("Press 1 to add scores \nPress 2 to view scores\nOr press -1 to exit")
    response = input("Please select: ")
    if (response == "1"):
        for i in range(len(current_json_state)):
            print(f'Enter {i + 1} to add scores to {current_keys[i]}')
        print('Enter 0 to enter a new series to start adding scores to' + 
                '\nOr enter -1 to go back')
        count_response = input('Please select: ')
        if (count_response == '0'):
            current_series = input('Please enter the name of the series you would like to count points for: ')
            print('Please enter the items you would like to include a count for' + 
                                    '\nEnter each item on a new line, and type \'done\' once complete\n')
            series_items = get_multiline_input()
            current_series_json = {}
            for item in series_items:
                current_series_json[item] = {
                    'points': 0,
                    'votes': []
                }
            current_json_state[current_series] = current_series_json
            score_file = open("points.json", "w")
            score_file.write(json.dumps(current_json_state))
            score_file.close()
        elif count_response != '-1':
            try:
                current_series = current_keys[int(count_response) - 1]
                current_series_json = current_json_state[current_series]
            except:
                input('Invalid selection. Press enter to continue')
        else:
            continue
        keys = list(current_json_state[current_series].keys())
        print('Please copy and paste the first set of votes')
        votes = get_multiline_input()
        for vote in votes:
            score = get_first_number(vote)
            if (score == 0):
                continue
            item = get_key(vote, keys)
            current_series_json[item]['points'] += score
            current_series_json[item]['votes'].append(score)
        score_file = open("points.json", "w")
        score_file.write(json.dumps(current_json_state))
        score_file.close()
    elif (response == "2"):
        for i in range(len(current_json_state)):
            print(f'Enter {i + 1} to view scores in {current_keys[i]}')
        print('Or enter -1 to go back')
        view_response = input('Please select: ')
        if view_response != '-1':
            try:
                current_series = current_keys[int(view_response) - 1]
                current_series_json = current_json_state[current_series]
            except:
                input('Invalid selection. Press enter to continue')
            tiebreak_list = {}
            sorted_series = sorted(current_series_json.items(), key=(functools.cmp_to_key(sort_scores)))
            sorted_series.reverse()
            index = 1
            for item in sorted_series:
                print(f"{index}: {item[0]} - {item[1]['points']} points {get_tiebreak_string(item[0])}")
                index += 1
            input('Press enter to continue')

    