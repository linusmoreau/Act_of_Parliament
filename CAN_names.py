import random

'''source: https://forebears.io/canada/forenames'''


names = {
    "english": {
        "female": {
            "Sarah", "Emily", "Emma", "Jessica", "Hannah", "Samantha", "Catherine", "Rachel", "Jade", "Amy", "Maya",
            "Olivia", "Charlotte", "Aria", "Ava", "Chloe", "Zoey", "Abigail", "Amelia", "Isabella", "Mila", "Lily",
            "Riley", "Madison", "Mia", "Nora", "Ella", "Jennifer", "Linda", "Karen", "Mary", "Lisa", "Susan", "Nancy",
            "Heather", "Kelly", "Sandra", "Barbara", "Laura", "Carole", "Elizabeth", "Sharon", "Angela", "Judy",
            "Brenda", "Debbie", "Amanda", "Stephanie", "Wendy", "Kathy", "Melissa", "Cindy", "Cheryl", "Margaret",
            "Cathy", "Janet", "Andrea", "Anna", "Tracy", "Lynn", "Helen", "Joan", "Sue", "Tammy", "Jane", "Shannon",
            "Janice", "Ann", "Ashley", "Tina", "Patricia", "Erin", "Caroline", "Elena", "Ruth", "Sheila", "Rose",
            "Rebecca", "Irene", "Diana", "Rita", "Joyce", "Paula", "Lindsay", "Kathleen", "Tracey", "Teresa", "Anita",
            "Cynthia", "Crystal", "Maria", "Theresa", "Pauline", "Katherine", "Leslie", "Megan", "Dorothy", "Victoria",
            "Jill", "Grace", "Carmen", "Monica", "Claire"
        },
        "male": {
            "Alex", "Nathan", "Simon", "William", "David", "Nicolas", "Samuel", "Kevin", "Charles", "Jordan", "Noah",
            "Liam", "Jackson", "Lucas", "Logan", "Benjamin", "Jacob", "Oliver", "James", "Lincoln", "Jack", "Ethan",
            "Carter", "Aiden", "Grayson", "Mason", "Owen", "Leo", "Nathan", "John", "Robert", "Michael", "Paul",
            "Richard", "Peter", "Brian", "Daniel", "Mark", "Chris", "George", "Ken", "Steven", "Jim", "Andrew", "Eric",
            "Kelly", "Ron", "Don", "Gary", "Frank", "Thomas", "Jason", "Donald", "Scott", "Martin", "Wayne", "Dan",
            "Doug", "Joe", "Marc", "Terry", "Bob", "Bruce", "Greg", "Gordon", "Stephen", "Mike", "Rick", "Edward",
            "Jeff", "Patrick", "Larry", "Tony", "Anthony", "Tim", "Timothy", "Ryan", "Ian", "Gerald", "Ronald", "Steve",
            "Fred", "Dennis", "Keith", "Shannon", "Allan", "Robin", "Bill", "Dave", "Douglas", "Randy", "Barry",
            "Lawrence", "Brad", "Alan", "Ray", "Matthew", "Tom", "Dale", "Adam", "Craig", "Norman", "Sean", "Jonathan",
            "Bernard", "Roy", "Walter", "Neil", "Henry", "Albert", "Kenneth", "Glen", "Derek", "Harold", "Carl",
            "Christopher", "Sam", "Lindsay", "Ted", "Glenn", "Brent", "Matt", "Harry", "Trevor", "Colin", "Dean",
            "Darren", "Jerry", "Ralph", "Philip", "Ross", "Justin", "Todd", "Francis", "Al", "Gerry", "Danny", "Roland"
        },
        "surnames": {
            "Kennedy", "Smith", "Martin", "Brown", "Roy", "Wilson", "MacDonald", "Johnson", "Taylor", "Campbell",
            "Anderson", "Lee", "Jones", "White", "Williams", "Miller", "Thompson", "Young", "Morin",
            "Scott", "Stewart", "Reid", "Moore", "King", "Robinson", "Murphy", "Clark", "Johnston", "Clarke", "Ross",
            "Walker", "Thomas", "Landry", "Kelly", "Davis", "Mitchell", "Murray", "Richard", "Wright", "Girard",
            "Lewis", "Baker", "Roberts", "Graham", "Harris", "Jackson", "Green", "Fraser", "Hall", "Hill", "Wood",
            "Bell", "Allen", "Adams", "Bennett", "Watson", "Robertson", "Walsh", "Collins", "Evans", "Hebert",
            "Hamilton", "Russell", "Cook", "Morrison", "Grant", "Parsons", "Sanders", "Warren", "Scheer", "May",
            "Peters", "Cooper", "Gray", "Marshall", "Simpson", "Harvey", "McLean", "Ward", "Morris", "Parker", "Hunter",
            "Davidson", "Elliott", "Harrison", "Richardson", "James", "Foster", "MacKenzie", "Gordon", "Fisher",
            "Hughes", "Rogers", "Gibson", "Ryan", "Morgan", "Patterson", "McLeod", "Bailey", "McKay"
        }
    },
    "french": {
        "female": {
            "Marie", "Marguerite", "Thérèse", "Louise", "Lise", "Denise", "Diane", "Nicole", "Cécile", "Hélène",
            "Monique", "Madeleine", "Suzanne", "Jeannine", "Francine", "Jacqueline", "Jeanne", "Gisèle", "Yvonne",
            "Claire", "Ginette", "Michelle", "Julie", "Christine", "Anne", "Joanne", "Mélanie", "Danielle", "Valérie",
            "Nathalie", "Isabelle", "Michèle"
        },
        "male": {
            "Joseph", "Pierre", "André", "Louis", "Michel", "François", "Jacques", "Jean", "Robert", "Marcel",
            "Claude", "Charles", "Roger", "Gilles", "Gérard", "Henri", "Arthur", "Georges", "Denis", "Raymond",
            "Albert", "Maurice", "Paul", "René", "Guy", "Alain", "Sylvain", "Luc", "Stéphane", "Yvon", "Gérard", "Yves",
            "Thériault", "Benoît", "Normand", "Réjean"
        },
        "surnames": {
            "Tremblay", "Gagnon", "Roy", "Côté", "Gauthier", "Morin", "Belanger", "Bouchard", "Pelletier", "Gagné",
            "Lavoie", "Fortin", "Levesque", "Boucher", "Bergeron", "Simard", "Caron", "Girard", "Leblanc", "Ouellet",
            "Fournier", "Lefebvre", "Cloutier", "Dubé", "Poulin", "Poirier", "Thibault", "Beaulieu", "Martel", "Bédard",
            "Nadeau", "Leclerc", "Lapointe", "Grenier", "Hebert", "Demers", "Richard", "Desjardins", "Moreau",
            "Boudreau", "Bernier", "Lambert", "Lalonde", "Arsenault", "Dupuis", "Turcotte", "Lemieux", "Lachance",
            "Beaudoin", "Gosselin", "Langlois", "Savard", "Mercier", "Villeneuve"
        }
    },
    "other": {
        "surnames": {
            "Singh", "Wang", "Li", "García", "Patel", "Müller", "Nguyen", "Gonzalez", "Rossi", "Devi", "Ali", "Zhang",
            "Wong", "Liu", "Yang", "Kumar", "Wu", "Xu", "Chen", "Huang", "Zhao", "Zhou", "Khan", "Ma", "Lu", "Sun",
            "Zhu", "Yu", "Kim", "Lin", "He", "Hu", "Jiang", "Guo", "Ahmed", "Khatun", "Luo", "Gao", "Akter", "Zheng",
            "Tang", "Das", "Wei", "Liang", "Islam", "Shi", "Song", "Xie", "Han", "Mohamed", "da Silva", "Tan", "Bai",
            "Deng", "Yan", "Kaur", "Feng", "Hernandez", "Rodriguez", "Cao", "Hussain", "Hassan", "Lopez", "Martinez",
            "Ahmad", "Ibrahim", "Ceng", "Peng", "Cai", "Tran", "Xiao", "Pan", "Cheng", "Yuan", "Rahman", "Yadav",
            "Perez", "Su", "Xia", "Mao"
        }
    }
}


def full_name(gender=random.choice(("male", "female")),
              background=random.choice(("english", "french", "other")),
              language=random.choice(("english", "french"))):
    return first_name(language, gender) + ' ' + last_name(background)


def first_name(language, gender):
    if gender.lower() == "male" or gender.lower() == "female":
        return random.choice(tuple(names[language][gender]))
    else:
        return random.choice(tuple(names[language]["male"] | names[language]["female"]))


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
    print("Duplicates:", len(duplicate_list))
    print(gen_names)
    print(duplicate_list)
