from flask import Blueprint, render_template, request, redirect, session, flash
import requests
from datetime import datetime

views = Blueprint("views",__name__)
api_key = "321d8e7f20aab42c0cd011cd3d17461a"

@views.route("/",methods=["POST","GET"])
def home():
    if request.method == "POST":
        city = request.form.get("city")
        return redirect(f"/search?q={city}")

    if "saved_locations" in session:
        saved_locations = session["saved_locations"]
    else:
        session.permanent = True
        session["saved_locations"] = []
        saved_locations = []

    weather_data = []
    for location in saved_locations:
        lat = location["lat"]
        lon = location["lon"]
        weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}").json()
        weather_data.append(weather)

    return render_template("home.html",saved_locations=saved_locations,weather_data=weather_data)

@views.route("/remove")
def remove_location():
    args = request.args
    lat = args.get("lat")
    lon = args.get("lon")

    if "saved_locations" in session:
        saved = session["saved_locations"]
        for location in saved:
            if location["lat"] == lat and location["lon"] == lon:
                saved.remove(location)
                flash("Location removed from home",category="success")
                break
        session["saved_locations"] = saved
        
    return redirect("/")

@views.route("/save")
def save_location():
    args = request.args
    name = args.get("name")
    state = args.get("state")
    country = args.get("country")
    lat = args.get("lat")
    lon = args.get("lon")
    search = args.get("search")
    required_args = [args,name,state,country,lat,lon,search]

    invalid = False
    for arg in required_args:
        if arg == None:
            invalid = True
            break
    
    if not invalid:
        if "saved_locations" in session:
            saved = session["saved_locations"]
            if {"name":name,"state":state,"country":country,"lat":lat,"lon":lon} not in saved:
                saved.append({"name":name,"state":state,"country":country,"lat":lat,"lon":lon})
                session["saved_locations"] = saved
                flash("Location added to home",category="success")
        else:
            session.permanent = True
            session["saved_locations"] = [{"name":name,"state":state,"country":country,"lat":lat,"lon":lon}]
            flash("Location added to home",category="success")
    else:
        flash("Can't remove location",category="error")
        return redirect("/")

    return redirect(f"/search?q={search}")

@views.route("/search", methods=["POST","GET"])
def search():
    if request.method == "POST":
        city = request.form.get("city")
        return redirect(f"/search?q={city}")

    args = request.args
    search = args.get("q")

    places = []
    try:
        geocoding_response = requests.get(f"https://api.openweathermap.org/geo/1.0/direct?q={search}&limit=5&appid={api_key}").json()
        for place in geocoding_response:
            place_info = {"name":place["name"],"state":place["state"],"country":place["country"],"lat":place["lat"],"lon":place["lon"]}
            place_added = False
            
            for place in places:
                if place["name"] == place_info["name"] and place["state"] == place_info["state"] and place["country"] == place_info["country"]:
                    place_added = True
                    break
            
            if not place_added:
                places.append(place_info)


    except:
        places = None

    return render_template("search.html",places=places,search=search)

@views.route("/city/<city_name>")
def city_weather(city_name):
    args = request.args
    lat = args.get("lat")
    lon = args.get("lon")
    tab = args.get("tab")

    try:
        weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}").json()
        description = weather["weather"][0]["description"]
        sunrise = datetime.utcfromtimestamp(weather["sys"]["sunrise"]).strftime('%H:%M')
        sunset = datetime.utcfromtimestamp(weather["sys"]["sunset"]).strftime('%H:%M')
        name_dict = {"name":city_name}
    except:
        weather = []
        sunrise = 0
        sunset = 0

    return render_template("weather.html",weather=weather,name=name_dict,tab=tab,lat=lat,lon=lon,sunrise=sunrise,sunset=sunset)
