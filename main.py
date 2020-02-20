# Python 3.4.3

import collections
import sys



k_states = "states"
k_alphabet = "alpha"
k_initial_state = "init.st"
k_final_states = "fin.st"
k_transitions = "trans"



def read_file(filename):
	fsa_description = dict()
	with open(filename, "r") as file:
		for line in file.readlines():
			key, tmp_value = line.strip().split("=")
			values = tmp_value[1:-1].split(",")
			fsa_description[key] = list(filter(lambda x: True if x != "" else False, values))

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
	# BFS is used here.
	graph = dict()
	for state_from, _, state_to in fsa[k_transitions]:
		if state_from not in graph.keys():
			graph[state_from] = []
		graph[state_from].append(state_to)
		if state_to not in graph.keys():
			graph[state_to] = []
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
	transition_function = dict()
	for state_from, transition, state_to in fsa[k_transitions]:
		function_input = (state_from, transition)
		if function_input not in transition_function.keys():
			transition_function[function_input] = state_to;
		else:
			return False

	return True;



def are_all_states_reachable(fsa):
	# BFS is used here
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
	try:
		fsa = read_file("fsa.txt");
		if len(fsa) != 5:
			raise Exception;
	except:
		print("E5: Input file is malformed")
		return;

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