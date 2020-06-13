import random

days_per_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August",
          9: "September", 10: "October", 11: "November", 12: "December"}


def get_date(dif, initial_date):
    init_day = initial_date.split('/')
    year = int(init_day[0])
    month = int(init_day[1])
    day = int(init_day[2])
    day += dif
    while True:
        month_length = get_month_length(month, year)
        year_length = get_year_length(year)
        if day > year_length:
            day -= year_length
            year += 1
        elif day <= -year_length:
            year -= 1
            day += get_year_length(year)
        elif day > month_length:
            day -= month_length
            month += 1
            if month > 12:
                year += 1
                month -= 12
        elif day <= 0:
            month -= 1
            if month < 1:
                month += 12
                year -= 1
            day += get_month_length(month, year)
        else:
            break
    return str(year) + '/' + str(month).rjust(2, '0') + '/' + str(day).rjust(2, '0')


def get_month_length(month, year):
    month_length = days_per_month[month]
    if month == 2 and leap_year(year):
        month_length += 1
    return month_length


def get_year_length(year):
    if leap_year(year):
        return 366
    else:
        return 365


def leap_year(year):
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return True
    else:
        return False


def date_as_text(date):
    date = date.split('/')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    return months[month] + ' ' + str(day) + ', ' + str(year)


def age(birthdate, currentdate):
    currentdate = currentdate.split('/')
    birthdate = birthdate.split('/')
    years = int(currentdate[0]) - int(birthdate[0])
    if currentdate[1] < birthdate[1] or (currentdate[1] == birthdate[1] and currentdate[2] < birthdate[2]):
        years -= 1
    return years


def random_date(year):
    month = random.randrange(1, 13)
    day = random.randrange(1, get_month_length(month, year))
    return str(year) + '/' + str(month) + '/' + str(day)


def between(start, end, date):
    dates = [start.split('/'), end.split('/'), date.split('/')]
    for i in range(len(dates)):
        dates[i] = dates[i][0] * 10000 + dates[i][1] + 100 + dates[i][2]
    if dates[0] < dates[2] <= dates[1]:
        return True
    else:
        return False


if __name__ == "__main__":
    init_date = "2020/04/12"
    dif = random.randint(-100000, 100000)
    date = get_date(dif, init_date)
    print(date)
    print(date_as_text(date))
    print(age("2002/09/05", "2020/04/30"))
