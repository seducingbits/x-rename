import os
import os.path
from dataclasses import dataclass
from os import path
import sys
from typing import List
import requests
from bs4 import BeautifulSoup
import re
import win32console  # needs pywin32
import time

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


@dataclass
class Scene:
    title: str
    performers: List[str]
    number: int


@dataclass
class Movie:
    title: str
    year: str
    date: str
    scenes: List[Scene]


def get_scene_performers(div):
    try:
        return list(map(lambda performer: performer.text, div.parent.find_all('a')))
    except AttributeError:
        return []


def get_movie_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    title = soup.find('h1').text.strip().split("\n")[0].strip()
    try:
        year = soup.find('div', {'class': 'item-info'}).find('small').text
    except AttributeError:
        year = ""
    studio = soup.find('div', {'class': 'item-info'}).find('a', {'label': 'Studio'}).text
    date = ""  # todo

    scene_rows = list(map(lambda row: row.parent, soup.find_all('div', {'class': 'col-sm-6 m-b-1'})))
    scenes = []
    for i, row in enumerate(scene_rows):
        scene_title = row.find('a', {'label': 'Scene Title'}).text.strip()
        scene_performers = get_scene_performers(row.find(text=re.compile(r'Starring:')))
        scenes.append(Scene(scene_title, scene_performers, i + 1))

    #print(title)
    # print(year)
    #print(studio)
    #print(scenes)
    return Movie(title, year, date, scenes)


def determine_files(folder):
    return list(filter(lambda element: path.isfile(path.join(folder, element)), os.listdir(folder)))


def handle_file(folder, index, file, data):
    index = ask_index(index, file)
    if index >= 0:
        new_filename = get_new_filename(index, file, data)
        rename(folder, file, new_filename)


def ask_index(index, filename):
    #input = input_def('ENTER SCENE NUMBER FOR "' + filename + '"\nIndex: ', index + 1)
    input = input_def('ENTER SCENE NUMBER FOR "' + filename + ' (0 to skip)"\nIndex: ', "")
    time.sleep(0.5)
    return int(input) - 1


def get_new_filename(index, file, data):
    scene = data.scenes[index]

    filename = '{title}{year} - Scene {index:02d}{performer}{scene_title}{ext}'.format(
        title=data.title,
        year=build_year_string(data.year),
        index=scene.number,
        performer=build_performer_string(scene.performers),
        scene_title=' - ' + scene.title,
        ext=path.splitext(file)[-1]
    )
    filename = re.sub(r'[<>/\\|?*]', '', filename)
    filename = re.sub(r'"', '\'', filename)
    filename = re.sub(r':', ' -', filename)
    return filename


def build_year_string(year):
    if year == "":
        return ""
    else:
        return f" {year}"


def build_performer_string(performers):
    if len(performers) > 2:
        return ' - ' + ', '.join(performers[:-1]) + ' & ' + str(performers[-1])
    elif len(performers) == 2:
        return ' - ' + ' & '.join(performers)
    elif len(performers) == 1:
        return ' - ' + performers[0]
    else:
        return ''


def rename(folder, file, new_filename):
    os.rename(path.join(folder, file), path.join(folder, new_filename))
    print(f'Rename {file} to {new_filename}')


if __name__ == '__main__':
    folder = sys.argv[1]
    #movie_url = sys.argv[2]

    files = determine_files(folder)
    files.sort()

    for index, file in enumerate(files):
        print()
        movie_url = input(f'URL for {file}: ')
        data = get_movie_data(movie_url)
        handle_file(folder, index, file, data)
