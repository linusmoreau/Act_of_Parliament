import random
import json

'''source: https://forebears.io/canada/forenames'''


try:
    f = open("data/names.json", 'r')
    names = json.load(f)
    f.close()
except FileNotFoundError:
    raise FileNotFoundError("Could not find names.json in data folder.")


def full_name(gender=random.choice(("male", "female")),
              background=random.choice(("english", "french", "other")),
              language=random.choice(("english", "french"))):
    return first_name(language, gender) + ' ' + last_name(background)


def first_name(language, gender):
    gender = gender.lower()
    if gender == "male" or gender == "female":
        return random.choice(tuple(names[language][gender]))
    else:
        return random.choice(names[language]["male"] + names[language]["female"])


def last_name(background):
    return random.choice(tuple(names[background]["surnames"]))


if __name__ == "__main__":
    print("Number of male English given names:", len(names["english"]["male"]))
    print("Number of female English given names:", len(names["english"]["female"]))
    print("Number of English surnames:", len(names["english"]["surnames"]))
    print("Number of male French given names:", len(names["french"]["male"]))
    print("Number of female French given names:", len(names["french"]["female"]))
    print("Number of French surnames:", len(names["french"]["surnames"]))
    print("Number of other surnames:", len(names["other"]["surnames"]))
    gen_names = []
    duplicate_list = []
    for _ in range(260):
        name = full_name("any", "english", "english")
        if name in gen_names:
            duplicate_list.append(name)
        gen_names.append(name)
    for _ in range(78):
        name = full_name("any", "french", "french")
        if name in gen_names:
            duplicate_list.append(name)
        gen_names.append(name)
    print("Total people:", len(gen_names))
    print(gen_names)
    print("Duplicates:", len(duplicate_list))
    print(duplicate_list)
