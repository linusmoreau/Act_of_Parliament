import json


def load_populations():
    dat = {}
    with open("test_data/country_populations.txt", 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            if '"' in line:
                nline = line.strip().split('"')
                name = nline[1]
                line_dat = nline[2].strip(',').split(',')
                tag = line_dat[0]
                year = int(line_dat[1])
                population = int(line_dat[2])
            else:
                line_dat = line.strip().split(',')
                name = line_dat[0]
                tag = line_dat[1]
                year = int(line_dat[2])
                population = int(line_dat[3])
            if tag in dat:
                dat[tag]['populations'][year] = population
            else:
                dat[tag] = {'name': name, 'populations': {year: population}}
    return dat


def load_groupings():
    with open('test_data/ideologies.txt', 'r') as f:
        return json.load(f)


def get_population(name: str, populations):
    while '_' in name:
        i = name.find('_')
        name = name[:i] + ' ' + name[i + 1:]
    for attr in populations.values():
        if name in attr['name']:
            return attr['populations'][max(attr['populations'].keys())]
    else:
        names = {'North Korea': 'PRK',
                 'South Korea': 'KOR',
                 'Czechia': 'CZE',
                 'Slovakia': 'SVK',
                 'DR Congo': 'COD',
                 'Timor Leste': 'TLS',
                 'Laos': 'LAO',
                 'Cote d Ivoire': 'CIV',
                 'Kyrgyzstan': 'KGZ',
                 'Guinea Bissau': 'GNB',
                 'Saint Vinvcent and the Grenadines': 'VCT'}
        try:
            tag = names[name]
            temp = populations[tag]['populations']
            return temp[max(temp.keys())]
        except KeyError:
            if name == 'Taiwan':
                return 23590000
            else:
                print("Not found:", name)
                return 0


if __name__ == '__main__':
    populations = load_populations()
    groupings = load_groupings()
    ideological_pops = {}
    for col, attr in groupings['groups'].items():
        ideological_pops[attr['label']] = sum([get_population(name, populations) for name in attr['paths']])
    order = sorted(list(ideological_pops.keys()), key=lambda n: ideological_pops[n], reverse=True)
    print()
    print('Ideologies'.rjust(24), 'Population'.rjust(16))
    for ideology in order:
        print(ideology.rjust(24), str(ideological_pops[ideology]).rjust(16))
