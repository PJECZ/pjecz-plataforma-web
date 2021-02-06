"""
Firebase Auth
"""
import os


firebase_auth = {
    "apiKey": os.environ.get("FIREBASE_APIKEY"),
    "authDomain": os.environ.get("FIREBASE_AUTHDOMAIN"),
    "databaseURL": os.environ.get("FIREBASE_DATABASEURL"),
    "projectId": os.environ.get("FIREBASE_PROJECTID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGEBUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGINGSENDERID"),
    "appId": os.environ.get("FIREBASE_APPID"),
    "measurementId": os.environ.get("FIREBASE_MEASUREMENTID"),
}
