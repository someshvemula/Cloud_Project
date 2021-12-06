from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, RegistrationForm_Advertiser
import requests
from monkeylearn import MonkeyLearn
from flask_login import LoginManager
from threading import Thread
import time
from Filter_ads import FilterAds

application = Flask(__name__)
application.config['SECRET_KEY'] = 'F5TH7654KI890PL75RFV76TG78ILF421'
news_articles = []
analysed_news_articles = []
user_logedin = False
news_length = 20
news_ads_data = []
news_ads_data_dr = []


class SentimentAnalysis:
    analysed_news = []
    model_ID = "cl_pi3C7JiL"
    api_Keys = ["f67941bd51156e9dc5cf556172ca4f05ccc1bfed",
                "75b70200f0ce8c46d7fb684bc18dd7aaca767549",
                "ed862c8971c0139a5113690d79b72293beb643eb",
                "52df758ccca3915818e479e237a06750201271a4",
                "3ef85671ca0a49ca1195d536fa9138fd808fd186",
                "02165944dcc2c40ea04b7b329ff63ab5e599a01d", "18dfd797f505f0ba1b1312c117045cb67a4bc756",
                "3a3de27734169f44a0c7ea0c9f32436134bd1f52", "d8bb505db1fea3b5d9cb034e544a4938adf5447b",
                "11738dca2069de2e31a6f8484ce3cb3771dea973", "ba3f7fc8f73e3466616e3239d869dfb6768b4154"]

    def api_call(self, news, api_key):
        result = MonkeyLearn(api_key).classifiers.classify(SentimentAnalysis.model_ID, [news["title"]])
        news["sentiment"] = result.body[0]["classifications"][0]["tag_name"]
        news["sentiment_accuracy"] = result.body[0]["classifications"][0]["confidence"]
        SentimentAnalysis.analysed_news.append(news)

    def news_analysis(self, raw_news):
        api = 0
        SentimentAnalysis.analysed_news = []
        for news in raw_news:
            if api >= len(SentimentAnalysis.api_Keys):
                api = 0
            # Thread(target=SentimentAnalysis.api_call(self, news, SentimentAnalysis.api_Keys[api])).start()
            SentimentAnalysis.api_call(self, news, SentimentAnalysis.api_Keys[api])
            api += 1


def remove_duplicates(news):
    news_dr = []
    for page in news:
        if page not in news_dr:
            news_dr.append(page)
        else:
            continue
    return news_dr


def get_news(country):
    websitetitle = "News On The Go"
    news_articles.clear()
    global news_ads_data
    news_ads_data.clear()
    api_key = "e60f42f7042f4c5aa06a003c9ebe8d04"
    link = "https://newsapi.org/v2/top-headlines?country=" + country + "&apiKey=" + api_key
    headlines = requests.get(link).json()
    for k in range(len(headlines["articles"])):
        if headlines["articles"][k]["urlToImage"] is not None:
            news = {"author": headlines["articles"][k]["source"]["name"], "title": headlines["articles"][k]["title"],
                    "content": headlines["articles"][k]["content"],
                    "date_posted": headlines["articles"][k]["publishedAt"],
                    "url": headlines["articles"][k]["url"], "url_image": headlines["articles"][k]["urlToImage"],
                    "article_number": k, "websitetitle": websitetitle,
                    "sentiment": " ", "sentiment_accuracy": " "}
            news_articles.append(news)
    while True:
        if len(news_articles) > news_length:
            news_articles.pop()
        else:
            break
    object_sentiment = SentimentAnalysis()
    object_sentiment.news_analysis(news_articles)
    global analysed_news_articles
    analysed_news_articles = SentimentAnalysis.analysed_news
    object_filter_ads = FilterAds()
    advertisements = object_filter_ads.filter_advertisements()
    for i in range(0, len(analysed_news_articles)):
        news = analysed_news_articles[i]
        ads = advertisements[i]
        news["ad_tagline"] = ads["ad_tagline"]
        news["ad_Image_url"] = ads["ad_Image_url"]
        news["ad_landing_url"] = ads["ad_landing_url"]
        news_ads_data.append(news)
    news_ads_data = remove_duplicates(news_ads_data)


@application.route("/")
@application.route("/home")
def home():
    get_news(country="us")
    return render_template('home.html', news_articles=news_ads_data, user_logedin=user_logedin)


@application.route("/ca")
def home0():
    get_news(country="ca")
    return render_template('home.html', news_articles=news_ads_data)


@application.route("/in")
def home1():
    get_news(country="in")
    return render_template('home.html', news_articles=news_ads_data)


@application.route("/us")
def home2():
    get_news(country="us")
    return render_template('home.html', news_articles=news_ads_data)


@application.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@application.route("/register_advertiser", methods=['GET', 'POST'])
def register_advertiser():
    form = RegistrationForm_Advertiser()
    if form.validate_on_submit():
        flash(f'Account created for {form.company_name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register_advertiser.html', title='Register', form=form)


@application.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'somesh@gmail.com' and form.password.data == 'somesh':
            flash('You have been logged in!', 'success')
            global user_logedin
            user_logedin = True
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    application.run(debug=True)
