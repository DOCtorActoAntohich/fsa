# Python 3.4.3

import collections
import sys
import re



k_states = "states"
k_alphabet = "alpha"
k_initial_state = "init.st"
k_final_states = "fin.st"
k_transitions = "trans"



def read_file(filename):
	"""Reads the file and transforms it to FSA description.

	Input file format must be:
	states=[s1,s2,...]
	alpha=[a1,a2,...]
	init.st=[s]
	fin.st=[s1,s2,...]
	trans=[s1>a>s2,...]

	Parameters:
	- filename -> str: a path to a file.

	Returns -> map:
	FSA description.

	Exceptions:
	- OSError - file not found.
	- ValueError - incorrect file format.
	"""

	fsa_description = dict()
	
	input_regex = [
		# Any strings separated by commas
		r"states=\[([a-zA-Z0-9]+,)*([a-zA-Z0-9])+\]",

		# Same as before but strings can contain underscores.
		r"alpha=\[([a-zA-Z0-9_]+,)*([a-zA-Z0-9_])+\]",

		# Same as 1st line but brackets can be empty (for E4 - no initial state defined).
		r"init\.st=\[([a-zA-Z0-9]+){0,1}\]",

		# Zero or more strings separated by comma (for W1 - no final state).
		r"fin\.st=\[(([a-zA-Z0-9]+,)*([a-zA-z0-9]+))*\]",

		# Same as before, but strings are in format "s1>t>s2" (for E2 - disjoint states).
		r"trans=\[(((([a-zA-Z0-9]+)>([a-zA-Z0-9_]+)>([a-zA-Z0-9]+)),)*(([a-zA-Z0-9]+)>([a-zA-Z0-9_]+)>([a-zA-Z0-9]+)))*\]"
	]
	with open(filename, "r") as file:
		i = 0
		for line in file.readlines():
			line = line.strip();
			if re.match(input_regex[i], line) == None:
				raise ValueError("Incorrect file format.")
			key, tmp_value = line.split("=")
			values = tmp_value[1:-1].split(",")
			fsa_description[key] = list(filter(lambda x: True if x != "" else False, values))
			i += 1

	if len(fsa_description[k_initial_state]) != 0:
		fsa_description[k_initial_state] = fsa_description[k_initial_state][0]
	else:
		fsa_description[k_initial_state] = None

	transitions = []
	for transition in fsa_description[k_transitions]:
		params = transition.split(">")
		transitions.append(tuple(params))
	fsa_description[k_transitions] = list(set(transitions))

	return fsa_description;



def is_disjoint(fsa):
	"""Checks if FSA has disjoint states using BFS.
	
	Parameters:
	- fsa -> map: a description of FSA.

	Returns -> bool:
	True if FSA has dosjoint states, False otherwise.
	"""

	graph = dict()
	for state in fsa[k_states]:
		graph[state] = []
	for state_from, _, state_to in fsa[k_transitions]:
		graph[state_from].append(state_to)
		graph[state_to].append(state_from)
	
	visited_nodes = set()
	q = collections.deque()
	q.append(fsa[k_initial_state])
	while len(q) != 0:
		node = q.popleft()
		visited_nodes.add(node)
		for next_node in graph[node]:
			if next_node not in visited_nodes:
				q.append(next_node)

	return len(visited_nodes) != len(fsa[k_states])



def find_error(fsa):
	"""Checks if FSA has errors in its description.

	Parameters:
	- fsa -> map: a description of FSA.

	Returns -> str, None:
	Error string if there are errors in description, None otherwise.
	"""

	if fsa[k_initial_state] == None:
		return "E4: Initial state is not defined"
	elif fsa[k_initial_state] not in fsa[k_states]:
		return "E1: A state '%s' is not in the set of states" % (fsa[k_initial_state])

	for state_from, transition, state_to in fsa[k_transitions]:
		if transition not in fsa[k_alphabet]:
			return "E3: A transition '%s' is not represented in the alphabet" % (transition)
		elif state_from not in fsa[k_states]:
			return "E1: A state '%s' is not in the set of states" % (state_from)
		elif state_to   not in fsa[k_states]:
			return "E1: A state '%s' is not in the set of states" % (state_to)

	for final_state in fsa[k_final_states]:
		if final_state not in fsa[k_states]:
			return "E1: A state '%s' is not in the set of states" % (final_state)

	if is_disjoint(fsa):
		return "E2: Some states are disjoint"

	return None;



def is_complete(fsa):
	"""Checks if FSA is complete.

	Parameters:
	- fsa -> map: a description of FSA.

	Returns -> bool:
	True if FSA is complete, False otherwise.
	"""

	transitions_for_state = dict()
	for state_from, transition, state_to in fsa[k_transitions]:
		if state_from not in transitions_for_state.keys():
			transitions_for_state[state_from] = []
		transitions_for_state[state_from].append(transition)

	for state in transitions_for_state.keys():
		transitions = set(transitions_for_state[state])
		if len(transitions) < len(fsa[k_alphabet]):
			return False;
	return True;



def is_deterministic(fsa):
	"""Checks if FSA is deterministic.

	Parameters:
	- fsa -> map: a description of FSA.

	Returns -> bool:
	True if FSA is deterministic, False otherwise.
	"""

	transition_function = dict()
	for state_from, transition, state_to in fsa[k_transitions]:
		function_input = (state_from, transition)
		if function_input not in transition_function.keys():
			transition_function[function_input] = state_to;
		else:
			return False

	return True;



def are_all_states_reachable(fsa):
	"""Checks if every state of FSA can be reached from the initial state.
	BFS is used here.

	Parameters:
	- fsa -> map: a description of FSA.

	Returns -> bool:
	True if all states can be reached from the initial state, False otherwise.

	- fsa -> map: a description of FSA.
	"""

	graph = dict()
	for state in fsa[k_states]:
		graph[state] = []
	for state_from, _, state_to in fsa[k_transitions]:
		graph[state_from].append(state_to)
	
	visited_nodes = set()
	q = collections.deque()
	q.append(fsa[k_initial_state])
	while len(q) != 0:
		node = q.popleft()
		visited_nodes.add(node)
		for next_node in graph[node]:
			if next_node not in visited_nodes:
				q.append(next_node)

	return len(visited_nodes) == len(fsa[k_states])



def main():
	"""This is method main.
	It is very main.
	What did you expect?
	"""

	try:
		fsa = read_file("fsa.txt");
	except ValueError:
		print("Error:")
		print("E5: Input file is malformed")
		return

	error = find_error(fsa)
	if error != None:
		print("Error:")
		print(error)
		return;


	print("FSA is %scomplete" % ("" if is_complete(fsa) else "in"))

	warnings = []
	if len(fsa[k_final_states]) == 0:
		warnings.append("W1: Accepting state is not defined")
	if not are_all_states_reachable(fsa):
		warnings.append("W2: Some states are not reachable from the initial state")
	if not is_deterministic(fsa):
		warnings.append("W3: FSA is nondeterministic")
	
	if len(warnings) != 0:
		print("Warning:")
		[print(x) for x in warnings]


	return;


if __name__ == "__main__":
	sys.stdout = open("result.txt", "w")
	main()
	sys.stdout.close();

	sys.stdout = sys.__stdout__