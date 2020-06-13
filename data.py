import random
from typing import List, Dict, Tuple

party_tags = {"LIB", "CON", "NDP", "GRN", "BQ", "PP"}
house_parties = {"LIB", "CON", "NDP", "GRN", "BQ"}
province_tags = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"]
territory_tags = ["YT", "NT", "NU"]
region_tags = province_tags + territory_tags
number_of_seats = 338
scale = 5000
turn_length = 7
default_game_state = {"player": None, "parliament": 43, "turn": 1, "date": "2019/10/28"}
game_state = default_game_state.copy()

private_orders_length = 10  # 30 in reality
private_orders_per_turn = 1  # 5ish in reality
government_orders_per_turn = 1

# For logic
government_orders: List[int] = []  # contains ID numbers of bills the government is bringing up
LCPMB: List[int] = []  # contains ID numbers of MPs who are eligible in a randomized order
# LCPMB: List for the Consideration of Private Members' Business
order_of_precedence: List[int] = []  # contains ID numbers of second stage bills MPs wish to progress
imminent_progress: List[int] = []  # contains ID numbers of bills that will have progress attempted at end of turn
votes: List[Dict[str, Dict[str, Dict[int, Dict[str, int]]]]] = []     # contains results of votes
vote_subjects: List[Tuple[int]] = []
# contains subject of votes (ligns up with the container above in terms of indices)

# For UI
page_history = []  # contains page location history
# For game metrics
opinion_polls = {}

poll_types = {"party_support"}
order_paper = [government_orders, LCPMB, order_of_precedence, imminent_progress]

riding_differential = 10
individual_differential = 30
base_radicalism = 30

elect_systems = {"First-Past-the-Post", "Proportional"}

laws = {
    "electsys": 100,
}

policies = {
    "finance": ["income_tax", "sales_tax", "property_tax", "capital_gains", "carbon_tax", "automation_tax",
                "wealth_tax", "resource_tax", "corporate_tax"],
    "public_services": ["health", "edu", "housing"],
    "welfare": ["pensions", "retirement", "ei", "basic_income", "disability_benefits"],
    "economy": ["minwage", "labour_rights", "consumer_rights", "financial_reg"],
    "foreign": ["border", "immigration_quota", "work-visas", "military", "diplomatic_stance", "trade", "foreign_aid"],
    "environment": ["aircare", "watercare", "wastecare", "parks", "ecoprojects"],
    "transport": ["rail", "bus", "roads", "flight", "cars"],
    "justice": ["prisons", "police", "punishment", "legal_aid", "guns", "drugs", "prostitution", "euthanasia",
                "abortion", "lgbt"],
    "electoral": ["voteage", "voteid", "electsys", "electfunds", "maxdon"]
}

all_values = list(policies.keys())

for area in policies.values():
    for policy in area:
        if policy not in laws:
            laws[policy] = 0

policy_attr = {
    "lgbt": {"name": "LGBTQ+ Rights",
             "desc": "Legal standing of lesbian, gay, bisexual, transgendered, and other persons with non-standard "
                     "sexual or gender identities.",
             "effects": "Restrictions on LGBTQ+ rights please some traditionalist conservatives while alienating those"
                        " within the community. On the other hand, positive discrimination is supported by some "
                        "liberals but can be deemed as unfair by the wider population."},
}

party_names = {
    "LIB": "Liberal Party",
    "CON": "Conservative Party",
    "NDP": "New Democratic Party",
    "GRN": "Green Party",
    "BQ": "Bloc Québécois",
    "PP": "People's Party"
}

party_leaders = {
    "LIB": "Justin Trudeau",
    "CON": "Andrew Scheer",
    "NDP": "Jagmeet Singh",
    "GRN": "Elizabeth May",
    "BQ": "Yves-François Blanchet",
    "PP": "Maxime Bernier"
}

# party_seats = {
#     "LIB": 157,
#     "CON": 121,
#     "NDP": 24,
#     "GRN": 3,
#     "BQ": 32,
# }

incumbent = {"LIB"}

party_positions = {
    "LIB": {"finance": 10, "public_services": 10, "welfare": -20, "economy": 20, "foreign": -30, "environment": -20,
            "transport": -40, "justice": -20, "electoral": 50},
    "CON": {"finance": 20, "public_services": 30, "welfare": 30, "economy": 40, "foreign": 20, "environment": 50,
            "transport": 40, "justice": 30, "electoral": 50},
    "NDP": {"finance": -20, "public_services": -40, "welfare": -30, "economy": -20, "foreign": -50, "environment": -50,
            "transport": -50, "justice": -40, "electoral": -50},
    "GRN": {"finance": 10, "public_services": -10, "welfare": -40, "economy": -10, "foreign": -60, "environment": -70,
            "transport": -50, "justice": -20, "electoral": -50},
    "BQ": {"finance": -10, "public_services": -40, "welfare": -20, "economy": -20, "foreign": 10, "environment": -50,
           "transport": -30, "justice": -10, "electoral": -20},
    "PP": {"finance": 50, "public_services": 50, "welfare": 60, "economy": 80, "foreign": 40, "environment": 80,
           "transport": 70, "justice": 40, "electoral": 0}
}
for value in all_values:
    for party in party_tags:
        if value not in party_positions[party]:
            party_positions[party][value] = random.randint(-100, 100)

party_constituencies = {
    "LIB": region_tags,
    "CON": region_tags,
    "NDP": region_tags,
    "GRN": region_tags,
    "BQ": {"QC"},
    "PP": region_tags
}

party_logos = {
    "LIB": "images/lib_logo.png",
    "CON": "images/con_logo.png",
    "NDP": "images/ndp_logo.png",
    "GRN": "images/grn_logo.png",
    "BQ": "images/bq_logo.png",
    "PP": "images/pp_logo.png"
}

colours = {
    "LIB": (215, 25, 32),
    "CON": (26, 71, 130),
    "NDP": (243, 112, 33),
    "GRN": (61, 155, 53),
    "BQ": (51, 178, 204),
    "PP": (78, 81, 128),
    "IND": (200, 200, 200),

    "far-left": (200, 10, 10),
    "left": (255, 0, 0),
    "centre-left": (255, 40, 100),
    "centre": (212, 175, 55),
    "centre-right": (150, 200, 255),
    "right": (0, 0, 255),
    "far-right": (10, 10, 200)
}

names = {
    # Policies page button/policy names
    "finance": "Finance", "income_tax": "Income Tax", "sales_tax": "Sales Tax", "capital_gains": "Capital Gains Tax",
    "carbon_tax": "Carbon Tax", "automation_tax": "Automation Tax", "wealth_tax": "Wealth Tax",
    "resource_tax": "Natural Resource Tax", "corporate_tax": "Corporate Income Tax", "property_tax": "Property Tax",

    "public_services": "Public Services", "health": "Healthcare", "edu": "Education", "housing": "Public Housing",

    "welfare": "Welfare", "pensions": "Pensions", "retirement": "Retirement Age", "ei": "Employment Insurance",
    "basic_income": "Universal Basic Income", "disability_benefits": "Disability Benefits",

    "economy": "Economy", "minwage": "Minimum Wage", "labour_rights": "Labour Rights",
    "consumer_rights": "Consumer Rights", "financial_reg": "Financial Regulation",

    "foreign": "Foreign Affairs", "border": "Border Controls", "immigration_quota": "Immigration Quota",
    "work-visas": "Work-Visas", "military": "Military", "diplomatic_stance": "Diplomatic Stance", "trade": "Tariffs",
    "foreign_aid": "Foreign Aid",

    "environment": "Environment", "aircare": "Air Management", "watercare": "Water Management",
    "wastecare": "Waste Management", "parks": "Park Management", "ecoprojects": "Environmental Projects",

    "transport": "Transport", "rail": "Rail", "bus": "Buses", "roads": "Road Construction",
    "flight": "Air Travel", "cars": "Car Ownership Incentives",

    "justice": "Justice", "prisons": "Prisons", "police": "Police Service", "punishment": "Criminal Sentencing",
    "legal_aid": "Legal Aid", "guns": "Firearm Regulation", "drugs": "Drug Regulation", "prostitution": "Prostitution",
    "euthanasia": "Euthanasia", "abortion": "Abortion", "lgbt": "LGBTQ+ Rights",

    "electoral": "Elections", "voteage": "Voting Age", "voteid": "Voting ID", "electsys": "Electoral System",
    "electfunds": "Public Funding for Elections", "maxdon": "Maximum Contribution",

    # Settings page button names
    "resume": "Resume",
    "save": "Save",
    "load": "Load Save",
    "credits": "Credits",
    "menu": "Return to Menu",
    "quit": "Quit",
    "new game": "New Game",

    # Statistics page button names
    "party_support": "Party Opinion Polls",

    "national": "National",
    # Province Names
    "BC": "British Columbia",
    "AB": "Alberta",
    "SK": "Saskatchewan",
    "MB": "Manitoba",
    "ON": "Ontario",
    "QC": "Québec",
    "NB": "New Brunswick",
    "NS": "Nova Scotia",
    "NL": "Newfoundland and Labrador",
    "PE": "Prince Edward Island",
    "YT": "Yukon Territory",
    "NT": "Northwest Territories",
    "NU": "Nunavut",
}

language_demo = {
    "QC": {"english": 0.076, "french": 0.780, "other": 0.144},
    "ON": {"english": 0.669, "french": 0.037, "other": 0.294},
    "BC": {"english": 0.705, "french": 0.012, "other": 0.283},
    "AB": {"english": 0.747, "french": 0.018, "other": 0.235},
    "SK": {"english": 0.857, "french": 0.017, "other": 0.126},
    "MB": {"english": 0.750, "french": 0.039, "other": 0.211},
    "NS": {"english": 0.925, "french": 0.034, "other": 0.041},
    "NB": {"english": 0.656, "french": 0.319, "other": 0.025},
    "NL": {"english": 0.977, "french": 0.004, "other": 0.019},
    "PE": {"english": 0.938, "french": 0.040, "other": 0.022},
    "YT": {"english": 0.857, "french": 0.037, "other": 0.106},
    "NT": {"english": 0.775, "french": 0.024, "other": 0.201},
    "NU": {"english": 0.268, "french": 0.013, "other": 0.719}
}

region_seats = {
    "QC": 78,
    "ON": 121,
    "BC": 42,
    "AB": 34,
    "SK": 14,
    "MB": 14,
    "NS": 11,
    "NB": 10,
    "NL": 7,
    "PE": 4,
    "YT": 1,
    "NT": 1,
    "NU": 1
}

seat_dist = {
    "QC": {"LIB": 35, "CON": 10, "BQ": 32, "NDP": 1},
    "ON": {"LIB": 79, "CON": 36, "NDP": 6},
    "BC": {"LIB": 12, "CON": 17, "NDP": 11, "GRN": 2},
    "AB": {"CON": 33, "NDP": 1},
    "SK": {"CON": 14},
    "MB": {"LIB": 4, "CON": 7, "NDP": 3},
    "NB": {"LIB": 6, "CON": 3, "GRN": 1},
    "NS": {"LIB": 10, "CON": 1},
    "PE": {"LIB": 4},
    "NL": {"LIB": 6, "NDP": 1},
    "YT": {"LIB": 1},
    "NT": {"LIB": 1},
    "NU": {"NDP": 1}
}

min_seats = {
    "QC": 75,
    "ON": 95,
    "BC": 28,
    "AB": 21,
    "SK": 14,
    "MB": 14,
    "NS": 11,
    "NB": 10,
    "NL": 7,
    "PE": 4,
    "YT": 1,
    "NT": 1,
    "NU": 1
}

senate_seats = {
    "QC": 24,
    "ON": 24,
    "BC": 6,
    "AB": 6,
    "SK": 6,
    "MB": 6,
    "NS": 10,
    "NB": 10,
    "PE": 4,
    "NL": 6,
    "YT": 1,
    "NT": 1,
    "NU": 1
}

population_dist = {
    "QC": 8522800,
    "ON": 14659616,
    "BC": 5105576,
    "AB": 4395586,
    "SK": 1178657,
    "MB": 1373859,
    "NS": 976768,
    "NB": 780021,
    "PE": 157901,
    "NL": 521922,
    "YT": 41022,
    "NT": 44895,
    "NU": 38873
}

# soundtracks for the game
soundtrack = {
    "sound/night-in-venice.mp3": "Night In Venice",
    "sound/lobby-time.mp3": "Lobby Time",
    "sound/george-street-shuffle.mp3": "George Street Shuffle",
    "sound/in-your-arms.mp3": "In Your Arms",
    "sound/opportunity-walks.mp3": "Opportunity Walks",
    "sound/no-good-layabout.mp3": "No Good Layabout",
    "sound/poppers-and-prosecco.mp3": "Poppers and Prosecco"
}

credit = "Directed, designed, and programmed by: Linus Moreau\n\n" \
         "Icons from Icons8 and are available at icons8.com.\n\n" \
         "All music by Kevin Macleod and available at incompetech.com.\n" \
         "Licensed under Creative Commons: By Attribution 3.0 (http://creativecommons.org/licenses/by/3.0/)\n\n" \
         "Written in Python 3.7 with the pygame module using the IDE PyCharm. Freezing into executable done using " \
         "PyInstaller"

# The following are purely for testing purposes

# poll_numbers = {
#     "LIB": {0: 33.7, 1: 33.7, 2: 33.7, 3: 33.8, 4: 33.7, 5: 33.7, 6: 33.7, 7: 32.9, 8: 32.8, 9: 33.0, 10: 32.7},
#     "CON": {0: 34.1, 1: 34.1, 2: 34.1, 3: 33.7, 4: 33.0, 5: 32.6, 6: 32.2, 7: 32.2, 8: 32.0, 9: 31.5, 10: 31.5},
#     "NDP": {0: 16.3, 1: 16.2, 2: 16.2, 3: 16.3, 4: 16.6, 5: 16.9, 6: 17.1, 7: 17.6, 8: 17.6, 9: 17.7, 10: 18.0},
#     "GRN": {0: 6.5, 1: 6.5, 2: 6.5, 3: 6.8, 4: 7.2, 5: 7.5, 6: 7.8, 7: 8.1, 8: 8.3, 9: 8.5, 10: 8.1},
#     "BQ": {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.4, 4: 7.3, 5: 7.2, 6: 7.2, 7: 7.1, 8: 7.0, 9: 7.0, 10: 7.3},
#     "PP": {0: 1.6, 1: 1.6, 2: 1.6, 3: 1.6, 4: 1.7, 5: 1.7, 6: 1.8, 7: 1.8, 8: 1.9, 9: 1.9, 10: 2.0}
# }
#
# new_test = {
#     "LIB": {0: 33.7},
#     "CON": {0: 34.1},
#     "NDP": {0: 16.3},
#     "GRN": {0: 6.5},
#     "BQ": {0: 7.5},
#     "PP": {0: 1.6}
# }
#
# test = {
#     "LIB": {0: 33.7, 1: 33.7, 2: 33.7, 3: 33.8, 4: 33.7, 5: 33.7, 6: 33.7},
#     "CON": {0: 34.1, 1: 34.1, 2: 34.1, 3: 33.7, 4: 33.0, 5: 32.6, 6: 32.2}
# }
#
# growth_figures = {
#     "GDP": {2007: 2.1,
#             2008: 1.0,
#             2009: -2.9,
#             2010: 3.1,
#             2011: 3.1,
#             2012: 1.7,
#             2013: 2.5,
#             2014: 2.4,
#             2015: 1.0,
#             2016: 1.4,
#             2017: 3.0}
# }
