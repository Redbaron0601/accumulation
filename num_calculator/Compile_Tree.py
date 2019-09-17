class compile_TreeNode(object):
    def __init__(self, left=None, right=None, v_node=''):
        self.left = left
        self.right = right
        self.node_value = v_node
        self.priority = 0
        self.is_Leaf = False
        return

    def isLeaf(self):
        if self.left is None and self.right is None:
            self.is_Leaf = True
        else:
            self.is_Leaf = False


class compile_Tree(object):
    def __init__(self):
        # self.prior_lexPool = Calc_Object.lexBox.lexPool
        return

    @staticmethod
    def make_priority(Calc_Object, tb_id=0, end_id=0):
        calculator = Calc_Object
        lexCon = calculator.lexBox.lexPool
        for index in range(tb_id, end_id, 1):
            if lexCon[index]['e_Value'] is '(':
                b_index = calculator.lexBox.match_map[str(index+1)]
                b_id = calculator.lexBox.bracket_record[')'][b_index-1]
                for p_prior in range(index+1, b_id, 1):
                    if lexCon[p_prior]['is_Calc']:
                        if lexCon[p_prior]['e_Value'] is not '(':
                            if lexCon[p_prior]['e_Value'] in ['*', '/']:
                                lexCon[p_prior]['priority'] = lexCon[index]['priority'] + 1
                            elif lexCon[p_prior]['e_Value'] in ['+', '-']:
                                lexCon[p_prior]['priority'] = lexCon[index]['priority']
                        else:
                            bb_index = calculator.lexBox.match_map[str(p_prior+1)]
                            bb_id = calculator.lexBox.bracket_record[')'][bb_index-1]
                            lexCon[p_prior]['priority'] = lexCon[index]['priority'] + 2
                            compile_Tree.make_priority(Calc_Object, tb_id=p_prior, end_id=bb_id)
        return

    def get_rValue(self):

        return

    @staticmethod
    def make_Tree(lex_Slice, lex_Object):
        min_priority = 1e5
        min_id_list = []
        _id = 1
        cnt = 0
        lexCon = lex_Slice
        temp_lex = []
        t_root = compile_TreeNode()
        #  In a Block
        for item in lexCon:
            temp_lex.append(item)
            if item['is_Calc'] and item['e_Value'] in ['(', ')']:
                temp_lex.remove(item)
        assert len(temp_lex) > 0
        if len(temp_lex) == 1:
            t_root.node_value = temp_lex[_id-1]['e_Value']
            # t_root.priority = temp_lex[_id-1]['priority']
        else:
            for item in temp_lex:
                cnt += 1
                if item['is_Calc'] and item['e_Value'] not in ['(', ')']:
                    if min_priority >= item['priority']:
                        min_priority = item['priority']
                        # min_id = item['lex_id']
                        _id = cnt
            # Assert Index range
            # Left Tree Branch
            # _l_end = lexCon[_id-2]['lex_id']
            # _l_index = lex_Object.bracket_record[')'].index(_l_end)
            # _l = lex_Object.match_map[')-{0}'.format(_l_index+1)]
            t_root.node_value = temp_lex[_id-1]['e_Value']
            llex_Slice_son = temp_lex[0:_id-1]
            assert len(llex_Slice_son) > 0
            if len(llex_Slice_son) > 1:
                new_lnode = compile_Tree.make_Tree(llex_Slice_son, lex_Object)
            else:
                new_lnode = compile_TreeNode(v_node=llex_Slice_son[0]['e_Value'])
                new_lnode.isLeaf()
            t_root.left = new_lnode
            # Right Tree Branch
            # _r = lexCon[_id]['lex_id']
            # _r_index = lex_Object.match_map['{0}'.format(_r)]
            # _r_end = lex_Object.bracket_record['('][_r_index-1]
            rlex_Slice_son = temp_lex[_id:]
            assert len(rlex_Slice_son) > 0
            if len(rlex_Slice_son) > 1:
                new_rnode = compile_Tree.make_Tree(rlex_Slice_son, lex_Object)
            else:
                new_rnode = compile_TreeNode(v_node=rlex_Slice_son[0]['e_Value'])
                new_rnode.isLeaf()
            t_root.right = new_rnode
        # Check is Leaf or not
        t_root.isLeaf()
        return t_root

    @staticmethod
    def calc_result(Tree_node):
        # DFS for result
        t_value = 0
        l_value = 0
        r_value = 0
        if not Tree_node.is_Leaf:
            if Tree_node.left is not None:
                l_value = compile_Tree.calc_result(Tree_node.left)
            if Tree_node.right is not None:
                r_value = compile_Tree.calc_result(Tree_node.right)
            if Tree_node.node_value is '+':
                t_value = l_value + r_value
            if Tree_node.node_value is '-':
                t_value = l_value - r_value
            if Tree_node.node_value is '*':
                t_value = l_value * r_value
            if Tree_node.node_value is '/':
                t_value = l_value / r_value
        else:
            t_value = float(Tree_node.node_value)
        return t_value






