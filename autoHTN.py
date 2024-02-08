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
	for item, value in reversed(list(consumes.items())):
		# if getattr(state, item)[ID] < value:
		subtasks.append(('have_enough', ID, item, value))
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
			subtasks.append(('have_enough', ID, item, value))

		consumes = rule.get('Consumes', {})	
		for item, value in reversed(list(consumes.items())):
			subtasks.append(('have_enough', ID, item, value))
		subtasks.append(('insert_prereq', rule, ID))
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

		# print("\n\nCalling stack:\n", calling_stack, "\n")
		# print("Tasks:\n", tasks, "\n\n")
		# print("plan: ", plan)
		# print("curr_task: ", curr_task)


		if curr_task in calling_stack:
			#happens when creating tools, don't need tools more then once
			#if curr_task #creating we a tool we already plan to have, 
			tools = ["bench",
   				"furnace",
   				"iron_axe",
   				"iron_pickaxe",
   				"stone_axe",
   				"stone_pickaxe",
   				"wooden_axe",
   				"wooden_pickaxe"
 				]		
			# pickaxes = ["iron_pickaxe", "stone_pickaxe", "wooden_pickaxe"]
			# axes = ["iron_axe", "stone_axe", "wooden_axe"]
			
			# if len(curr_task) >= 3 and curr_task[2] in tools and curr_task[0] in ["produce"]:
			# 	if curr_task[2] == "stone_axe":
			# 		# already have wooden axe and plan to make iron axe
			# 		if getattr(state, "wooden_axe")[ID] >= 1:
			# 			for task in calling_stack:
			# 				if len(task) >= 3 and task[2] in axes:
			# 					print("elimnating: ", curr_task[2], " because of axes")
			# 					return True
			# 	if curr_task[2] == "stone_pickaxe":
			# 		# already have wooden axe and plan to make iron axe
			# 		if getattr(state, "wooden_pickaxe")[ID] >= 1:
			# 			for task in calling_stack:
			# 				if len(task) >= 3 and task[2] in pickaxes:
			# 					print("elimnating: ", curr_task[2], " because of pickaxes")
			# 					return True


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
						tasks.remove(task)

						print("\n\nCurrent Task eliminated: ", curr_task[2])
						return True
			
			# print("current task: ", curr_task)
			# pyhop.print_state(state)
			# if len(curr_task) >= 3 and curr_task[0] in ["produce"]:
			# 	item = curr_task[2]
			# 	recipes = data["Recipes"]
			# 	r_name = ""
			# 	print("currently looking at this item: ", item)
			# 	for name in recipes:
			# 		split_name = name.split(" ")
			# 		# print(split_name)
			# 		if "craft" in split_name[0] and item == split_name[1]:
			# 			r_name = name
			# 	if r_name != "":
			# 		for r in recipes[r_name]["Consumes"]:
			# 			print("r is ", r)
			# 			tasks.insert(0, ('have_enough', ID, r, recipes[r_name]["Consumes"][r]))
			# 			print("ME ADDING TASK:", tasks)					
			

			##### current mission
			# dict_completed_items = {}						
			# recipes = data["Recipes"]
			# # dict_completed_items = {}
			# for task in plan:
			# 	print("Task in plan: ", task)
			# 	new_name = task[0][3:].replace("_", " ")
			# 	for name in recipes:
			# 		if new_name == name:
			# 			produces = recipes[new_name]["Produces"]
			# 			for k, v in produces.items():
			# 				if k not in dict_completed_items:
			# 					dict_completed_items[k] = v
			# 				else:
			# 					dict_completed_items[k] = dict_completed_items[k] + v
			
			# for task in tasks:
			# 	if len(task) > 3:
			# 		if task[2] not in dict_completed_items:
			# 			dict_completed_items[task[2]] = task[3]
			# 		else:
			# 			dict_completed_items[task[2]] = dict_completed_items[task[2]] + task[3]
			
			# if (len(curr_task) > 3):
			# 	dict_completed_items[curr_task[2]] = dict_completed_items[curr_task[2]] + curr_task[3]
			
			# dict_of_reserved_items = {}
			# for task in calling_stack:
			# 	if task not in plan:
			# 		if len(task) > 3 and task[2] not in tools:
			# 			if task[2] not in dict_of_reserved_items:
			# 				dict_of_reserved_items[task[2]] = task[3]
			# 			else:
			# 				dict_of_reserved_items[task[2]] = dict_of_reserved_items[task[2]] + task[3]	
			
			# print("\n\nreserved (calling stack): ", dict_of_reserved_items.items(),"\n")
			# print("completed items (plan): ", dict_completed_items.items(),"\n\n")

			# for item in dict_of_reserved_items:
			# 	print("item: ", item, dict_completed_items.get(item,0),  " < ", dict_of_reserved_items.get(item,0),)
			# 	if dict_completed_items.get(item,0) < dict_of_reserved_items.get(item,0):
			# 		return True
			##########
			
			# recipes = data["Recipes"]
			# r_name = ""
			# total_time = 0
			# for task in tasks:
			# 	print("task in loop: ", task)
			# 	if task[0] not in ["have_enough"]:
			# 		total_time += 1
			# 		print("time:", total_time, task)
			# if total_time > 100:
			# 	True
					
			# if state.stone_pickaxe[ID] >= 1 and depth > 350:
			# 	return True
			
			# count the total number of items we will get in the future
			# dict_of_needed_items = {}
			# for task in tasks:
			# 	if len(task) > 3:
			# 		if task[2] not in dict_of_needed_items:
			# 			dict_of_needed_items[task[2]] = task[3]
			# 		else:
			# 			dict_of_needed_items[task[2]] = dict_of_needed_items[task[2]] + task[3]
			# total number of each item we should have at the end
			# dict_of_used_items = {}
			# for task in calling_stack:
			# 	if len(task) > 3 and task[2] not in tools:
			# 		if task[2] not in dict_of_used_items:
			# 			dict_of_used_items[task[2]] = task[3]
			# 		else:
			# 			dict_of_used_items[task[2]] = dict_of_used_items[task[2]] + task[3]						
			
			# print("\n\nneed items (tasks): ", dict_of_needed_items.items(),"\n")
			# print("used items (calling stack): ", dict_of_used_items.items(),"\n\n")

			# # HOW MUCH WE ALREADY CONSUMED
					# calculated what we consumed to get each item
					# so, look at all the possible tools and items, check what's the recipe for them
					# add the items consumed to the dict x the number of the items we have in the state
						# so if rn we have none of the item, it wouldn't add anything
			# items = data["Items"] + tools
			# for item in items:
			# 	if item not in dict_of_needed_items:
			# 		dict_of_needed_items[item] = getattr(state, item)[ID]
			# 	else:
			# 		dict_of_needed_items[item] = dict_of_needed_items[item] + getattr(state, item)[ID]
				
			# 	recipes = data["Recipes"]
			# 	r_name = ""
			# 	print("currently looking at this item: ", item)
			# 	for name in recipes:
			# 		split_name = name.split(" ")
			# 		# print(split_name)
			# 		if "craft" in split_name[0] and item == split_name[1]:
			# 			r_name = name
			# 	if r_name != "":
			# 		for i in range(0,getattr(state, item)[ID]):
			# 			print("r_name is: ", r_name)
			# 			for r in recipes[r_name]["Consumes"]:
			# 				new_name = ""
			# 				for name in recipes:
			# 					split_name = name.split(" ")
			# 					if "craft" in split_name[0] and r == split_name[1]:
			# 						new_name = name
			# 				if new_name != "":
			# 					print("subtask: ", new_name)
			# 					for c in recipes[new_name]["Consumes"]:
			# 						# c = recipes[new_name]["Consumes"]
			# 						print("sub item: ", r, "consumes: ", c, recipes[new_name]["Consumes"][c])
			# 						if c not in dict_of_needed_items:
			# 							dict_of_needed_items[c] = recipes[new_name]["Consumes"][c]
			# 						else:
			# 							dict_of_needed_items[c] = dict_of_needed_items[c] + recipes[new_name]["Consumes"][c]
			# 				print("Item: ", item, "consumes: ", r, recipes[r_name]["Consumes"][r])
			# 				if r not in dict_of_needed_items:
			# 					dict_of_needed_items[r] = recipes[r_name]["Consumes"][r]
			# 				else:
			# 					dict_of_needed_items[r] = dict_of_needed_items[r] + recipes[r_name]["Consumes"][r]

				

			# for item in dict_of_used_items:
			# 	print("item: ", item, dict_of_used_items.get(item,0),  " - ", dict_of_needed_items.get(item,0),)
			# 	if dict_of_needed_items.get(item,0) < dict_of_used_items.get(item,0):
			# 		return True

			# Problem:
					# when an item that is a dependency of one of the tasks is counted as fulfilled
					# and then it is being used in a different task, so now it's impossible to make the original task
			
			# solve:
					# have a dict[item] = how much is needed
					# if the current task is 'have enough', add the amount to dict
					# if it's produce, look at date to see what it takes and remove it from the dict
					# if getattr is less than the amount in the dict, add a new task to make it

		return False

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	# print("\n\n resetting at set up state \n\n")

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

	state = set_up_state(data, 'agent', time=100) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	
	pyhop.pyhop(state, [('have_enough', 'agent', 'iron_axe', 1)], verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'iron_pickaxe', 1)], verbose=3)

	# pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
