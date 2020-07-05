from data import *
import CAN_names as Names
import json
import os
import toolkit
import date_translator
from typing import Dict


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, (Person, Party, ParliamentMember, Riding, Region, Bill)):
            return obj.json_dump()
        else:
            return super().default(obj)


def make_save(f_name):
    save_doc = {"parties": [parties[p] for p in parties],
                "regions": [regions[r] for r in regions],
                "ridings": [ridings[r] for r in ridings],
                "persons": [persons[p] for p in persons],
                "bills": [bills[b] for b in bills],
                "votes": votes,
                "vote_subjects": vote_subjects,
                "game_state": game_state,
                "laws": laws,
                "opinion_polls": opinion_polls,
                "order_paper": order_paper}
    f = open("saves/" + f_name, "w+")
    f.write(json.dumps(save_doc, cls=Encoder, separators=(',', ':')))
    f.close()


def load_save(f_name):
    try:
        f = open("saves/" + f_name, "r")
    except FileNotFoundError:
        print("Could not find file")
        return
    else:
        clear_data()
        load_doc = json.load(f)
        f.close()
        for attr, val in load_doc["game_state"].items():
            game_state[attr] = val
        for obj in load_doc["parties"]:
            Party(**obj)
        for obj in load_doc["regions"]:
            Region(loaded=True, **obj)
        for obj in load_doc["ridings"]:
            Riding(loaded=True, **obj)
        for obj in load_doc["bills"]:
            Bill(**obj)
        for obj in load_doc["persons"]:
            obj_type = obj.pop("type")
            if obj_type == "ParliamentMember":
                ParliamentMember(**obj)
            else:
                Person(**obj)
        for vote in load_doc["votes"]:
            votes.append(reformat_data(vote))
        vote_subjects.extend(load_doc["vote_subjects"])
        for key, value in load_doc["opinion_polls"].items():
            opinion_polls[key] = reformat_data(value)
        for i, construct in enumerate(load_doc["order_paper"]):
            order_paper[i].extend(construct)


def reformat_data(data):
    if type(data).__name__ == "dict" and len(data) > 0:
        new_data = {}
        for key in data:
            try:
                int(key)
            except ValueError:
                for k, v in data.items():
                    new_data[k] = reformat_data(v)
                return new_data
        for key, value in data.items():
            new_data[int(key)] = reformat_data(value)
        return new_data
    else:
        return data


def delete_save(f_name):
    os.remove("saves/" + f_name)


def clear_data():
    Person.id_num = 0
    Bill.id_num = 0
    Bill.nums = {'gov': 1, 'member': 201, 'private': 1001}
    for dat in all_data:
        dat.clear()


class Person:
    id_num = 0

    def __init__(self, region, riding, values, values_importance, radicalism, party=None, name=None, gender=None,
                 age=None, background=None, language=None, supports=None, best_opinion=None, voted=False,
                 id_num=None, titles=None, birthdate=None):
        if id_num is None:
            self.id_num = Person.id_num
            Person.id_num += 1
        else:
            self.id_num = id_num
            if self.id_num > Person.id_num:
                Person.id_num = self.id_num + 1
            else:
                Person.id_num += 1
        self.region = region
        self.riding = riding
        self.values = values
        self.values_importance = values_importance

        self.radicalism = radicalism
        if type(party).__name__ == "str":
            self.party = parties[party]
        else:
            self.party = party

        if titles is None:
            self.titles = []

        self.supports = supports
        self.best_opinion = best_opinion
        self.voted = voted

        # todo this age generator will need a rework at some point to include population growth and underaged people
        if birthdate is None:
            if age is None:
                while True:
                    if random.randrange(10) > 5:        # 40% chance
                        age = round(random.gauss(70, 10))
                    else:
                        age = random.randrange(18, 60)
                    birthdate = date_translator.random_date(int(game_state["date"].split('-')[0]) - age)
                    age = date_translator.age(birthdate, game_state["date"])
                    if age >= 18:
                        break
        else:
            age = date_translator.age(birthdate, game_state["date"])
        self.birthdate = birthdate
        self.age = age

        if gender is None:
            self.gender = random.choice(["male", "female"])
        else:
            self.gender = gender

        if background is None or language is None:
            rand = random.random()
            if rand < language_demo[self.region]["other"]:
                self.background = "other"
                rand = rand / language_demo[self.region]["other"]
                if rand < language_demo[self.region]["french"]:
                    self.language = "french"
                else:
                    self.language = "english"
            else:
                rand += language_demo[self.region]["other"]
                if rand < language_demo[self.region]["french"]:
                    self.background = "french"
                    self.language = "french"
                else:
                    self.background = "english"
                    self.language = "english"
        else:
            self.background = background
            self.language = language

        if name is None:
            self.name = Names.full_name(self.gender, self.background, self.language)
        else:
            self.name = name

        ridings[self.riding].persons.append(self.id_num)
        persons[self.id_num] = self

    def json_dump(self):
        attr = self.__dict__.copy()
        attr["type"] = type(self).__name__
        if attr["party"] is not None:
            attr["party"] = attr["party"].tag
        return attr

    def do_turn(self):
        new_age = date_translator.age(self.birthdate, game_state["date"])
        self.age = new_age

    def consider_parties(self, ballot):  # ballot is the tags (strings) of what parties are available in the region
        opinion_of_parties = {}
        for p in ballot:
            party_opinion = 0
            for issue in self.values:
                policy_opinion = -abs(self.values[issue] - parties[p].values[issue]) * self.values_importance[issue]
                party_opinion += policy_opinion
            party_opinion = party_opinion / len(self.values)
            opinion_of_parties[p] = party_opinion
        best_party = toolkit.largest_in_dictionary(opinion_of_parties)
        self.supports = best_party  # party that is supported (string)
        self.best_opinion = opinion_of_parties[best_party]  # value from -200 to 0
        # if self.best_opinion > - random.random() / 50 and self.party is None:
        #     self.join_party()
        # elif self.best_opinion < - (1 + random.random()) / 50 and self.party is not None:
        #   self.leave_party()

    def join_party(self):
        self.party = parties[self.supports]
        self.party.members.append(self)

    def leave_party(self):
        self.party.members.remove(self)
        self.party = None

    def election_vote(self, ballot):
        self.consider_parties(ballot)
        if self.best_opinion > -random.random() * 20:
            self.voted = True
        else:
            self.voted = False
        return self.voted


class ParliamentMember(Person):

    def __init__(self, region, riding, values, values_importance, radicalism, party, party_leader=False, name=None,
                 gender=None, birthdate=None, background=None, language=None, seniority=None, player=False,
                 bbd=None, bbp=None, bwfc=None, **kwargs):
        if birthdate is None:
            while True:
                age = round(random.gauss(50, 10))
                birthdate = date_translator.random_date(int(game_state["date"].split('-')[0]) - age)
                age = date_translator.age(birthdate, game_state["date"])
                if age >= 18:
                    break
        else:
            age = date_translator.age(birthdate, game_state["date"])
        kwargs["age"] = age
        super().__init__(region, riding, values, values_importance, radicalism, party, name=name, gender=gender,
                         birthdate=birthdate, background=background, language=language, **kwargs)
        self.player = player
        self.party_leader = party_leader
        self.party.seats += 1
        self.party.members.append(self)
        self.party.politicians.append(self)

        self.bbd = bbd  # bbd: Bill Being Drafted (id_num)
        self.bbp = bbp  # bbp: Bill Being Pushed (id_num)
        if bwfc is None:   # bwfc: Bills Waiting For Consideration (id_nums)
            self.bwfc = []
        else:
            self.bwfc = bwfc
        if seniority is None:
            self.seniority = random.random()
        else:
            self.seniority = seniority
        ridings[self.riding].mp.append(self.id_num)
        politicians[self.id_num] = self

    def do_turn(self):
        if self.bbd is not None:
            bills[self.bbd].progress()
        if not self.player:
            if self.bbp is not None:
                bill = bills[self.bbp]
                bill.advance()
            if self.bbp is None:
                pass
                # todo MP chooses new bill to push
        super().do_turn()

    def select_bwfc(self):
        return random.choice(self.bwfc)

    def first_vote(self, bill):
        factors = {}
        party_pressure = 0
        if bill.id_num in self.party.bill_support and self.party.bill_support[bill.id_num] is not None:
            if self.party.bill_support[bill.id_num]:
                party_pressure = (100 - self.radicalism) * self.party.discipline
            else:
                party_pressure = -(100 - self.radicalism) * self.party.discipline
        factors["Party Pressure"] = party_pressure
        for provision in bill.provisions:
            for issue, policy_list in policies.items():
                if provision in policy_list:
                    belief = self.values[issue]
                    belief_import = self.values_importance[issue]
                    break
            else:
                belief = 0
                belief_import = 0
            current_difference = abs(belief - laws[provision])
            proposed_difference = abs(belief - bill.provisions[provision])
            opinion = round((current_difference - proposed_difference) * belief_import)
            if opinion > 0:
                key = "Right direction"
            elif opinion < 0:
                if laws[provision] < belief < bill.provisions[provision] or \
                        laws[provision] > belief > bill.provisions[provision]:
                    key = "Goes too far"
                else:
                    key = "Wrong direction"
            else:
                key = "Indifferent"
            key = names[provision] + " (" + key + ")"
            factors[key] = opinion
        return factors

    def final_vote(self, bill):
        return self.first_vote(bill)
        # factors = {}
        # party_pressure = 0
        # if self.party.bill_support is not None:
        #     if self.party.bill_support:
        #         party_pressure = (100 - self.radicalism) * self.party.discipline
        #     else:
        #         party_pressure = -(100 - self.radicalism) * self.party.discipline
        # factors["Party Pressure"] = party_pressure
        # for provision in bill.provisions:
        #     for issue, policy_list in policies.items():
        #         if provision in policy_list:
        #             belief = self.values[issue]
        #             break
        #     else:
        #         belief = 0
        #     current_difference = abs(belief - laws[provision])
        #     proposed_difference = abs(belief - bill.provisions[provision])
        #     opinion = round((current_difference - proposed_difference) * self.values_importance[provision])
        #     if opinion > 0:
        #         key = "Right direction"
        #     elif opinion < 0:
        #         key = "Wrong direction"
        #     else:
        #         key = "Indifferent"
        #     key = names[provision] + " (" + key + ")"
        #     factors[key] = opinion
        # return factors


class Party:

    def __init__(self, tag, name, on_ballot, values, **kwargs):
        self.popular_vote = None
        self.tag = tag
        self.seats = 0
        self.name = name
        # self.incumbent = incumbent
        self.values = values
        if "values_importance" not in kwargs:
            self.values_importance = {}
            for value in self.values:
                self.values_importance[value] = round(random.random(), 1)
        else:
            self.values_importance = kwargs["values_importance"]
        self.on_ballot = on_ballot
        if "discipline" not in kwargs:
            self.discipline = 0
        else:
            self.discipline = kwargs["discipline"]
        if "bill_support" not in kwargs:
            self.bill_support = {}
        else:
            self.bill_support = kwargs["bill_support"]
        self.politicians = []
        self.members = []
        # self.leader = None
        parties[self.tag] = self

    def json_dump(self):
        attr = self.__dict__.copy()
        attr["type"] = type(self).__name__
        del attr["politicians"]
        del attr["members"]
        return attr

    # def first_vote(self, issue, proposed_law):
    #     self.leader.first_vote(issue, proposed_law)
    #     self.bill_support = self.leader.bill_support
    #
    # def last_vote(self, issue, proposed_law):
    #     self.leader.last_vote(issue, proposed_law)
    #     self.bill_support = self.leader.bill_support


class Region:

    def __init__(self, tag, num_of_districts, population, seat_distribution=None, loaded=False, **kwargs):
        self.tag = tag
        self.num_of_districts = num_of_districts
        self.population = int(population)
        self.simulated = int(population / scale)
        self.ballot = []
        for p in parties:
            if self.tag in parties[p].on_ballot:
                self.ballot.append(p)

        self.ridings = {}
        self.total_votes = 0
        self.vote_totals = {}
        self.riding_wins = {}

        regions[self.tag] = self

        if loaded:
            self.vote_history = kwargs["vote_history"]
        else:
            self.vote_history = {}
            self.gen_ridings(seat_distribution)

    def json_dump(self):
        attr = self.__dict__.copy()
        attr["type"] = type(self).__name__
        del attr["ridings"]
        return attr

    def gen_ridings(self, seat_distribution):
        i = 1
        party_held_seats = []
        for party in seat_distribution:
            for s in range(seat_distribution[party]):
                party_held_seats.append(party)
        random.shuffle(party_held_seats)
        for party in party_held_seats:
            Riding(self.tag, self.tag + '-' + str(i), int(self.simulated / self.num_of_districts), self.ballot, party)
            i += 1

    def election(self):
        self.total_votes = 0
        self.vote_totals = {}
        self.riding_wins = {}
        for p in self.ballot:
            self.vote_totals[p] = 0
            self.riding_wins[p] = 0

        for riding in self.ridings:
            riding_total, winner = self.ridings[riding].election()
            self.riding_wins[winner] += 1
            for p in riding_total:
                self.vote_totals[p] += riding_total[p]

        for p in self.ballot:
            self.total_votes += self.vote_totals[p]

        return self.vote_totals, self.riding_wins

    # def display_results(self):
    #     display.popular_vote(self.vote_totals, self.total_votes, self.simulated, scale)
    #     display.seat_wins(self.riding_wins, self.num_of_districts)


class Riding:

    def __init__(self, region, tag, population, ballot, incumbent, loaded=False, **kwargs):
        self.region = region
        self.tag = tag
        self.ballot = ballot
        self.population = population
        self.incumbent = incumbent

        self.persons = []
        self.mp = []
        self.winner = None
        self.vote_totals = {}

        regions[self.region].ridings[self.tag] = self
        ridings[self.tag] = self

        if loaded:
            self.values = kwargs["values"]
            self.vote_history = kwargs["vote_history"]
        else:
            self.values = parties[self.incumbent].values.copy()
            self.vote_history = {}
            self.gen_population()
            if laws["electsys"] == 100:
                self.set_mp()

    def json_dump(self):
        attr = self.__dict__.copy()
        attr["type"] = type(self).__name__
        del attr["persons"]
        del attr["mp"]
        return attr

    def gen_population(self):
        d = individual_differential
        for i in range(self.population):
            values, values_importance, radicalism = self.gen_beliefs(self.values, d)
            Person(self.region, self.tag, values, values_importance, radicalism)

    def set_mp(self):
        d = 10
        values, values_importance, radicalism = self.gen_beliefs(parties[self.incumbent].values, d)
        ParliamentMember(self.region, self.tag, values, values_importance, radicalism, parties[self.incumbent])

    @staticmethod
    def gen_beliefs(base, d):
        values = {}
        for value in all_values:
            pos = round(random.gauss(base[value], d))
            if pos > 100:
                pos = 100
            elif pos < -100:
                pos = -100
            values[value] = pos
        values_importance = {}
        for value in values:
            values_importance[value] = round(random.random(), 1)
        radicalism = base_radicalism
        return values, values_importance, radicalism

    def election(self):
        self.vote_totals = {}
        for p in self.ballot:
            self.vote_totals[p] = 0

        for v in self.persons:
            v = persons[v]
            if v.election_vote(self.ballot):
                self.vote_totals[v.supports] += 1

        self.winner = toolkit.largest_in_dictionary(self.vote_totals)
        self.incumbent = self.winner
        return self.vote_totals, self.winner


class Bill:
    id_num = 0
    nums = {"gov": 1, "member": 201, "private": 1001}
    cost_multiplier = 1
    stages = ["Drafting", "First Reading", "Second Reading", "Committee", "Third Reading", "Senate", "Royal Assent",
              "Passed"]

    '''provisions in {subject: position, subject: position, etc.} format'''

    def __init__(self, sponsor, provisions, kind, parliament=game_state["parliament"], name=None, **kwargs):
        self.sponsor = sponsor
        self.provisions = provisions
        self.kind = kind
        self.parliament = parliament
        self.main_provision = kwargs.get("main_provision", list(self.provisions.keys())[0])
        self.draft_cost = kwargs.get("draft_cost", self.det_draft_cost())
        self.draft_progress = kwargs.get("draft_progress", 0)
        self.stage = kwargs.get("stage", 0)
        self.num = kwargs.get("num", None)
        self.dead = False

        if "id_num" not in kwargs:
            self.id_num = Bill.id_num
            Bill.id_num += 1
        else:
            self.id_num = kwargs.pop("id_num")
            if self.id_num >= Bill.id_num:
                Bill.id_num = self.id_num + 1

        if "num" not in kwargs:
            self.num = None
        else:
            self.num = kwargs["num"]
            if self.num is not None:
                if self.parliament == parliament and self.num >= Bill.nums[self.kind]:
                    Bill.nums[self.kind] = self.num + 1

        if name is None:
            self.name = names[self.main_provision] + " Act"
            self.find_duplicates(1)
        else:
            self.name = name

        bills[self.id_num] = self

    def find_duplicates(self, num):
        for id_num in bills:
            bill = bills[id_num]
            if bill != self and bill.name == self.name and self.parliament == bill.parliament:
                num += 1
                if num > 2:
                    i = self.name[::-1].index(' ')
                    self.name = self.name[:-i] + str(num)
                    self.find_duplicates(num)
                elif num > 1:
                    self.name = self.name + ' ' + str(num)
                    self.find_duplicates(num)
                break

    def det_draft_cost(self):
        draft_cost = len(self.provisions)
        # draft_cost = 0
        # for subject in self.provisions:
        #     try:
        #         draft_cost += abs(self.provisions[subject] - laws[subject])
        #     except TypeError:
        #         draft_cost += 5
        draft_cost *= self.cost_multiplier
        return draft_cost

    def json_dump(self):
        attr = self.__dict__.copy()
        attr["type"] = type(self).__name__
        return attr

    def in_queue(self):
        if self.id_num in imminent_progress or \
                self.id_num in politicians[self.sponsor].bwfc or \
                self.id_num in government_orders or \
                self.id_num in order_of_precedence:
            return True
        else:
            return False

    def advance(self):
        stage = Bill.stages[self.stage]
        sponsor = politicians[self.sponsor]
        if stage == "Passed":
            sponsor.bbp = None
        elif stage == "Second Reading":
            if self.sponsor not in cabinet:
                sponsor.bwfc.append(self.id_num)
            else:
                government_orders.append(self.id_num)
        elif stage == "Third Reading":
            if self.sponsor not in cabinet:
                order_of_precedence.append(self.id_num)
            else:
                government_orders.append(self.id_num)
        else:
            imminent_progress.append(self.id_num)

    def progress(self):
        if not self.dead:
            success = False
            stage = Bill.stages[self.stage]
            if stage == "Drafting":
                self.draft_progress += 1
                # todo draft progress should be increased by legislative ability of author
                # print(self.draft_progress, self.draft_cost)
                if self.draft_progress >= self.draft_cost:
                    success = True
            elif stage == "First Reading":
                success = self.introduce()
            elif stage == "Second Reading":
                success = self.first_vote()
            elif stage == "Committee":
                success = self.committee()
            elif stage == "Third Reading":
                success = self.final_vote()
            elif stage == "Senate":
                success = self.senate()
            elif stage == "Royal Assent":
                success = self.royal_assent()

            if self.stage > 0 or success:
                if success:
                    self.stage += 1
                else:
                    self.stage = 1
                    self.dead = True

    def reset(self):
        if self.stage > 0:
            self.stage = 1
            self.num = None
            self.dead = False

    def add_provision(self, subject, position):
        self.provisions[subject] = position
        self.det_draft_cost()

    def introduce(self):
        self.num = Bill.nums[self.kind]
        Bill.nums[self.kind] += 1
        return True

    def first_vote(self):
        return vote(self, 1)[0]

    @staticmethod
    def committee():
        # todo make committee do something
        return True

    def final_vote(self):
        return vote(self, 2)[0]

    @staticmethod
    def senate():
        # todo make senate do something
        return True

    def royal_assent(self):
        for subject in self.provisions:
            laws[subject] = self.provisions[subject]
        return True


def election():
    popular_vote = {}
    riding_wins = {}
    total_votes = 0
    for p in parties:
        parties[p].seats = 0
        popular_vote[p] = 0
        riding_wins[p] = 0

    for region in regions:
        regional_vote, regional_wins = regions[region].election()
        for p in regional_vote:
            popular_vote[p] += regional_vote[p]
            riding_wins[p] += regional_wins[p]

    for p in popular_vote:
        parties[p].popular_vote = popular_vote[p]
        total_votes += parties[p].popular_vote
    if laws["electsys"] == 100:
        elect_fptp(riding_wins)
    elif laws["electsys"] < 100:
        elect_prop(popular_vote, total_votes)
    # display.popular_vote(popular_vote, total_votes, len(persons), scale)
    # display.seats(parties, number_of_seats)
    # display.seat_wins(riding_wins, number_of_seats)
    game_state["parliament"] += 1
    new_parliament()


def elect_fptp(riding_wins):
    for p in parties:
        parties[p].seats = riding_wins[p]


def elect_prop(popular_vote, total_votes):
    votes_per_seat = int(sum(popular_vote.values()) / number_of_seats)
    for x in range(number_of_seats):
        tally = {}
        for p in parties:
            if popular_vote[p] > int(total_votes * laws["cutoff"]):
                tally[p] = 0
        for p in parties:
            if p in tally:
                tally[p] = popular_vote[p] - parties[p].seats * votes_per_seat
        parties[toolkit.largest_in_dictionary(tally)].seats += 1


def vote(bill, number, hypothetical=False):
    vote = {"Yea": {}, "Nay": {}}
    for party in house_parties:
        vote["Yea"][party] = {}
        vote["Nay"][party] = {}
    for p in politicians.values():
        if number == 1:
            reason = p.first_vote(bill)
        else:
            reason = p.final_vote(bill)
        if sum(reason.values()) > 0:
            vote["Yea"][p.party.tag][p.id_num] = reason
        else:
            vote["Nay"][p.party.tag][p.id_num] = reason
    if not hypothetical:
        votes.append(vote)
        vote_subjects.append((bill.id_num, number))
    num = vote_num(vote)
    if num["Yea"] > num["Nay"]:
        passed = True
    else:
        passed = False
    # display.vote_result(num["Yea"], num["Nay"], passed)
    return passed, vote


def vote_num(vote):
    vote_num = {}
    for way in vote:
        vote_num[way] = sum([len(vote[way][party]) for party in vote[way]])
    return vote_num


def do_poll():
    results = {}
    total_polled = {}
    for region in regions:
        total_polled[region] = 0
        results[region] = {}
        for party in regions[region].ballot:
            results[region][party] = 0
    # sample = random.sample(list(persons.values()), 1000)
    for tag, province in regions.items():
        for riding in province.ridings.values():
            for p in riding.persons:
                person = persons[p]
                person.consider_parties(ridings[person.riding].ballot)
                results[tag][person.supports] += 1
                total_polled[tag] += 1
    # sample = persons.values()
    # for person in sample:
    #     person.consider_parties(ridings[person.riding].ballot)
    #     if person.supports not in results:
    #         results[person.supports] = 1
    #     else:
    #         results[person.supports] += 1
    total_polled["national"] = sum([total_polled[region] for region in total_polled])
    results["national"] = {}
    for region in results:
        if region != "national":
            for party in results[region]:
                if party not in results["national"]:
                    results["national"][party] = 0
                results["national"][party] += results[region][party]
    for region in results:
        for party in results[region]:
            results[region][party] = round(results[region][party] / total_polled[region] * 100, 1)
    return results


def det_pol_pos(pos):
    if pos <= -70:
        pol_pos = "far-left"
    elif pos <= -40:
        pol_pos = "left"
    elif pos <= -10:
        pol_pos = "centre-left"
    elif pos < 10:
        pol_pos = "centre"
    elif pos < 40:
        pol_pos = "centre-right"
    elif pos < 70:
        pol_pos = "right"
    else:
        pol_pos = "far-right"
    return pol_pos


def det_importance(pos):
    if pos < 0.2:
        imp = "not at all"
    elif pos < 0.4:
        imp = "not really"
    elif pos < 0.6:
        imp = "somewhat"
    elif pos < 0.8:
        imp = "very"
    else:
        imp = "most"
    return imp


def compare_pops(region):
    if region == "national":
        return sum(list(population_dist.values()))
    elif region in population_dist:
        return population_dist[region]
    else:
        return 0


def add_poll():
    poll_results = do_poll()
    for region in poll_results:
        if region not in opinion_polls["party_support"]:
            opinion_polls["party_support"][region] = {}
        for party in poll_results[region]:
            if party not in opinion_polls["party_support"][region]:
                opinion_polls["party_support"][region][party] = {}
            opinion_polls["party_support"][region][party][game_state["turn"] - 1] = poll_results[region][party]


def get_politician(id_num):
    # if id_num is None:
    #     id_num = game_state["player"]
    try:
        return politicians[id_num]
    except ValueError:
        return former_politicians[id_num]


def replenish_oop(eligible, num, times):
    if times == 1:
        over = False
    else:
        over = True
    for i in range(len(LCPMB)):
        id_num = LCPMB.pop(0)
        if (len(politicians[id_num].bwfc) == times and eligible.count(id_num) < times) or \
                len(politicians[id_num].bwfc) > times:
            eligible.append(id_num)
            over = False
            if len(eligible) == num:
                break
    else:
        establish_pol()
        if not over:
            eligible = replenish_oop(eligible, num, times + 1)
        else:
            return eligible
    return eligible


def end_turn():
    # This is the end of the turn
    if len(government_orders) > 0:
        bills[government_orders.pop(0)].progress()

    if len(order_of_precedence) <= private_orders_length / 2:
        num = private_orders_length - len(order_of_precedence)
        eligible = replenish_oop([], num, 1)
        if len(eligible) < num:
            num = len(eligible)
        for i in range(num):
            bill = politicians[eligible[i]].select_bwfc()
            politicians[eligible[i]].bwfc.remove(bill)
            order_of_precedence.append(bill)
    if len(order_of_precedence) > 0:
        bills[order_of_precedence.pop(0)].progress()

    for bill_id in imminent_progress:
        bills[bill_id].progress()
    imminent_progress.clear()

    game_state["turn"] += 1
    game_state["date"] = date_translator.get_date(turn_length, game_state["date"])

    start_turn()


def start_turn():
    # This is the beginning of the next turn
    add_poll()
    people = list(persons.values())
    random.shuffle(people)
    for person in people:
        person.do_turn()


def establish_pol():
    # pol: private_orders_list
    mps = list(politicians.values())
    random.shuffle(mps)
    for mp in mps:
        if mp not in cabinet:
            LCPMB.append(mp.id_num)


def new_parliament():
    government_orders.clear()
    LCPMB.clear()
    establish_pol()
    order_of_precedence.clear()
    for b in bills.values():
        b.reset()


def init_game():
    clear_data()
    for entry, value in default_game_state.items():
        game_state[entry] = value
    for party in party_tags:
        Party(party, party_names[party], party_constituencies[party], party_positions[party])
    for region in region_tags:
        Region(region, region_seats[region], population_dist[region], seat_dist[region])
    for kind in poll_types:
        opinion_polls[kind] = {}
    game_state["player"] = random.choice(list(politicians.keys()))
    # player = politicians[game_state["player"]]
    # print(player.name, player.age, player.party.tag)
    new_parliament()
    start_turn()


parties: Dict[str, Party] = {}  # keys are party tags
politicians: Dict[int, ParliamentMember] = {}  # keys are id_num
former_politicians: Dict[int, Person] = {}  # keys are id_num
cabinet: Dict[str, int] = {}  # keys are id_num
persons: Dict[int, Person] = {}  # keys are id_num
regions: Dict[str, Region] = {}  # keys are postal code
ridings: Dict[str, Riding] = {}  # keys are region's postal code + district number
bills: Dict[int, Bill] = {}  # keys are id_num

all_data = [parties, politicians, former_politicians, persons, regions, ridings, bills, votes, vote_subjects,
            page_history, game_state, opinion_polls, government_orders, LCPMB, order_of_precedence, imminent_progress]
