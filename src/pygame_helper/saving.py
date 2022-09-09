import json
from typing import Type,List,Tuple,Dict,Union,Any

"""
This module contains helpful functions to easl save and load objects and more.
"""

# FILE
def save_data_json(dictionary:Dict[Any,Any],file_path:str):
	"""
	Lets you save a json-serializable dictionary to a file.
	"""
	with open(file_path,"w") as save_file:
		json.dump(dictionary, save_file)
		return save_file

def load_data_json(file_path:str)->Dict[Any,Any]:
	"""
	Load and return a json dictionary from a file.
	"""
	with open(file_path,"r") as load_file:
		return json.load(load_file)

# CONVERSION
def convert_object_json(obj:Any,attributes_rules:Dict[Type,List[str]])->dict:
	"""
	Convert an object in to a json-serializable dictionary, following the specified rules.

	You must specify the rules for every other type inside the main object.
	"""
	empty = {}
	if not type(obj) in attributes_rules.keys():
		raise ValueError("Missing rule for "+obj.__class__.__name__)
	for attr in attributes_rules[type(obj)]:
		value = getattr(obj, attr)
		if isinstance(value, (str,int,float,set,bool)) or value == None:
			empty[attr] = value
		elif isinstance(value, list):
			empty[attr] = convert_list_json(value, attributes_rules)
		elif isinstance(value, tuple):
			empty[attr]=convert_tuple_json(value,attributes_rules)
		elif isinstance(value, dict):
			empty[attr]= convert_dict_json(value, attributes_rules)
		else:
			empty[attr] = convert_object_json(value, attributes_rules)
	return empty

def convert_list_json(obj:List[Any],attributes_rules:Dict[Type,List[str]])->list:
	"""
	Replace every non-json-serializable object inside a list to a dictionary, following the specified rules.
	"""
	new = []
	for e in obj:
		if isinstance(e, (str,int,float,set,bool)) or e == None:
			new.append(e)
		elif isinstance(e, list):
			new.append(convert_list_json(e, attributes_rules))
		elif isinstance(e, tuple):
			new.append(convert_tuple_json(e,attributes_rules))
		elif isinstance(e, dict):
			new.append(convert_dict_json(e, attributes_rules))
		else:
			new.append(convert_object_json(e, attributes_rules))
	return new

def convert_tuple_json(obj:tuple,attributes_rules:Dict[Type,List[str]])->tuple:
	"""
	Replace every non-json-serializable object inside a tuple to a dictionary, following the specified rules.
	"""
	new = []
	for e in obj:
		if isinstance(e, (str,int,float,set,bool)) or e == None:
			new.append(e)
		elif isinstance(e, list):
			new.append(convert_list_json(e, attributes_rules))
		elif isinstance(e, tuple):
			new.append(convert_tuple_json(e,attributes_rules))
		elif isinstance(e, dict):
			new.append(convert_dict_json(e, attributes_rules))
		else:
			new.append(convert_object_json(e, attributes_rules))
	return tuple(new)

def convert_dict_json(obj:Dict[Any,Any],attributes_rules:Dict[Type,List[str]])->dict:
	"""
	Replace every non-json-serializable object inside a dictionary to a dictionary, following the specified rules.
	"""
	new = {}
	for key in obj.keys():
		if not (isinstance(key, (str,int,float,set,list,tuple,dict,bool)) or key == None):
			raise ValueError("A dictionary key cannot be json serialized if it's an object.")
		value = obj[key]
		if isinstance(value, (str,int,float,set)) or value == None:
			new[key] = value
		elif isinstance(value, list):
			new[key] = convert_list_json(value, attributes_rules)
		elif isinstance(value, tuple):
			new[key]=convert_tuple_json(value,attributes_rules)
		elif isinstance(value, dict):
			new[key]= convert_dict_json(value, attributes_rules)
		else:
			new[key] = convert_object_json(value, attributes_rules)
	return new
