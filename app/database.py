from pymongo import MongoClient


mydb = MongoClient("mongodb://localhost:27017")

shop = mydb["shop"]
users = shop["users"]
products = shop["products"]


def user_parser(user):
    return {
        "_id":  str(user["_id"]),
        "first" : user["first"],
        "last": user["last"],
    }


def cart_parser(list):
    new_list = []
    for item in list:
        new_list.append(item_parser(item))
    return new_list


def item_parser(item):
    return {
        "_id": str(item["_id"]),
        "name": item["name"],
        "desc": item["desc"],
        "price": item["price"],
        "category": item["category"],
        "quantity": item["quantity"]
    }


def item_parser_return(item):
    return {
        "_id": str(item["_id"]),
        "name": item["name"],
        "desc": item["desc"],
        "price": item["price"],
        "category": item["category"]
    }



