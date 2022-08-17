from typing import Iterable


class Lexer:

    def __init__(self, original_word):
        self.dfas = []
        self.result = []
        self.write_me = ""
        self.default_msg = "No viable alternative at character "
        # as from requirements: the input is written on the first line
        self.default_line = ", line 0"
        self.failed = False
        self.word_copy = original_word
        self.current_index = 0

    def resolve_result(self):

        size = len(self.result)
        count = 0
        for (token, max_match) in self.result:
            if max_match == '\n':
                max_match = "\\n"
            if count == size - 1:
                self.write_me += token + " " + max_match
            else:
                self.write_me += token + " " + max_match + "\n"
                count += 1

    def add_dfa(self, token, dfa):
        self.dfas.append((token, dfa))

    def check_dfas_alphabets(self):
        for (token, dfa) in self.dfas:
            if not dfa.not_in_alphabet:
                return True
        return False

    def lexical_analysis(self, word):
        if len(word) == 0:
            self.resolve_result()
            return self.result

        max_index = -1
        dfa_index = " "
        # find maximum prefix for each dfa
        for (token, dfa) in self.dfas:
            current_index = dfa.accept_word(word)

            if max_index < current_index:
                max_index = current_index
                dfa_index = token

        # add the dfa which have max prefix in the list and the word accepted by it
        if max_index != -1:
            self.current_index += max_index
            self.result.append((dfa_index, word[0:max_index]))
            # update word and call function again
            updated_word = word[max_index:]
            return self.lexical_analysis(updated_word)
        else:
            # all dfas are in sink state
            self.failed = True
            # check for wrong alphabet in input
            no_dfa = self.check_dfas_alphabets()
            # grab last_dfa
            (last_token, last_dfa) = self.dfas[len(self.dfas) - 1]
            # if last letter read is not in any alphabet then display last dfa max reached index
            if last_dfa.not_in_alphabet and not no_dfa:
                self.default_msg += str(self.current_index) + self.default_line
            # end of file
            elif self.current_index + 1 == len(self.word_copy):
                self.default_msg += "EOF" + self.default_line
            # return sink index reached
            else:
                self.default_msg += str(self.current_index + 1) + self.default_line
            return self.lexical_analysis("")


class DFA:

    def __init__(self, string):

        self.delta = dict()
        self.initial_state = -1
        self.final_states = set()
        self.alphabet = []
        self.last_state = 0
        self.states = []
        self.rev_delta = dict()
        self.max_index = -1
        self.token = ""
        self.not_in_alphabet = False

        lines_parsed = string.split("\n")
        for char in lines_parsed[0]:
            if char == "\\":
                self.alphabet.append('\n')
                continue
            elif char == "n":
                continue
            elif char != '\n':
                self.alphabet.append(char)
            else:
                continue

        self.token = lines_parsed[1]
        self.initial_state = int(lines_parsed[2])

        for transition_raw in lines_parsed[3:]:
            transition_processed = transition_raw.split(",")
            # final states
            if len(transition_processed) == 1:
                transition_processed_copy = str(transition_processed[0]).split(" ")

                for final_state in transition_processed_copy:
                    if final_state != ' ' and final_state != '\n':
                        self.final_states.add(int(final_state))
            else:
                if transition_processed[1][1:2] == "\\":
                    transition_processed[1] = "'\n'"
                # transitions
                self.delta[(int(transition_processed[0]), transition_processed[1][1:2])] = int(transition_processed[2])
                aux = max(int(transition_processed[0]), int(transition_processed[2]))
                self.last_state = max(self.last_state, aux)

        self.states = list(range(0, self.last_state + 1))
        """
        # preprocessing - complete undefined states 
        # there is no need for this currently
        for state in self.states:
            for letter in self.alphabet:
                if(state, letter) not in self.delta.keys():
                    self.delta[(state, letter)] = self.last_state + 1
        for letter in self.alphabet:
            self.delta[(self.last_state + 1, letter)] = self.last_state + 1
        """

    # used for find_sink_states
    def flatten(self, list):
        for sub_list in list:
            if isinstance(sub_list, Iterable) and not isinstance(sub_list, (str, bytes)):
                for sub_sub_list in self.flatten(sub_list):
                    yield sub_sub_list
            else:
                yield sub_list

    # find sink_states
    # 1. reverse delta function
    # 2. BFS/DFS from final states and build K_visited
    # 3. K - K_visited -> sink_states
    # 4. delete sink_states from delta and run algorithm
    def find_sink_states(self):

        for key, value in self.delta.items():
            (current_state, letter) = key
            next_state = value
            if current_state == next_state:
                continue
            else:
                if next_state in self.rev_delta:
                    # take all values from 'next_state' key and append the current one
                    aux = [self.rev_delta.get(next_state), current_state]
                    # update dict value
                    self.rev_delta[next_state] = aux
                else:
                    self.rev_delta[next_state] = current_state

        def dfs(visited, graph, node):
            if node not in visited:
                visited.add(node)
                # if it s list -> flatten it
                if isinstance(self.rev_delta.get(node), list):
                    flat_list = list(self.flatten(self.rev_delta.get(node)))
                    for neighbour in flat_list:
                        dfs(visited, graph, neighbour)
                # else call function
                else:
                    dfs(visited, graph, self.rev_delta.get(node))
            return visited

        k_visited = set()
        # dfs from every final state
        for state in self.final_states:
            aux = set()
            aux = dfs(aux, self.rev_delta, state)
            # append visited states
            k_visited = k_visited | aux

        # return the sink states
        return set(self.states) - k_visited

    def delete_sink_states(self, sink_states):
        updated_delta = dict()
        for sink in sink_states:
            for key, value in self.delta.items():
                (current_state, letter) = key
                next_state = value
                if current_state == sink or next_state == sink:
                    continue
                else:
                    updated_delta[key] = value
        if len(updated_delta) != 0:
            self.delta = updated_delta

    def one_step(self, config):
        (current_state, current_word, count) = config
        # if transition exists in delta is valid because of pre sink states elimination
        if (current_state, current_word[0]) in self.delta:
            next_state = self.delta[(current_state, current_word[0])]
            rest_word = current_word[1:]
            count += 1
            return next_state, rest_word, count
        else:
            return -1, 'err', count

    # checks if a char is in a dfa s alphabet
    def check_alphabet(self, check_char):
        if self.alphabet.__contains__(check_char):
            self.not_in_alphabet = False
        else:
            self.not_in_alphabet = True

    def accept_word(self, word):
        self.max_index = -1
        initial_config = (self.initial_state, word, 0)
        first_config = self.one_step(initial_config)

        (updated_state, updated_word, updated_count) = first_config
        if updated_word == 'err':
            self.check_alphabet(word[0])
            return self.max_index
        else:
            if updated_state in self.final_states and updated_count != 0:
                self.max_index = max(self.max_index, updated_count)

        for _ in updated_word:
            updated_step = self.one_step(first_config)
            updated_state, updated_word, updated_count = updated_step
            if updated_state in self.final_states and updated_count != 0:
                self.max_index = max(self.max_index, updated_count)
            if updated_word == 'err':
                self.check_alphabet(word[0])
                return self.max_index
            first_config = updated_step

        return self.max_index

    def __str__(self):
        return f'alphabet: {self.alphabet}\n' \
               f'token: {self.token}\n' \
               f'initial_state: {self.initial_state}\n' \
               f'final_states: {self.final_states}\ndelta: {self.delta}\n' \
               f'last_state: {self.last_state}\n' \
               f'states: {self.states}\n' \
               f'rev_delta: {self.rev_delta}\n'


def runlexer(lex_file, in_file, out_file):
    with open(in_file, 'r') as f:
        test_input = f.readlines()
    f.close()
    test_input = ''.join(test_input)
    with open(lex_file, 'r') as f:
        test_lex = f.readlines()
    f.close()

    test_lex_updated = ''.join(test_lex)
    test_lex_parsed = test_lex_updated.split("\n\n")

    dfas = []
    # dfa -> the parsing is done in the DFA class
    for dfa in test_lex_parsed:
        dfas.append(DFA(dfa))
    '''
SPACE
0
0,' ',1
1,' ',2
1

^^ it s a string
'''

    lex = Lexer(test_input)

    # delete sink states
    for dfa in dfas:
        dfa.delete_sink_states(dfa.find_sink_states())
        lex.add_dfa(dfa.token, dfa)

    # run lexical analysis
    (lex.lexical_analysis(test_input))
    # write to file
    if lex.failed:
        lex.write_me = lex.default_msg
    f = open(out_file, "w")
    f.write(lex.write_me)
    f.close()

# debug purposes

# lex_file = "tests/T1/T1.11/T1.11.lex"
# in_file = "tests/T1/T1.11/input/T1.11.3.in"
# out_file = "output.txt"
# runlexer(lex_file, in_file, out_file)
