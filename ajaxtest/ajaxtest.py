#!/usr/bin/python3
print("Content-type: text/html\n")
from jinja2 import Template
from cgi import FieldStorage
storage = FieldStorage()
with open("keytest.html", "r") as file:
    text = file.read()
print(Template(text).render(user_number=storage.getfirst("user_number")))
