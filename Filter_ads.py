import pymongo
import random

cluster = pymongo.MongoClient(
    "mongodb+srv://somesh:icdeskillstack@cluster0.odqp5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["ICDE_DataBase"]
collection = db["Advertisement"]

ads = []


class FilterAds:
    def filter_advertisements(self):
        ad_themes = ["Sports", "Food", "Electronics", "Beauty"]
        for theme in ad_themes:
            ad = collection.find_one({"Advertisement_theme": theme})
            del ad["_id"]
            del ad["Advertisement_theme"]
            for i in range(1, 6):
                key = theme + "_ad_" + str(i)
                ads.append(ad[key])
        random.shuffle(ads)
        return ads
