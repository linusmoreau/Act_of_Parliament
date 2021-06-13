

def process_file(content, candidates):
    data = []
    for line in content:
        if "text-align:left" in line:
            riding_dat = {}
            dat = line.strip().split('||')
            riding_dat['name'] = dat[0].split('|')[-1].strip(' []')
            riding_dat['region'] = dat[1].split('|')[-1].strip()
            riding_dat['party'] = dat[5].split('|')[-1].strip().upper()
            riding_dat['turnout'] = round(float(dat[10].strip(' %')) / 100, 3)
            votes = {}
            for i in range(len(candidates)):
                try:
                    votes[candidates[i]] = int(dat[11 + i].strip().replace(',', ''))
                except ValueError:
                    pass
            riding_dat['votes'] = votes
            riding_dat['total'] = int(dat[19].strip().replace(',', ''))
            data.append(riding_dat)
    return data


def write_to_file(data, candidates):
    order = ['name', 'region', 'party', 'turnout', 'total', 'votes']
    txt = ''
    for subj in order:
        if subj == 'votes':
            for cand in candidates:
                txt += cand + ','
        else:
            txt += subj + ','
    txt = txt[:-1] + '\n'
    for dat in data:
        txt += dat['name'] + ',' + \
               dat['region'] + ',' + \
               dat['party'] + ',' + \
               str(dat['turnout']) + ',' + \
               str(dat['total']) + ','
        for cand in candidates:
            try:
                txt += str(dat['votes'][cand]) + ','
            except KeyError:
                txt += ','
        txt = txt[:-1] + '\n'
    txt = txt[:-1]
    with open('data/ridings.csv', 'w') as f:
        f.write(txt)


if __name__ == '__main__':
    with open('test_data/canada_2019_by_riding.txt', 'r', encoding='utf-8') as f:
        content = f.readlines()
    candidates = ['LIB', 'CON', 'NDP', 'BQ', 'GRN', 'PPC', 'IND']
    write_to_file(process_file(content, candidates), candidates)
