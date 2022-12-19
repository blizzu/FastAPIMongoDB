import pytest
import requests
from app import *
from database import *

item = {
    "name": "test item1",
    "desc": "This is test description",
    "price": 1,
    "category": "cat1"
}

item_update = {
    "name": "update item1",
    "desc": "This is update description",
    "price": 1,
    "category": "cat1"
}

user = {
    "first": "Rychu",
    "last": "Gryps"
}

user_update = {
    "first": "Rychu_update",
    "last": "Gryps_update"
}

URL = 'http://127.0.0.1:8000'

@pytest.fixture
def user_adding():
    user = {
        "first": "Rychu",
        "last": "Gryps",
        "cart": []
    }
    inserted_user = users.insert_one(user)
    yield inserted_user.inserted_id
    users.delete_one({"_id": ObjectId(inserted_user.inserted_id)})


@pytest.fixture
def item_adding():
    item = {
        "name": "test item1",
        "desc": "This is test description",
        "price": 1,
        "category": "cat1",
        "quantity": 0

    }
    inserted_item = products.insert_one(item)
    yield inserted_item.inserted_id
    products.delete_one({"_id": ObjectId(inserted_item.inserted_id)})



def user_finder(id):
    f_user = users.find_one({"_id": ObjectId(id)})
    return user_parser(f_user)


def item_finder(id):
    f_item = products.find_one({"_id": ObjectId(id)})
    return item_parser_return(f_item)


def product_finder(user_id, product_id):
    our_user = users.find_one({"_id": ObjectId(user_id), "cart._id": ObjectId(product_id)})
    if our_user:
        cart = our_user['cart']
        product = next((item for item in cart if item["_id"] == ObjectId(product_id)), None)
        return product
    else:
        return None


def cart_creator(user_id, product_id, quantity):
    user = users.find_one({"_id": ObjectId(user_id)})
    cart = user["cart"]
    product = products.find_one({"_id": ObjectId(product_id)})
    product.update({"quantity": quantity})
    cart.append(product)
    users.update_one({"_id": ObjectId(user_id)}, {"$set": {"cart": cart}})
    return product_finder(user_id, product_id)


class TestUserOnly:



    def test_add_user_to_database(self):
        r = requests.post(f"{URL}/user/", json=user)
        json = r.json()
        id = json['data'][0]['_id']
        assert json['data'][0] == user_finder(id)
        users.delete_one({"_id": ObjectId(id)})

    def test_update_users_data(self, user_adding):
        id = user_adding
        param = {"id": id}
        r = requests.put(f"{URL}/user-update/", params=param, json=user_update)
        json = r.json()
        result = json['data'][0]
        assert result == user_finder(id)

    def test_get_all_users_fstring(self):
        r = requests.get(f"{URL}/get-all-users-fstring/")
        json = r.json()
        result = json['data']
        list_of_users = []
        all_users = users.find()
        for user in all_users:
            a = f"User: {user_parser(user)} Cart: {cart_parser(user['cart'])}"
            list_of_users.append(a)
        assert result == list_of_users

    def test_get_all_users(self):
        r = requests.get(f"{URL}/get-all-users/")
        json = r.json()
        result = json['data']
        list_of_users = []
        all_users = users.find()
        for user in all_users:
            list_of_users.extend([user_parser(user), cart_parser(user["cart"])])
        assert result == list_of_users

    def test_delete_user(self, user_adding):
        id = user_adding
        param = {"id": id}
        r = requests.delete(f"{URL}/delete-user/", params=param)
        user = users.find_one({"_id": ObjectId(id)})
        assert user is None

    def test_get_user(self, user_adding):
        id = user_adding
        param = {"id": id}
        r = requests.get(f"{URL}/get-user/", params=param)
        json2 = r.json()
        result = json2['data']
        test_user = user_finder(id)
        assert result == test_user


class TestItemOnly:

    def test_add_product_to_database(self):
        r = requests.post(f"{URL}/item/", json=item)
        json = r.json()
        id = json['data'][0]['_id']
        assert json['data'][0] == item_finder(id)
        products.delete_one({"_id": ObjectId(id)})

    def test_update_items_data(self, item_adding):
        id = item_adding
        param = {"id": id}
        r = requests.put(f"{URL}/item-update/", params=param, json=item_update)
        json = r.json()
        result = json['data'][0]
        assert result == item_finder(id)

    def test_get_all_items(self):
        r = requests.get(f"{URL}/get-all-items/")
        json = r.json()
        result = json['data']
        list_of_items = []
        all_items = products.find()
        for item in all_items:
            list_of_items.append(item_parser_return(item))
        assert result == list_of_items

    def test_get_item(self, item_adding):
        id = item_adding
        param = {"id": id}
        r = requests.get(f"{URL}/get-item/", params=param)
        json = r.json()
        result = json['data']
        test_item = item_finder(id)
        assert result == test_item

    def test_delete_item(self, item_adding):
        id = item_adding
        param = {"id": id}
        r = requests.delete(f"{URL}/delete-item/", params=param)
        our_item = products.find_one({"_id": ObjectId(id)})
        assert our_item is None


class TestCart:

    def test_add_item_to_cart(self, user_adding, item_adding):
        user_id = user_adding
        product_id = item_adding
        param = {"user_id": user_id, "product_id": product_id}
        n = 1
        while n < 10:
            requests.put(f"{URL}/add-item-to-cart/", params=param)
            product = product_finder(user_id, product_id)
            assert product["quantity"] == n
            n += 1

    def test_delete_tem_from_cart_one(self, user_adding, item_adding):
        user_id = user_adding
        product_id = item_adding
        param = {"user_id": user_id, "product_id": product_id}
        item = cart_creator(user_id, product_id, 10)
        n = item["quantity"]
        while n > 0:
            requests.put(f"{URL}/delete-item-from-cart-one/", params=param)
            product = product_finder(user_id, product_id)
            if product is None:
                pass
                break
            else:
                assert product["quantity"] == n - 1
                n -= 1

    def test_delete_item_from_cart_all(self, user_adding, item_adding):
        user_id = user_adding
        product_id = item_adding
        param = {"user_id": user_id, "product_id": product_id}
        cart_creator(user_id, product_id, 10)
        requests.put(f"{URL}/delete-item-from-cart-all/", params=param)
        item = product_finder(user_id, product_id)
        assert item is None

    def test_empty_cart(self, user_adding, item_adding):
        user_id = user_adding
        product_id = item_adding
        cart_creator(user_id, product_id, 1)
        param = {"id": user_id}
        r = requests.put(f"{URL}/empty-cart/", params=param)
        user = f_user = users.find_one({"_id": ObjectId(user_id)})
        assert user['cart'] == []

    def test_get_user_cart(self, user_adding, item_adding):
        user_id = user_adding
        product_id = item_adding
        cart_creator(user_id, product_id, 1)
        user = users.find_one({"_id": ObjectId(user_id)})
        cart = cart_parser(user['cart'])
        param = {"id": user_id}
        r = requests.get(f"{URL}/get-user-cart/", params=param)
        json2 = r.json()
        result = json2['data']
        assert result == cart


# Negative tests
class TestABC:

    flawed_item = {
        "name": "item1",
        "desc": "This is the description"
    }

    flawed_user_id = '111b7f713b989234b9f71111'


    def test_add_flawed_product_to_database(self):
        r = requests.post(f"{URL}/item/", json=self.flawed_item)
        assert r.status_code == 422


    def test_update_users_data_using_flawed_user_id(self):
        id = self.flawed_user_id
        param = {"id": id}
        r = requests.put(f"{URL}/user-update/", params=param, json=user_update)
        result = r.json()
        code = r.status_code
        assert result == "An error occurred, code= 400, User can't be updated"
        assert code == 400



class TestExperiments:


    @pytest.fixture
    def cart_adding(self):
        """Made for the sake of making it"""
        user = {
            "first": "Rychu",
            "last": "Gryps",
            "cart": []
        }
        inserted_user = users.insert_one(user)
        item = {
            "name": "test item1",
            "desc": "This is test description",
            "price": 1,
            "category": "cat1",
            "quantity": 0
        }
        inserted_item = products.insert_one(item)
        user = users.find_one({"_id": ObjectId(inserted_user.inserted_id)})
        cart = user["cart"]
        product = products.find_one({"_id": ObjectId(inserted_item.inserted_id)})
        product.update({"quantity": 10})
        cart.append(product)
        users.update_one({"_id": ObjectId(inserted_user.inserted_id)}, {"$set": {"cart": cart}})
        yield [product_finder(inserted_user.inserted_id, inserted_item.inserted_id), inserted_user.inserted_id,
               inserted_item.inserted_id]
        users.delete_one({"_id": ObjectId(inserted_user.inserted_id)})
        products.delete_one({"_id": ObjectId(inserted_item.inserted_id)})

    def test_empty_cart_experiment(self,cart_adding):
        user_id = cart_adding[1]
        param = {"id": user_id}
        r = requests.put(f"{URL}/empty-cart/", params=param)
        user = users.find_one({"_id": ObjectId(user_id)})
        assert user['cart'] == []