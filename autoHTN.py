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

def insert_prereq(state, rule, ID):
	subtasks = []

	# requires = rule.get('Requires', {})
	# for item, value in requires.items():
	# 	# if getattr(state, item)[ID] < value:
	# 	subtasks.append(('have_enough', ID, item, value))

	consumes = rule.get('Consumes', {})	
	for item, value in consumes.items():
		if getattr(state, item)[ID] < value:
			subtasks.append(('produce_enough', ID, item, value-getattr(state, item)[ID]))
	print("\nsubtasks in insert prerqe: ", subtasks, "\n")

	return subtasks # a list

	# if we are missing a dependency, add it to the list
	# adjusts the plan by task decomposition
pyhop.declare_methods ('insert_prereq', insert_prereq)

def make_method (name, rule):
	def method (state, ID):
		subtasks = []

		requires = rule.get('Requires', {})
		for item, value in requires.items():
			# if item == "furnace" and getattr(state, "stone_pickaxe")[ID] < 1:
			# 	subtasks.append(('have_enough', ID, "wooden_pickaxe", 1))
			# 	subtasks.append(('have_enough', ID, "stone_pickaxe", 1))
			subtasks.append(('have_enough', ID, item, value))

		consumes = rule.get('Consumes', {})	
		for item, value in reversed(list(consumes.items())):
			# if value < 3:
			# 	subtasks.append(('have_enough', ID, item, 2*value))
			# else:
			subtasks.append(('have_enough', ID, item, value))
		# subtasks.append(('insert_prereq', rule, ID))
		subtasks.append((name, ID))
		return subtasks # a list

	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	#check when recipes are getting overcomplicated

	# your code here
	# print("\n declare method do we have a bench? \n", state.bench)

	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	dict_of_all_methods = {}
	recipes = data["Recipes"]
	# sort recipes
	# Sort recipes based on time, faster recipes first	
	# def custom_sort(item):
	# 	time = item[1]["Time"]
	# 	reverse_time = -time  # Reverse time
	# 	name = item[0]
	# 	return (reverse_time, name[::-1])  # Reverse the name for alphabetical reverse order

	# # Sort the recipes using the custom sorting function
	# sorted_recipes = dict(sorted(recipes.items(), key=custom_sort))
	sorted_recipes = dict(sorted(recipes.items(), key=lambda x: x[1].get('Time', 1), reverse=True))


	print(sorted_recipes)
	#the way we sort the recipes is 
	
	# make methods
	#loop through sorted recipes
	for name in sorted_recipes.keys():
		# checks what's the method goal
		produces = recipes[name].get('Produces', {})
		assert len(produces.keys()) == 1
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
		# Declare the methods to pyhop for the current goal
		
		#find out the ways to produce woods, dict_of_all_methods,
		#iterate through dict_of_all_methods
	# print("dict of all methods: ", dict_of_all_methods["produce_wooden_axe"])
	# dict_of_all_methods["produce_wood"] = list(reversed(dict_of_all_methods["produce_wood"]))
	for method_name in dict_of_all_methods.keys():
		#going through, produce wood, give it all the ways and then declare, 2 ways of producing wood, axe or punching, first for loop looking at ways
		#don't want to declare one for each, declare through method_name, not recipe
		pyhop.declare_methods(method_name, *dict_of_all_methods[method_name]) #unpacks the list
	
def make_operator(rule):
	def operator(state, ID):
        # Extract relevant information from the rule
		produces = rule.get('Produces', {})
		requires = rule.get('Requires', {})
		consumes = rule.get('Consumes', {})
		time_required = rule.get('Time', 1) #sets 1 as the default
		
		if state.time[ID] < time_required:
			return False
				
		for item, value in requires.items(): #how does bench dissapear
			if getattr(state, item)[ID] < value:
				return False
			
		for item, value in consumes.items():
			if getattr(state, item)[ID] < value:
        	# You don't have enough of this item, handle accordingly
				return False
			else:
				setattr(state, item, {ID: getattr(state, item)[ID] - value})

				#getattr(state, item)[ID] -= value
		
		state.time[ID] -= time_required
		for item, value in produces.items():
			setattr(state, item, {ID: getattr(state, item)[ID] + value})
			# getattr(state, item)[ID] += value
		
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
		#print("----------HUERSITIC------------", "state: ", state, " current task: ", curr_task, " tasks: ", tasks, " plan: ", plan, " depth: ", depth, " stack: ", calling_stack)
		#heuristic takes into account the current_stack
		#list of subtasks connecting to the curr_task
		#if the curr_task has been seen at the same or lower depth, cut		
		# check if we got enough of original item

		print("\n\nCalling stack:\n", calling_stack, "\n")
		print("Tasks:\n", tasks, "\n\n")
		# print("plan: ", plan)
		# print("curr_task: ", curr_task)
		tools = ["bench",
   				"furnace",
   				"iron_axe",
   				"iron_pickaxe",
   				"stone_axe",
   				"stone_pickaxe",
   				"wooden_axe",
   				"wooden_pickaxe"
 				]		
		
		if curr_task in calling_stack:
			#happens when creating tools, don't need tools more then once
			#if curr_task #creating we a tool we already plan to have, 
		
			if len(curr_task) >= 3 and curr_task[2] in tools and curr_task[0] in ["produce"]:
				if getattr(state, curr_task[2])[ID] >= 1:
						
						# tasks.remove(curr_task)
						print("\n\nNEW Current Task eliminated: ", curr_task[2])
						return True
								
			if len(curr_task) >= 3 and curr_task[2] in tools and curr_task[0] in ["have_enough", "produce"]:
				# if we already made a tool -> break				
				# if we need the current tool to create the tool in the future (need wooden axe to get wood to make a wooden axe) -> break
				for task in tasks[1:]:
					if len(task) >= 3 and curr_task[2] == task[2]:
						print("\n\nCurrent Task eliminated: ", curr_task[2])
						return True
			if depth > 900:
				return True
					
		return False

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

	state = set_up_state(data, 'agent', time=1000) # allot time here
	# state = set_up_state(data, 'agent', time=100)
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	
	# pyhop.pyhop(state, [('have_enough', 'agent', 'iron_pickaxe', 1)], verbose=3)
	pyhop.pyhop(state, [('have_enough', 'agent', 'stick', 120),('have_enough', 'agent', 'plank', 100),('have_enough', 'agent', 'wooden_pickaxe', 1), ('have_enough', 'agent', 'wooden_axe', 1), ('have_enough', 'agent', 'stone_pickaxe', 1), ('have_enough', 'agent', 'stone_axe', 1), ('have_enough', 'agent', 'ore', 15), ('have_enough', 'agent', 'cobble', 10), ('have_enough', 'agent', 'coal', 10), ('have_enough', 'agent', 'ingot', 10)], verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 40),('have_enough', 'agent', 'iron_axe', 10)], verbose=3)

	# pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 10)], verbose=3)
