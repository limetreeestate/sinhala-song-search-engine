import json

# with open("sinhala_songs_corpus.json", "r", encoding="utf-8") as f:
#     text = f.read()
#     print(text)
#     text = text.replace("\n", '\\' + 'n ')
#
# with open("sinhala_songs_corpus.json", "w", encoding="utf-8") as f:
#     f.write(text)

with open("sinhala_songs_corpus.json", "r", encoding="utf-8") as f:
    text = f.read()
    data = json.loads(text)
    for d in data:
        d["track_rating"] = int(d["track_rating"])
        d["artist_rating"] = int(d["track_rating"])
    text = text.replace("\n", '\\' + 'n ')

with open("sinhala_songs_corpus.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
