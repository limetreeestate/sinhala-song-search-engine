import requests
import json


def classify_query(q):
    """
    Classify a given query string based on several rules
    :param q: Query string
    :return: A string representing the query type
    """
    q = q.lower()
    cls = ["general"]

    if "ගේ" in q and "හොඳම" in q or "හොඳම" in q:
        cls = ['top']

    if "අලුත්" in q or "නව" in q:
        cls += ["recent"]

    if "lyrics" in q or "පදවැල" in q:
        cls = ["lyrics"]

    if "album" in q or "ඇල්බම" in q:
        cls += ["album"]

    if "artist" in q or "කලාකරු" in q:
        cls += ["artist"]

    if "සිංදු" in q:
        cls += ["song"]

    return cls


def _prepare_query_params(q, filters, cls):
    """
    Prepare the POST request body to use as parameters for ElasticSearch using the query string depending on the
     determined query type
    :param q: Query string
    :param cls: Query type (string)
    :return: A dictionary containing the parameters to use with ElasticSearch Search API
    """
    print(cls)
    q = q.lower()
    query = q[:]
    body = dict({
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["track_name_si^2", "album_name_si", "artist_name_si^2", "lyrics"],
                "fuzziness": 2
            }
        },
        "size": 15,
        "_source": ["track_name_si", "album_name_en", "album_name_si", "artist_name_en", "artist_name_si"],
    })

    if 'top' in cls:
        query = query.replace("ගේ", "")
        query = query.replace("හොඳම", "")
        n = [int(s) for s in query.split(" ") if s.isdigit()]
        body["query"]["multi_match"]["query"] = query

        print(n)
        if n != []:
            body["size"] = n[-1]
            print(n)
            query = query.replace(str(n[-1]), "")



    if "recent" in cls:
        query = query.replace("අලුත්", "")
        query = query.replace("නව", "")
        body["query"]["multi_match"]["query"] = query

    if "lyrics" in cls:
        #Assumed searching through mainly song name
        query = query.replace("lyrics", "")
        query = query.replace("පදවැල", "")
        body["size"] = 1
        body["query"]["multi_match"]["query"] = query
        body["query"]["multi_match"]["fields"] = ["track_name_si^2", "album_name_si", "artist_name_si^3"]
        body["_source"] += ["lyrics"]

    if "album" in cls:
        #Assumed searching through mainly artist name or a track name
        query = query.replace("album", "")
        query = query.replace("ඇල්බමය", "").replace("ඇල්බම", "")
        body["query"]["multi_match"]["query"] = query
        body["query"]["multi_match"]["fields"] = ["track_name_si", "artist_name_si^2"]
        body["_source"] = ["album_name_en", "album_name_si", "artist_name_en", "artist_name_si",
                                    "track_rating", "artist_rating"]

    if "artist" in cls:
        #Assumed searching through mainly song name
        query = query.replace("artist", "")
        query = query.replace("ඇල්බමය", "").replace("ඇල්බම", "")
        body["query"]["multi_match"]["query"] = query
        body["query"]["multi_match"]["fields"] = ["track_name_si^2", "album_name_si^2", "lyrics"]
        body["_source"] = ["artist_name_en", "artist_name_si", "artist_rating"]

    if "song" in cls:
        #Assumed searching through mainly album name or artist name
        query = query.replace("සිංදුව", "").replace("සිංදු", "")
        body["query"]["multi_match"]["query"] = query
        body["query"]["multi_match"]["fields"] = ["artist_name_si^2", "album_name_si^2", "lyrics"]
        body["_source"] = ["track_name_si", "album_name_en", "album_name_si", "artist_name_en",
                                    "artist_name_si", "track_rating"]

    if cls == ["general"]:
        #Assumed mainly searching general information such as searching through a lyiric to find a song name, or artist by song name etc.
        # print(body["query"])
        body["query"]["multi_match"]["type"] = "phrase"
        body["query"]["multi_match"]["slop"] = 3
        body["_source"] += ["lyrics"]
        del body["query"]["multi_match"]["fuzziness"]

    # if filters != None:
    #     fs = filters.split(":")
    #     if len(fs) > 1:
    #         body["query"]["bool"] = {"filter": None}
    #         if fs[0] == "artist":
    #             body["query"]["bool"]["filter"] = [{"term": {"artist_name_si": fs[1]}}]
    #         if fs[0] == "album":
    #             body["query"]["bool"]["filter"] = [{"term": {"album_name_si": fs[1]}}]
    #         if fs[0] == "song_rating":
    #             body["query"]["bool"]["filter"] = [{"range": {"track_rating": {"gte": int(fs[1])}}}]
    #         if fs[0] == "artist_rating":
    #             body["query"]["bool"]["filter"] = [{"range": {"artist_rating": {"gte": int(fs[1])}}}]

    return body


def _search_index(params, URL):
    """
    Search ElasticSearch index using given parameters
    :param params: ElasticSearch Search API query parameters
    :return: HTTP POST response
    """
    URL += "/sinhala_songs/_doc/"
    # print(json.dumps(params, ensure_ascii=False))
    r = requests.post(url=URL, json=params)

    return r.json()


def _iterate_results(results, params):
    for r in results:
        # print(r["_source"])
        for key, val in params.items():
            print(key, r["_source"][val])
        print()


def _display_results(results, filters, cls):
    """
    Prepare output from ElasticSearch to display in accordance to query type and intent
    :param results: Search results (dictionary)
    :param cls: Query type
    :return: None
    """
    # print (results)
    hits = results["hits"]["hits"]

    if 'top' in cls:
        #Sort results based on rating and print
        if "song" in cls:
            sorted_songs = sorted(hits, key=lambda item: item["_source"]["track_rating"])
            _iterate_results(sorted_songs, {"Title:": "track_name_si", "Artist:": "artist_name_si"})
        if "artist" in cls:
            sorted_artists = sorted(hits, key=lambda item: item["_source"]["artist_rating"])
            _iterate_results(sorted_artists, {"Artist: ": "artist_name_si"})

    if "lyrics" in cls:
        _iterate_results(hits, {"Song Lyrics:\n": "lyrics"})

    if "album" in cls:
        _iterate_results(hits, {"Artist:": "artist_name_si", "Album:": "album_name_si"})

    if "artist" in cls:
        _iterate_results(hits, {"Artist:": "artist_name_si"})

    if "song" in cls:
        _iterate_results(hits, {"Title:": "track_name_si", "Artist:": "artist_name_si"})

    if cls == ["general"]:
        _iterate_results(hits, {"Title:": "track_name_si", "Artist:": "artist_name_si", "Song Lyrics:\n": "lyrics"})



def get_query():
    with open("conf.json", "r") as conf:
        URL = json.load(conf)["URL"]

    while True:
        input_str = input("What would you like to search? ")
        input_arr = [str(item).strip() for item in input_str.split("-")]

        q = input_arr[0]
        if len(input_arr) > 1:
            filters = input_arr[1]
        else:
            filters = None

        cls = classify_query(q)

        params = _prepare_query_params(q, filters, cls)

        results = _search_index(params, URL)

        _display_results(results, filters, cls)

if __name__ == "__main__":
    get_query()