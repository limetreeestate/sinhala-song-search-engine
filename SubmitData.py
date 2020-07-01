import orjson
import json
import os
import requests
from sys import argv
import time


def submit_data(filename):
    print(filename)

    with open(filename, "r", encoding="utf-8") as song_file:
        song_data = json.load(song_file)

    URL = "http://localhost:9200/sinhala_songs/_doc/"
    for song in song_data:
        r = requests.post(url=URL, json=song)
        print(r.json())
        time.sleep(0.1)

if __name__ == "__main__":
    if len(argv) == 1:
        filename = "sinhala_songs_corpus.json"
    else:
        filename = argv[0]
    submit_data(filename)

