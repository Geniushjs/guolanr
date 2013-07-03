import json

menu = []

fruit = dict()
fruit["name"] = "apple"
fruit["price"] = 1.5
fruit["count"] = 2

menu.append(fruit)

print json.dumps(menu)
