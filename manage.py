#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

@app.route('/')
def static_page():
    return render_template('index.html')

@app.route('/search')
def test_reply():
	value = str(request.args.get('value', "DEFAULT VALUE"))
	return_value = value.upper()
    return jsonify(result = "JS said: " + value + " and Flask replied " + return_value)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
