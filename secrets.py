"""
import requests
import base64
import six
"""
USER_CLIENT_ID = "884385fad8034a09aafaccebdea4af0f"
USER_CLIENT_SECRET = "44886e17d67f48598b9e72e53855c899"
USER_REDIRECT_URI = "https://httpbin.org/anything"
"""
code = "AQDzvCNh0CjxU9yhJJtfOnWTsJatEOLDvw-eDglewOoYQo8-1BlyeONhcqdD5Lo5o5zhzIqSW2QKRhzjNRe9I5xN85dYICAAapBpvVMW0_c4_sLQEBI8k-k7zuY0jLIncZRS84locXNRc_fUsnChnam0Kvksnn0II2KwezDQ7xWwFB2C_xL2RLmyaw_5RjfufkvMma7DYI9G8mmi08_8_kgQsaE"
"""
spotify_user_id = "5nukhuv7dgru66ng5n017tszf"
spotify_token = ""
"""
url = "https://accounts.spotify.com/api/token"
headers = {}
body = {
    "grant_type": "auntorization_code",
    "code": code,
    "redirect_uri": USER_REDIRECT_URI,
}

message = f"{USER_CLIENT_ID}:{USER_CLIENT_SECRET}"
messageBytes = message.encode("ascii")
base64Bytes = base64.b64encode(messageBytes)
base64Message = base64Bytes.decode("ascii")

x = base64.b64encode(six.text_type(USER_CLIENT_ID + ":" + USER_CLIENT_SECRET).encode("ascii")).decode("ascii")

headers['Authorization'] = "Basic %s" % x

r = requests.post(url, headers=headers, params=body)
print(r)
#print(headers['Authorization'])
#print(x  ,  base64Message)
"""