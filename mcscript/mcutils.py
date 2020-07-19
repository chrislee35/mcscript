# -*- coding: utf-8 -*-
import re
import ast
import json

class MCUtils:
    @staticmethod
    def convertMinecraftJson(text):
    	r"""
    	Convert Minecraft json string into standard json string and json.loads() it
    	Also if the input has a prefix of "xxx has the following entity data: " it will automatically remove it, more ease!
    	Example available inputs:
    	- Alex has the following entity data: {a: 0b, big: 2.99E7, c: "minecraft:white_wool", d: '{"text":"rua"}'}
    	- {a: 0b, big: 2.99E7, c: "minecraft:white_wool", d: '{"text":"rua"}'}
    	- [0.0d, 10, 1.7E9]
    	- {Air: 300s, Text: "\\o/..\""}
    	- "hello"
    	- 0b

    	:param str text: The Minecraft style json string
    	:return: Parsed result
    	"""

    	# Alex has the following entity data: {a: 0b, big: 2.99E7, c: "minecraft:white_wool", d: '{"text":"rua"}'}
    	# yeet the prefix
    	text = re.sub(r'^.* has the following entity data: ', '', text)  # yeet prefix

    	# {a: 0b, big: 2.99E7, c: "minecraft:white_wool", d: '{"text":"rua"}'}
    	# remove letter after number
    	text = re.sub(r'(?<=\d)[a-zA-Z](?=(\D|$))', '', text)

    	# {a: 0, big: 2.99E7, c: "minecraft:white_wool", d: '{"text":"rua"}'}
    	# add quotation marks to all
    	text = re.sub(r'([a-zA-Z.]+)(?=:)', '"\g<1>"', text)

    	# {"a": 0, "big": 2.99E7, "c": ""minecraft":white_wool", "d": '{"text":"rua"}'}
    	# remove unnecessary quotation created by namespaces
    	list_a = re.split(r'""[a-zA-Z.]+":', text)  # split good texts
    	list_b = re.findall(r'""[a-zA-Z.]+":', text)  # split bad texts
    	result = list_a[0]
    	for i in range(len(list_b)):
    		result += list_b[i].replace('""', '"').replace('":', ':') + list_a[i + 1]

    	# {"a": 0, "big": 2.99E7, "c": "minecraft.white_wool", "d": '{"text":"rua"}'}
    	# process apostrophe string
    	text = ''.join([i for i in MCUtils.mcSingleQuotationJsonReader(result)])

    	# {"a": 0, "big": 2.99E7, "c": "minecraft.white_wool", "d": "{\"text\": \"rua\"}"}
    	# finish
    	return json.loads(text)

    @staticmethod
    def mcSingleQuotationJsonReader(data):
    	part = data  # type: str
    	count = 1
    	while True:
    		spliter = part.split(r"'{", 1)  # Match first opening braces
    		yield spliter[0]
    		if len(spliter) == 1:
    			return  # No more
    		else:
    			part_2 = spliter[1].split(r"}'")  # Match all closing braces
    			index = 0
    			res = MCUtils.jsonCheck("".join(part_2[:index + 1]))
    			while not res:
    				index += 1
    				if index == len(part_2):
    					raise RuntimeError("Out of index")  # Looks like illegal json string
    				res = MCUtils.jsonCheck("".join(part_2[:index + 1]))
    			j_dict = ""
    			while res:
    				# Is real need?
    				j_dict = res
    				index += 1
    				if index == len(part_2):
    					break  # Yep, is real
    				res = MCUtils.jsonCheck("".join(part_2[:index + 1]))

    			yield j_dict  # Match a json string

    		# Restore split string
    		part_2 = part_2[index:]
    		part = part_2[0]
    		if len(part_2) > 1:
    			for i in part_2[1:]:
    				part += "}'"
    				part += i
    		count += 1

    @staticmethod
    def jsonCheck(j):
    	checking = "".join(["{", j, "}"])
    	try:
    		# Plan A
    		# checking = checking.replace("\"", "\\\"")
    		# checking = checking.replace("\'","\\\'")
    		# checking = checking.replace("\\n", "\\\\n")
    		checking = checking.replace(r'\\', "\\")
    		res = json.loads(checking)
    	except ValueError:
    		try:
    			# Plan B
    			res = ast.literal_eval(checking)
    		except:
    			return False

    	data = json.dumps({"data": json.dumps(res)})
    	return data[9:-1]
