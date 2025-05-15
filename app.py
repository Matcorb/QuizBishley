from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, world! This is online 🎉"

if __name__ == "__main__":
    app.run()