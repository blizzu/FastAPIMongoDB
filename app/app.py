from fastapi import FastAPI, Response
from bson.objectid import ObjectId
from models.user import *
from models.item import *
from models.response import *
from database import *

app = FastAPI()


# Creating an item
@app.post("/item/")
def create_product(item: Item):
    inserted_item = products.insert_one(item.dict())
    new_product = products.find_one({"_id": inserted_item.inserted_id})
    if new_product:
        return ResponseModel([item_parser_return(new_product), "Product has been added successfully"],
                             "Product created")
    else:
        ErrorResponseModel(400, "Can't create Product")


# Creating a user
@app.post("/user/")
def create_user(user: User):
    inserted_user = users.insert_one(user.dict())
    new_user = users.find_one({"_id": inserted_user.inserted_id})
    if new_user:
        return ResponseModel([user_parser(new_user), "User has been added successfully"], "User created")
    else:
        ErrorResponseModel(400, "Can't create user")


# Updating item's data
@app.put("/item-update/")
def item_update(id: str, item: UpdateItem, response: Response):
    update = {k: v for k, v in item.dict().items() if v is not None}
    products.update_one({"_id": ObjectId(id)}, {"$set": update})
    updated_product = products.find_one({"_id": ObjectId(id)})
    if updated_product:
        return ResponseModel([item_parser_return(updated_product), f"Product with id = {id} has been"
                                                                   f" updated successfully"], "Update successful")
    else:
        response.status_code = 400
        return ErrorResponseModel(400, "Product can't be updated")


# Updating user's data
@app.put("/user-update/")
def user_update(id: str, user: UpdateUser, response: Response):
    update = {k: v for k, v in user.dict().items() if v is not None}
    users.update_one({"_id": ObjectId(id)}, {"$set": update})
    updated_user = users.find_one({"_id": ObjectId(id)})
    if updated_user:
        return ResponseModel([user_parser(updated_user), f"User with id = {id} has been updated successfully"],
                             "Update successful")
    else:
        response.status_code = 400
        return ErrorResponseModel(400, "User can't be updated")


# Adding item to the cart
@app.put("/add-item-to-cart/")
def add_item_to_cart(user_id: str, product_id: str, response: Response):
    user = users.find_one({"_id": ObjectId(user_id)})
    if user:
        cart = user["cart"]
        product = products.find_one({"_id": ObjectId(product_id)})
        if product:
            if len([x for x in cart if (x['_id'] == ObjectId(product_id))]) > 0:
                updated_cart = [x for x in cart if not (x['_id'] == ObjectId(product_id))]
                our_product = [x for x in cart if (x['_id'] == ObjectId(product_id))][0]
                our_product["quantity"] += 1
                updated_cart.append(our_product)
                users.update_one({"_id": ObjectId(user_id)}, {"$set": {"cart": updated_cart}})
            else:
                product.update({"quantity": 1})
                cart.append(product)
                users.update_one({"_id": ObjectId(user_id)}, {"$set": {"cart": cart}})
            return ResponseModel(f"One instance of item with id = {product_id} has been successfully added to the cart"
                                 f" of user with id = {user_id}", "Item Added")
        else:
            response.status_code = 404
            return ErrorResponseModel(404, f"Product with id = {product_id} does not exist")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"User with id = {user_id} does not exist")


# Delete item from user's cart
@app.put("/delete-item-from-cart-one/")
def delete_item_from_cart_one(user_id: str, product_id: str, response: Response):
    user = users.find_one({"_id": ObjectId(user_id)})
    cart = user["cart"]
    if len([x for x in cart if (x['_id'] == ObjectId(product_id))]) > 0:
        updated_cart = [x for x in cart if not (x['_id'] == ObjectId(product_id))]
        our_product = [x for x in cart if (x['_id'] == ObjectId(product_id))][0]
        our_product["quantity"] -= 1
        updated_cart.append(our_product)
        users.update_one({"_id": ObjectId(user_id)}, {"$set": {"cart": updated_cart}})
        if our_product["quantity"] < 1:
            updated_cart = [x for x in cart if not (x['_id'] == ObjectId(product_id))]
            users.update_one({"_id": ObjectId(user_id)}, {"$set": {"cart": updated_cart}})
        return ResponseModel(f"One instance of item with id = {product_id} has been successfully removed from the cart",
                             "Item deleted")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"Item with id = {product_id} is not in the cart")


# Delete all instances of item from user's cart
@app.put("/delete-item-from-cart-all/")
def delete_item_from_cart_all(user_id: str, product_id: str, response: Response):
    user = users.find_one({"_id": ObjectId(user_id)})
    cart = user["cart"]
    if len([x for x in cart if (x['_id'] == ObjectId(product_id))]) > 0:
        our_product = [x for x in cart if (x['_id'] == ObjectId(product_id))][0]
        updated_cart = [x for x in cart if not (x['_id'] == ObjectId(product_id))]
        users.update_one({"_id": ObjectId(user_id)}, {"$set": {"cart": updated_cart}})
        if our_product not in updated_cart:
            return ResponseModel("All instances of item has been deleted", "Item deleted")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"Item with id = {product_id} is not in the cart")


# Empty user's cart
@app.put("/empty-cart/")
def empty_cart(id: str, response: Response):
    user = users.find_one({"_id": ObjectId(id)})
    cart = user["cart"]
    if len(cart) > 0:
        users.update_one({"_id": ObjectId(id)}, {"$set": {"cart": []}})
        return ResponseModel(f"Cart belonging to user with id = {id} has been emptied ",
                             "Cart has been successfully emptied")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, "Cart is already empty")


# Fetching all users and returning list of fstrings
@app.get("/get-all-users-fstring/")
def get_all_users(response: Response):
    list_of_users = []
    all_users = users.find()
    for user in all_users:
        a = f"User: {user_parser(user)} Cart: {cart_parser(user['cart'])}"
        list_of_users.append(a)
    if len(list_of_users) > 0:
        return ResponseModel(list_of_users, "All users in database")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, "There are no users in database")


# Fetching all users and returning list of dictionaries
@app.get("/get-all-users/")
def get_all_users(response: Response):
    list_of_users = []
    all_users = users.find()
    for user in all_users:
        list_of_users.extend([user_parser(user), cart_parser(user["cart"])])
    if len(list_of_users) > 0:
        return ResponseModel(list_of_users, "All users in database")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, "There are no users in database")


# Fetching all users and returning list of dictionaries
@app.get("/get-all-items/")
def get_all_items(response: Response):
    list_of_items = []
    all_items = products.find()
    for item in all_items:
        list_of_items.append(item_parser_return(item))
    if len(list_of_items) > 0:
        return ResponseModel(list_of_items, "All products in database")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, "There are no products in database")


# Fetching item's data using items' id
@app.get("/get-item/")
def get_item(id: str, response: Response):
    item = products.find_one({"_id": ObjectId(id)})
    if item:
        return ResponseModel(item_parser_return(item), "Product has been found")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"Product with id = {id} does not exist")



# Fetching user's data using users' id
@app.get("/get-user/")
def get_user(id: str, response: Response):
    user = users.find_one({"_id": ObjectId(id)})
    if user:
        return ResponseModel(user_parser(user), "User has been found")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"User with id = {id} does not exist")


# Fetching user's cart
@app.get("/get-user-cart")
def get_user_cart(id: str, response: Response):
    user = users.find_one({"_id": ObjectId(id)})
    if user:
        cart = cart_parser(user["cart"])
        if cart:
            return ResponseModel(cart, "User's cart")
        else:
            response.status_code = 404
            return ErrorResponseModel(404, "Cart is empty")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"User with id = {id} does not exist")


# Delete user from database
@app.delete("/delete-user/")
def delete_user(id: str, response: Response):
    users.delete_one({"_id": ObjectId(id)})
    user = users.find_one({"_id": ObjectId(id)})
    if user:
        return ResponseModel(f"User with id = {id} has been deleted", "Deletion successful")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"User with id = {id} does not exist")


# Delete product from database
@app.delete("/delete-item/")
def delete_item(id: str, response: Response):
    products.delete_one({"_id": ObjectId(id)})
    product = products.find_one({"_id": ObjectId(id)})
    if product:
        return ResponseModel(f"Product with id = {id} has been deleted", "Deletion successful")
    else:
        response.status_code = 404
        return ErrorResponseModel(404, f"Product with id = {id} does not exist")


