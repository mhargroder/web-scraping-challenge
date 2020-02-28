from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars



app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/planets_db"
mongo = PyMongo(app)



@app.route("/")

def index():

	mars_data = mongo.db.mars.find_one()
	return render_template('index.html', data = mars_data)

@app.route("/scrape")
def scraper():
	
    scrape_mars.scrape()
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)
