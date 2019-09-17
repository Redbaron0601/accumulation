import Compile_Tree as ct

class Calculator(object):
    def __init__(self, lex_Object):
        self.num_string = ""
        self.result = 0
        self.calc_symbol = ['+', '-', '*', '/', '(', ')']
        self.digit = [x for x in '0123456789.$']
        self.isBlank = True
        self.lexBox = lex_Object
        return

    def get_input(self, path):
        # path = r'./test.txt'
        with open(path, 'rb') as f:
            # Unicode Bytes
            temp = f.read().decode()
            # print(type(temp[0]))
            assert type(temp) == str
            self.num_string = temp
            self.isBlank = False
        return

    def string_parse(self):
        parse_str = self.num_string + '$'
        peek_len = len(parse_str)
        i = 0
        lex_find_id = -1
        tmp_lex = ""
        while True:
            now_str = parse_str[i]
            if i == peek_len-1:
                assert parse_str[i] == '$'
                break
            assert i < peek_len - 1
            # Still need to Check if str-num, could be turn into Int
            look_forward = parse_str[i+1]
            try:
                if now_str in self.digit and look_forward in self.digit:
                    if look_forward is '$':
                        tmp_lex += now_str
                        self.lexBox.push_lexObject(tmp_lex, lex_find_id, False)
                        lex_find_id = -1
                        tmp_lex = ""
                        break
                        # Finish Parsing
                    if lex_find_id in [-1, 0, 1, 6]:
                        # New Finding
                        if lex_find_id == 0 or lex_find_id == -1:
                            tmp_lex += now_str
                        else:
                            # Keep Searching
                            tmp_lex += now_str
                        lex_find_id = 1
                if now_str in self.digit and look_forward in self.calc_symbol:
                    if look_forward == '(':
                        print('\'(\' should not be used here !')
                        raise ValueError
                    if lex_find_id in [-1, 0, 1, 6]:
                        # New Finding
                        if look_forward is ')':
                            flag = self.lexBox.find_matchlex()
                            if flag:
                                tmp_lex += now_str
                            else:
                                raise ValueError('Wrong use of \')\'')
                        else:
                            tmp_lex += now_str
                        self.lexBox.push_lexObject(tmp_lex, lex_find_id, False)
                        tmp_lex = ""
                        lex_find_id = 2
                        # Finding a terminate-string like ')' or '+'
                if now_str in self.calc_symbol and look_forward in self.digit:
                    if now_str == ')' and look_forward is '$':
                        flag = self.lexBox.find_matchlex(1)
                        if flag:
                            self.lexBox.push_lexObject(now_str, lex_find_id, True)
                            lex_find_id = -1
                            break
                            # Finish Parsing
                        else:
                            # print("Wrong use of \')\'")
                            raise ValueError("Wrong use of \')\'")
                    elif now_str == ')' and look_forward is not '$':
                        # print('\')\' should not be used here !')
                        raise ValueError('\')\' should not be used here !')
                    if lex_find_id == -1:
                        # Begin-state
                        # Only '(' can be set in head of the string
                        if now_str is not '(':
                            # print(r"Only '(' can be set in head of the string !")
                            raise ValueError(r"Only '(' can be set in head of the string !")
                        else:
                            tmp_lex = now_str
                            self.lexBox.push_lexObject(tmp_lex, lex_find_id, True)
                            tmp_lex = ""
                            lex_find_id = 6
                            # Find new Lex Item
                    else:
                        # lex_find_id = 2, 3, 4, 5
                        # 0 is not a state of calc-symbols
                        # The symbol of a lex ends
                        tmp_lex += now_str
                        self.lexBox.push_lexObject(tmp_lex, lex_find_id, True)
                        tmp_lex = ""
                        if now_str == '(':
                            lex_find_id = 6
                        else:
                            lex_find_id = 0
                        # Find new Lex Item
                if now_str in self.calc_symbol and look_forward in self.calc_symbol:
                    # -(express1) or express2)*(express3 or express4)/ ...
                    if lex_find_id == 2:
                        if now_str in ['+', '-', '*', '/'] and look_forward is '(':
                            tmp_lex = now_str
                            self.lexBox.push_lexObject(tmp_lex, 3, True)
                            lex_find_id = 3
                            tmp_lex = ""
                        elif now_str is ')' and look_forward in ['+', '-', '*', '/', ')']:
                            flag = self.lexBox.find_matchlex(1)
                            if flag:
                                tmp_lex = now_str
                                self.lexBox.push_lexObject(tmp_lex, 4, True)
                                tmp_lex = ""
                                lex_find_id = 4
                            else:
                                # print("Expression seriously Wrong !")
                                raise ValueError("Expression seriously Wrong !")
                        else:
                            # print('Invalid Expression')
                            raise ValueError('Invalid Expression')
                    elif lex_find_id == 3:
                        if now_str == '(' and look_forward == '(':
                            self.lexBox.push_lexObject(now_str, 5, True)
                            lex_find_id = 5
                        else:
                            raise ValueError("Expression seriously Wrong !")
                    elif lex_find_id == 4:
                        if now_str is not ')':
                            raise ValueError("Expression seriously Wrong !")
                        else:
                            flag = self.lexBox.find_matchlex(1)
                            if flag:
                                tmp_lex = now_str
                                self.lexBox.push_lexObject(tmp_lex, 4, True)
                                tmp_lex = ""
                                lex_find_id = 4
                            else:
                                raise ValueError("Expression seriously Wrong !")
                    elif lex_find_id in [5, -1]:
                        if now_str == '(' and look_forward == '(':
                            self.lexBox.push_lexObject(now_str, lex_find_id, True)
                            lex_find_id = 5
                        else:
                            # print("Expression seriously Wrong !")
                            raise ValueError("Expression seriously Wrong !")
            except Exception as e:
                print(e)
                exit(99)
            i += 1
        return

    def reset_Calculator(self, lexObject):
        self.num_string = ""
        self.isBlank = True
        self.result = None
        self.lexBox = None
        del lexObject
        return


class lex_container(object):
    def __init__(self):
        self.lexPool = []
        self.bracket_record = {'(': [], ')': []}
        self.match_map = {}
        self.tmp_lex = ""
        self._id = len(self.lexPool)
        return

    def get_id(self):
        self._id = len(self.lexPool) + 1
        return self._id

    def push_lexObject(self, lex_str, find_id=2, calc=False):
        # print(lex_str)
        b_type = 0
        lex_id = self.get_id()
        priority = 0
        if calc:
            if lex_str is '(':
                b_type = 1
                priority = 2
                self.bracket_record['('].append(lex_id)
            elif lex_str is ')':
                b_type = 2
                priority = 2
                self.bracket_record[')'].append(lex_id)
            elif lex_str in ['*', '/']:
                priority = 1
            else:
                priority = 0
        element = {'e_Value': lex_str, 'state': find_id, 'is_Calc': calc, 'lex_id': lex_id,\
                   'type_bracket': b_type, 'priority': priority}
        self.lexPool.append(element)
        # 后续还可以假如作用域划分管理
        return

    def check_lexTable(self):

        return

    def find_matchlex(self, flag=0):
        index = len(self.bracket_record['('])
        # str_key = '{0}'.format(index)
        r_bracket_id = len(self.bracket_record[')'])
        if index:
            while index > 0:
                if str(self.bracket_record['('][index-1]) in self.match_map.keys():
                    index -= 1
                    continue
                else:
                    if flag:
                        r_bracket_id += 1
                        self.match_map.setdefault(str(self.bracket_record['('][index-1]), r_bracket_id)
                        self.match_map.setdefault(')-{0}'.format(r_bracket_id), str(self.bracket_record['('][index-1]))
                    return True
            if index == 0:
                return False
        else:
            print('Use \')\' when there is no \'(\ ahead')
            return False

    def persist_lexAll(self):

        return

# ######################### TEST
lexBox = lex_container()
calc = Calculator(lexBox)
calc.get_input('test.txt')
print(calc.num_string)
calc.string_parse()
ct.compile_Tree.make_priority(calc, end_id=len(calc.lexBox.lexPool))
root = ct.compile_Tree.make_Tree(calc.lexBox.lexPool, calc.lexBox)
result = ct.compile_Tree.calc_result(root)
print(result)
# ######################### TEST
