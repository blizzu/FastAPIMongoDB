def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message
    }


def ErrorResponseModel(code, message):
    return f"An error occurred, code= {code}, {message}"