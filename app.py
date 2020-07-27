from flask import Flask, render_template
from flask_pymongo import PyMongo
import scraping

# Setting Flask
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# Home route
@app.route("/")
def index():
   mars = mongo.db.mars.find_one()
   hemi_list = list(mongo.db.hemispheres.find({}))
   hemispheres = mongo.db.hemispheres.find_one()
   return render_template("index.html", mars=mars, hemi_list=hemi_list)

# Scrapping route
@app.route("/scrape")
def scrape():
   mars = mongo.db.mars
   mars_data = scraping.scrape_all()
   hemispheres = mongo.db.hemispheres
   mars_data, hemi_list = scraping.scrape_all()
   mars.update({}, mars_data, upsert=True)
   for hemi in hemi_list:
      hemispheres.update_one(
         {'title':hemi.get('title')},
         {
            '$set':{
               'img_url':hemi.get('img_url')
            }
         },
         upsert=True)

   return "Scraping Successful!"

if __name__ == "__main__":
   app.run()