from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template('home_page.html')

@app.route("/documentation")
def documentation():
    return render_template('documentation.html')

if __name__=="__main__":
    app.run(host="localhost", port=5000, debug=True)