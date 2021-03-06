import sys
import os
import os.path
from os import path
import requests
import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
import re
from typing import Optional
import win32console  # needs pywin32
import time

## TODO
# Don't crash when the file is already existing and cannot move
# implement a command line interface

# CONFIG
auto_approve_single_match = True
autoskip = False
move_skipped_files = True
replace_site_names_globally = True
turn_dates_around = False
renamed_dir = '\\\\unraid\\porn\\Sites\\_import4'
skipped_dir = ''

_stdin = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)


def input_def(prompt, default=''):
    keys = []
    for c in str(default):
        evt = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
        evt.Char = c
        evt.RepeatCount = 1
        evt.KeyDown = True
        keys.append(evt)

    _stdin.WriteConsoleInput(keys)
    return input(prompt)


site_scene_names = {
    '': [''],
    '18 Only Girls': ['18onlygirls'],
    '18 Years Old': ['18yearsold'],
    '2 Chicks Same Time': ['2cst'],
    'ATK Girlfriends': ['atkgfs', 'ATKGirlfriends'],
    'All Anal': ['allanal'],
    'All Fine Girls': ['allfinegirls'],
    'All Girl Massage': ['agm', 'AllGirlMassage'],
    'All Internal': ['AllInternal'],
    'Amateur Allure': ['aa'],
    'Amateur Lapdancer': ['amateurlapdancer'],
    'Amour Angels': ['amourangels'],
    'Anal Overdose': ['analoverdose'],
    'Ass Parade': ['ap'],
    'Asshole Fever': ['assholefever'],
    'Babes': ['babes'],
    'Back Room Facial': ['brf'],
    'Backroom Casting Couch': ['brcc', 'bcc'],
    'Backroom Facials': ['bf'],
    'Backroom MILF': ['mf'],
    'Ball Busting World': ['BallBustingWorld'],
    'Banana Hotties': ['bananahotties'],
    'Bang Bros 18': ['bbe'],
    'Bang Bros Angels': ['bng'],
    'Bang Bros Clips': ['bbc'],
    'Bang Bros Remastered': ['rm'],
    'Bang Bus': ['bb'],
    'Bang Casting': ['hih'],
    'Bang POV': ['bangpov', 'bpov'],
    'Bang Pretty And Raw': ['bprettyraw'],
    'Bang Rammed': ['brammed'],
    'Banging Beauties': ['bangingbeauties'],
    'Banned Stories': ['BannedStories'],
    'Beauty 4K': ['beauty4k'],
    'Big Butts Like It Big': ['bblib'],
    'Big Mouthfuls': ['bm', 'bmf'],
    'Big Tit Cream Pie': ['btcp'],
    'Big Tits, Round Asses': ['btra'],
    'Big Wet Butts': ['bwb'],
    'Blacked Raw': ['blackedraw'],
    'Blacked': ['b'],
    'Blowbang Girls': ['bbg'],
    'Blowjob Fridays': ['bj'],
    'Brace Faced': ['bracefaced'],
    'Bratty Sis': ['brattysis'],
    'Brazzers Exxtra': ['bex'],
    'Brazzers ZZ Series': ['zzs'],
    'British Sex Films': ['BritishSexFilms'],
    'Broken Babes': ['BrokenBabes'],
    'Brown Bunnies': ['bkb'],
    'Brutal Castings': ['bcas'],
    'Can He Score': ['bd'],
    'Casting Couch X': ['castingcouchx', 'ccx'],
    'Cherry Pop': ['cherrypop'],
    'Colombia Fuck Fest': ['cff'],
    'Cuckold Sessions': ['cuckoldsessions'],
    'Cum Blast City': ['CumBlastCity'],
    'Cum Fiesta': ['cuf'],
    'Czech Casting': ['cc'],
    'DTF Sluts': ['dtfsluts'],
    'Dad Crush': ['dadcrush'],
    'Dark X': ['darkx'],
    'Day With A Pornstar': ['dcdaywithapornstar'],
    'Deepthroat Love': ['dtl'],
    'Deepthroat Sirens': ['dts'],
    'Device Bondage': ['deb'],
    'Digital Desire': ['dd'],
    'Dirty World Tour': ['bf'],
    'Do The Wife': ['dothewife'],
    'Dont Break Me': ['dbm', 'dontbreakme'],
    'Dorcel Club': ['dorcelclub'],
    'Electro Sluts': ['el'],
    'Erotique TV Live': ['etvl'],
    'Exploited 18': ['exp'],
    'Exxxtra Small': ['exxxtrasmall'],
    'Facial Fest': ['ff'],
    'Fake Agent': ['fakeagent'],
    'Fake Hospital': ['fakehospital'],
    'First Class POV': ['fcpov'],
    'First Time Auditions': ['firsttimeauditions', 'fta'],
    'Fuck Studies': ['fuckstudies'],
    'Fucked Hard 18': ['fh18'],
    'Fucking Machines': ['fum'],
    'Gape Land': ['gapeland'],
    'Genuine Features': ['genuinefeatures'],
    'Girls Gone Pink': ['girlsgonepink'],
    'Girls Rimming': ['girlsrimming'],
    'Girls Try Anal': ['gta'],
    'Girls Way': ['gw'],
    'Glory Hole Loads': ['ghl'],
    'HD Love': ['hdlove'],
    'HardX': ['hardx'],
    'Hot And Mean': ['ham'],
    'Immoral Live': ['il'],
    'In The Crack': ['inthecrack'],
    'Innocent High': ['innocenthigh'],
    'Jays POV': ['jayspov'],
    'Jesh By Jesh': ['jbyj'],
    'Jesse Loads Monster Facials': ['jesseloadsmonsterfacials'],
    'Johnny Castle Unleashed': ['jcu'],
    'Jules Jordan': ['julesjordan', 'Jules Jordan Video'],
    'Kelly Madison': ['kellymadison'],
    'Kinky Family': ['kinkyfamily'],
    'LA New Girl': ['lang'],
    'Latina Rampage': ['lrp'],
    'Legal Porno': ['legalporno'],
    'Lesbian X': ['lesbianx'],
    'Lily Chey': ['lilychey'],
    'Little Caprice': ['lcd'],
    'MILF Lessons': ['ml'],
    'MILF Soup': ['ms'],
    'Magical Feet': ['fj'],
    'Mano Job': ['maj'],
    'Manuel Ferrara': ['mfa'],
    'Massage Creep': ['mc'],
    'Massage Parlor': ['mp'],
    'Met Art': ['Met-Art', 'metart'],
    'Mofos B Sides': ['mbs'],
    'Mofos Lab': ['mofoslab'],
    'Mofos Live': ['mofosl'],
    'Mom Is Horny': ['mih'],
    'Mom XXX': ['mom'],
    'Moms Teach Sex': ['mts'],
    'Money Talks': ['moneytalks'],
    'Monsters Of Cock': ['mc', 'moc'],
    'Mr. Anal': ['ma'],
    'My Dirty Maid': ['mda'],
    'My Life In Miami': ['mlim', 'MyLifeInMiami'],
    'My Sisters Hot Friend': ['mysistershotfriend'],
    'New Sensations': ['newsensations'],
    'Nubile Films': ['nubilef'],
    'Nubiles Casting': ['nubc'],
    'Nubiles ET': ['nubileset'],
    'Nubiles': ['nubiles'],
    'Nuru Massage': ['num'],
    'Old Goes Young': ['ogy'],
    'Only Teen Blowjobs': ['OnlyTeenBlowJobs'],
    'Only Tiny Teens': ['OnlyTinyTeens'],
    'POV Life': ['povlife'],
    'POVD': ['povd'],
    'Pascals Sub Sluts': ['psus'],
    'Passion HD': ['phd', 'passion-hd', 'passionhd'],
    'Pawg': ['pwg'],
    'Pervs On Patrol': ['pop', 'pervsonpatrol'],
    'Petite HD Porn': ['phdp', 'petitehdporn'],
    'Playboy Plus': ['playboyplus'],
    'Porn Star Spa': ['pos'],
    'Pretty Dirty': ['prdi'],
    'Private Casting X': ['privatecastingx'],
    'Private Society': ['PrivateSociety'],
    'Property Sex': ['ps', 'propertysex'],
    'Public Agent': ['pba'],
    'Public Bang': ['pb'],
    'Public Disgrace': ['pud'],
    'Pure Taboo': ['puretaboo'],
    'RK Prime': ['rkprime'],
    'Real Ex Girlfriends': ['reg'],
    'Real Slut Party': ['rsp'],
    'Sex And Submission': ['sas', 'SexAndSubmission'],
    'Sexually Broken': ['sb', 'seb', 'SexuallyBroken'],
    'Shady PI': ['spi'],
    'Share My BF': ['sharemybf'],
    'Shes New': ['shesnew'],
    'Shop Lyfter': ['shoplyfter'],
    'Simply Anal': ['simplyanal'],
    'Sins Life': ['sinslife'],
    'Slob Jobz': ['slobjobz'],
    'Spy Fam': ['spyfam'],
    'Stasy Q': ['stasyq'],
    'Stepmom Videos': ['smv'],
    'Street Ranger': ['sg'],
    'Subby Girls': ['SubbyGirls'],
    'Swallow Salon': ['swallowsalon'],
    'Tease and Thank You': ['TeaseandThankYou'],
    'Teen BFF': ['tbff'],
    'Teen Pies': ['tp', 'teenpies'],
    'Teens Do Porn': ['tdp'],
    'Teens Like It Big': ['tlib'],
    'Teens Love Black Cocks': ['tlbc'],
    'Teens Love Huge Cocks': ['teenslovehugecocks', 'tlhc'],
    'Teens Love Money': ['tlm'],
    'The Dick Suckers': ['tds'],
    'The Life Erotic': ['thelifeerotic'],
    'The Real Workout': ['trwo'],
    'The Training Of O': ['tto'],
    'The Training of O': ['ToO'],
    'The Upper Floor': ['tuf'],
    'This Girl Sucks': ['thisgirlsucks'],
    'Throated': ['ted'],
    'Tiny 4K': ['tiny4k'],
    'Tonights Girlfriend': ['tonightsgirlfriend', 'tog'],
    'Tug Jobs': ['tj'],
    'Tugjobs': ['hj'],
    'Tushy Raw': ['tushyraw'],
    'Twistys Hard': ['th', 'twistyshard'],
    'Ultra Films': ['ultrafilms'],
    'Viv Thomas': ['viv'],
    'Wake Up N Fuck': ['wunf'],
    'Wank it Now': ['wankitnow'],
    'Web Young': ['wy'],
    'Woodman Casting X': ['wcx'],
    'Working Latinas': ['wl'],
    'Wow Girls': ['wowg', 'wowgirls'],
    'Wow Porn': ['wowp', 'wowporn'],
    'Young Legal Porn': ['younglegalporn'],
}
ignored_words = [
    r'((3840x)?2160|(1920x)?1080|(1280x)?720|480)p?',
    r'(?<!\w)(xxx|full-hd|hevc|reencode|highversion|high|tayto|pics)(?!\w)',
    r'(?<!\w)(?<!passion )(?<!petite )hd(?!\w)',
    r'(?<!\w)(?<!tiny )4k(?!\w)',
    r'(?<!\w)(h264|h265|x264|x265|hevc|Scenes|10bit)(?!\w)',
    r'{The Rat Bastards}'
]


@dataclass_json
@dataclass
class PerformerExtras:
    gender: Optional[str] = None


@dataclass_json
@dataclass
class PerformerParent:
    name: str
    extras: PerformerExtras = None


@dataclass_json
@dataclass
class Performer:
    name: str
    extra: PerformerExtras = None
    parent: Optional[PerformerParent] = ''

    def gender(self):
        if self.extra.gender is not None:
            return self.extra.gender
        elif self.parent.extras.gender is not None:
            return self.parent.extras.gender
        else:
            return ''

    def get_name(self):
        if self.name is not None:
            return self.name
        else:
            return self.parent.name


@dataclass_json
@dataclass
class Site:
    name: str


@dataclass_json
@dataclass
class Scene:
    id: str
    title: str
    slug: Optional[str]
    site_id: int
    date: Optional[str]
    performers: List[Performer]
    site: Site


def determine_files(folder):
    # todo: also get files in subfolders when there is only one file or only one video and one image
    return list(filter(lambda element: path.isfile(path.join(folder, element)), os.listdir(folder)))


def handle_file(file):
    query = clean_name(file)
    print('\n\n')
    print(f'File: {file}')
    print(f'Searching for: {query}')
    success = False
    while not success:
        result = search(file, query)
        if result == 'RENAMED':
            success = True
            continue
        elif result == 'NO_RESULTS':
            if autoskip:
                break
        elif result == 'SKIP':
            if autoskip:
                break
        new_query = edit_name(query)
        if new_query == query:
            break
        query = new_query
    if not success and move_skipped_files:
        rename_scene(folder, file, skipped_dir, file)


def clean_name(name):
    # print("old name: " + name)
    name = replace_scene_names(name)
    name = filter_ignored_words(name)
    name = reformat_date(name)
    name = path.splitext(name)[0]
    name = replace_filler_characters(name)
    # print("new name: " + name)
    # todo: do an automatic filename cleanup, allow regex rules
    return name


def replace_scene_names(name):
    for key, values in site_scene_names.items():
        for value in values:
            if replace_site_names_globally:
                name = re.sub(rf'(?<!\w)\[?{value}\]?(?!\w)', f'{key} ', name, flags=re.IGNORECASE)
            else:
                name = re.sub(rf'^\[?{value}\]?[- \._]', f'{key} ', name, flags=re.IGNORECASE)
    return name


def filter_ignored_words(name):
    for ignore in ignored_words:
        name = re.sub(ignore, '', name, flags=re.IGNORECASE)
    return name


def reformat_date(name):
    name = re.sub(r'(\d\d)\.(\d\d)\.(\d\d\d\d)', r'\3-\2-\1', name)
    if turn_dates_around:
        name = re.sub(r'(\d\d)\.(\d\d)\.(\d\d)', r'20\3-\2-\1', name)
    else:
        name = re.sub(r'(\d\d)\.(\d\d)\.(\d\d)', r'20\1-\2-\3', name)
    name = re.sub(
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|January|February|March|April|May|June|July|August|September|October|November|December)\.? \d\d, 20\d\d',
        replace_written_month,
        name,
        flags=re.IGNORECASE
    )
    return name


def replace_written_month(date):
    months = {'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3, 'april': 4, 'apr': 4,
              'may': 5, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7, 'august': 8, 'aug': 8,
              'september': 9, 'sep': 9, 'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12}
    month, day, year = re.sub(r'[\.,]', '', date.group()).split(' ')
    return f'{year}-{months.get(month.lower()):02d}-{int(day):02d}'


def replace_filler_characters(name):
    name = re.sub(r'[._\[\]\(\)#&]', ' ', name, flags=re.IGNORECASE)
    name = re.sub(r' {2,}', ' ', name)
    name = re.sub(r'[\'’]', '', name)
    return name.strip()


def edit_name(query):
    query = input_def('EDIT SEARCH QUERY: ', query)
    time.sleep(0.5)
    return query


def search(filename, query):
    # search for the query
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(f'https://metadataapi.net/api/scenes?parse={query}', headers=headers)
    # parse results
    scenes = list(map(lambda entry: Scene.from_dict(entry), json.loads(r.text)['data']))

    if len(scenes) == 0:
        print("No results found.")
        return 'NO_RESULTS'
    elif len(scenes) == 1:
        # rename if there is a match
        new_filename = build_new_filename(scenes[0]) + os.path.splitext(filename)[1]
        if not auto_approve_single_match:
            selection = input(f'Found one match. Rename to: "{new_filename}"? [Yn]:')
        if auto_approve_single_match or selection == '' or selection.lower() == 'y':
            rename_scene(folder, filename, renamed_dir, new_filename)
            return 'RENAMED'
        else:
            return 'SKIP'
    else:
        print()
        for i, scene in enumerate(scenes[:9]):
            print(f'{i + 1}: {build_new_filename(scene)}')
        i_str = input('\nSelection [enter to change search]: ')
        time.sleep(0.5)
        if i_str == '':
            return 'SKIP'
        try:
            i = int(i_str)
        except ValueError:
            print("Couldn't read input")
            return 'SKIP'
        if 0 < int(i) < 10:
            rename_scene(
                folder, filename,
                renamed_dir, build_new_filename(scenes[i - 1]) + os.path.splitext(filename)[1]
            )
            return 'RENAMED'
        else:
            return 'SKIP'


def rename_scene(from_dir, from_filename, to_dir, to_filename):

    make_directory(to_dir)
    target_filename = path.join(to_dir, to_filename)
    if not os.path.isfile(target_filename):
        if from_dir != to_dir:
            print(f'Moving scene to: {to_dir}')
        if from_filename != to_filename:
            print(f'Renaming scene: {from_filename}\t->\t{to_filename}')
        os.rename(path.join(from_dir, from_filename), target_filename)
    else:
        print(f'WARNING: Cannot rename {from_filename} because the target already exists: {to_filename}')


def build_new_filename(scene):
    scene_data = {
        'studio': scene.site.name,
        'date': scene.date,
        'performer': build_performer_string(scene.performers),
        'title': scene.title,
    }
    # todo: get the scheme from somewhere else
    # todo: clean the filename from forbidden characters
    filename = '%(studio)s - %(date)s - %(performer)s - %(title)s' % scene_data
    filename = re.sub(r'[<>/\\|?*]', '', filename)
    filename = re.sub(r'"', '\'', filename)
    filename = re.sub(r':', ' -', filename)
    return filename


def build_performer_string(performers):
    females = list(filter(lambda performer: performer.gender().lower() == 'female', performers))
    names = list(set(map(lambda female: female.get_name(), females)))
    if len(names) > 2:
        return ', '.join(names[:-1]) + ' & ' + str(names[-1])
    elif len(names) == 2:
        return ' & '.join(names)
    elif len(names) == 1:
        return names[0]
    else:
        return ''


def make_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


if __name__ == '__main__':
    # todo: implement better arg pars. maybe with Plac?
    folder = sys.argv[1]

    skipped_dir = path.join(folder, 'skipped')

    files = sorted(determine_files(folder), key=str.casefold)
    for file in files:
        handle_file(file)

# todo: preview video with vlc while editing?

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
