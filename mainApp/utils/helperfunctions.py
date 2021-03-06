from django.contrib.auth.models import User
from PIL import Image


def is_valid_image(photo):
    """uses Pillow to check whether file is an image"""
    try:
        image = Image.open(photo)
        valid_formats = ['jpeg', 'jpg', 'png']
        if image.format.lower() in valid_formats:
            return True
        else:
            return False
    except:
        return False


def create_response_scelet(status, message, data):
    response = dict()
    response['status'] = status
    response['messages'] = message
    response['data'] = data
    return response


def validate_user_registration(username, pswd, conf_pswd, photo):
    """
    :param username: str
    :param pswd: str
    :param conf_pswd: str
    :param photo: file or none
    :return: {valid: bool,  responseData: dict}
    """
    response_data = dict()

    if User.objects.filter(username=username):
        response_data['username'] = u"This username already exist"
    if pswd != conf_pswd:
        response_data['password'] = u"Passwords to do match"
    if photo and photo.size > (4096*1024):
        response_data["photo"] = u"Avatar size shouldn't be greater than 4MB. "
    if photo and not is_valid_image(photo):
        if 'photo' in response_data:
            response_data["photo"] += u"Supported formats are 'jpeg', 'jpg', 'png'"
        else:
            response_data["photo"] = u"Supported formats are 'jpeg', 'jpg', 'png'"

    if response_data:
        return {"is_valid": False, "responseData": response_data}
    else:
        return {"is_valid": True, "responseData": response_data}


def get_pool_avg_hashrate(obj):
    """
    :param obj: {'h1': '1277.8', 'h3': '1241.9', 'h6': '1233.4', 'h12': '1093.0', 'h24': '996.2'} example
    :return:  as old avg as possible avarage as float
    """
    value = 0.0
    list_of_keys = list(obj)
    list_of_keys.reverse()
    for key in list_of_keys:
        value = float(obj[key])
        if value != 0.0:
            return value
    return value


