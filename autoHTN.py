import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method (name, rule):
	def method (state, ID):
		subtasks = []
		
		requires = rule.get('Requires', {})
		for item, value in requires.items():
			subtasks.append(('have_enough', ID, item, value))

		consumes = rule.get('Consumes', {})
		for item, value in consumes.items():
			subtasks.append(('have_enough', ID, item, value))
		
		subtasks.append((name, ID))
		return subtasks # a list

	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	dict_of_all_methods = {}
	recipes = data["Recipes"]
	# sort recipes
	
	sorted_recipes = dict(sorted(recipes.items(), key=lambda x: x[1].get('Time', 1)))
	# make methods

	#for name, rule in sorted_recipes:
		#op_name = "op_" + name.replace(" ", "_")
		#method_name = "produce_" + list(produces.keys())[0].replace(" ", "_")
		#method = make_method(op_name, rule)
		#pyhop.declare_methods(method_name, method)

	
	for name in sorted_recipes.keys():
		# checks what's the method goal
		produces = recipes[name].get('Produces', {})
		method_name = "produce_" + list(produces.keys())[0].replace(" ", "_")

		# name of related operator to pass to the make_method
		op_name = "op_" + name.replace(" ", "_")
		method = make_method(op_name, recipes[name])

		# name of possible method that achieve it
		single_method = name.replace(" ", "_")
		method.__name__ = single_method
		# have a dict with all possible ways to produce this item
		if method_name not in dict_of_all_methods:
			dict_of_all_methods[method_name] = [method]
		else:
			dict_of_all_methods[method_name].append(method)
		pyhop.declare_methods(method_name, *dict_of_all_methods[method_name])
	
def make_operator(rule):
	def operator(state, ID):
        # Extract relevant information from the rule
		produces = rule.get('Produces', {})
		requires = rule.get('Requires', {})
		consumes = rule.get('Consumes', {})
		time_required = rule.get('Time', 1) #sets 1 as the default
		
		if state.time[ID] < time_required:
			return False

		for item, value in requires.items():
			if getattr(state, item)[ID] < value:
				return False
			
		for item, value in consumes.items():
			if getattr(state, item)[ID] < value:
        	# You don't have enough of this item, handle accordingly
				return False
			else:
				getattr(state, item)[ID] -= value
		
		state.time[ID] -= time_required
		for item, value in produces.items():
			getattr(state, item)[ID] += value
		
		return state
	return operator

def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
	list_of_all_operators = []
	recipes = data["Recipes"]
	for name in recipes.keys():
		op_name = "op_" + name.replace(" ", "_")
		op = make_operator(recipes[name])
		op.__name__ = op_name
		list_of_all_operators.append(op)
	pyhop.declare_operators(*list_of_all_operators)


def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		# your code here
		return False # if True, prune this branch

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=46) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	pyhop.print_operators()
	pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, [('have_enough', 'agent', 'wood', 12)], verbose=3)
	# pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
