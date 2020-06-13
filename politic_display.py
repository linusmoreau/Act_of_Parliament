

def popular_vote(popular_vote, total_votes, num_voters, scale=1):
    print("Total votes:", total_votes * scale)
    print("Turnout:", round(total_votes / num_voters * 100, 1), "%\n")
    print("Popular vote:")
    for p in popular_vote:
        print(p, round(popular_vote[p] / total_votes * 100, 1), "%")
    print("")


def seat_wins(won_seats, number_of_seats):
    print("Seats:")
    for p in won_seats:
        print(p, won_seats[p], "  \t", round(won_seats[p] / number_of_seats * 100, 1), "%")
    print("")


def seats(parties, number_of_seats):
    print("Seats:")
    for p in parties:
        print(p, parties[p].seats, " \t", round(parties[p].seats / number_of_seats * 100, 1), "%")
    print("")


def members(parties, num_of_voters, scale=1):
    print("Total number of voters: ", num_of_voters * scale)
    print("Party Membership:")
    for p in parties:
        print(p, len(parties[p].members) * scale, " \t", round(len(parties[p].members) / num_of_voters * 100, 1), "%")


def help_menu(commands):
    for command in sorted(commands.keys()):
        print(command + ":", commands[command])


def list_names(names):
    for name in names:
        print(name + "  ", end=" ")
    print("")


def laws(policy_names, laws):
    for policy in policy_names.keys():
        print(policy + ": " + str(laws[policy_names[policy]]))
    print("")


def vote_result(yea, nay, passed):
    print("Yea:", yea, "\t", end=" ")
    print("")
    print("Nay:", nay, "\t", end=" ")
    print("")
    if passed:
        print("Motion Passed")
    else:
        print("Motion Failed")
