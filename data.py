import json
import csv
import date_kit
from typing import Dict, List, Tuple


credit: str
order_paper: List
poll_types: List
settings: Dict
game_title: str
soundtrack: Dict
containers: List
regions: Dict
parties: Dict
all_values: List
game_state: Dict
votes: List[Dict[str, Dict[str, Dict[int, Dict[str, int]]]]]
vote_subjects: List[Tuple[int]]
opinion_polls: Dict
policies: Dict
colours: Dict
imminent_progress: List[int]
order_of_precedence: List[int]
government_orders: List[int]
lcpmb: List[int]
default_game_state: Dict


def init():
    global credit, order_paper, poll_types, settings, game_title, soundtrack, containers, regions, parties, \
        all_values, game_state, votes, vote_subjects, opinion_polls, policies, colours, imminent_progress, \
        order_of_precedence, government_orders, lcpmb, default_game_state

    government_orders = []  # contains ID numbers of bills the government is bringing up

    lcpmb = []  # contains ID numbers of MPs who are eligible in a randomized order
    # LCPMB: List for the Consideration of Private Members' Business

    order_of_precedence = []  # contains ID numbers of second stage bills MPs wish to progress

    imminent_progress = []  # contains ID numbers of bills that will have progress attempted at end of turn

    votes = []     # contains results of votes

    vote_subjects = []  # contains subject of votes (ligns up with the container above in terms of indices)

    opinion_polls = {}

    order_paper = [government_orders, lcpmb, order_of_precedence, imminent_progress]

    colours = {}
    credit = "Directed, designed, and programmed by: </-c (212,175,55)/>Linus Moreau</-c d/>.\n\n" \
             "Icons are from </-c (212,175,55)/>Icons8</-c d/> and are available at " \
             "</-c (150,150,255) -u -h/>icons8.com</-c d -u -h/>.\n\n" \
             "All music is by </-c (212,175,55)/>Kevin Macleod</-c d/>.\n" \
             "Licensed under Creative Commons by Attribution 3.0 " \
             "(</-c (150,150,255) -u -h/>creativecommons.org/licenses/by/3.0/</-c d -u -h/>)\n" \
             "Available at </-c (150,150,255) -u -h/>incompetech.com</-c d -u -h/>.\n\n" \
             "Written in Python 3.7 with the pygame module using the IDE PyCharm. Freezing into executable done " \
             "using PyInstaller."

    poll_types = ["party_support"]

    try:
        f = open('settings.json', 'r')
    except FileNotFoundError:
        raise FileNotFoundError('Could not find settings.json file.')
    else:
        settings = json.load(f)
        f.close()

    try:
        f = open('data/misc.json')
    except FileNotFoundError:
        raise FileNotFoundError('Could not find misc.json in data folder.')
    else:
        doc = json.load(f)
        f.close()
        game_title = doc["game_title"]
        date = date_kit.Date(text=doc['date'])
        default_game_state = {"player": None, "parliament": doc["parliament"], "turn": 1, "date": date}
        game_state = default_game_state.copy()
        soundtrack = doc["soundtrack"]

        containers = [votes, vote_subjects, game_state, opinion_polls, government_orders, lcpmb,
                      order_of_precedence, imminent_progress]

    try:
        f = open('data/regions.json')
    except FileNotFoundError:
        raise FileNotFoundError('Could not find regions.json in data folder.')
    else:
        regions = json.load(f)
        f.close()

    try:
        f = open('data/parties.json')
    except FileNotFoundError:
        raise FileNotFoundError('Could not find parties.json in data folder.')
    else:
        parties = json.load(f)
        f.close()

    try:
        f = open('data/policies.json')
    except FileNotFoundError:
        raise FileNotFoundError('Could not find policies.json in data folder.')
    else:
        doc = json.load(f)
        f.close()

        new_colours = {}
        for colour in doc['colours']:
            new_colours[colour] = tuple(doc['colours'][colour])
        colours.update(new_colours)

        policies = doc['policies']
        all_values = list(policies.keys())

    try:
        with open('data/ridings.csv', 'r') as f:
            doc = csv.reader(f)
            for row in doc:
                print(row)
    except FileNotFoundError:
        raise FileNotFoundError('Could not find ridings.csv in data folder')
