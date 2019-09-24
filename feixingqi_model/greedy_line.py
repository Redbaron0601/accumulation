from nonlinearEquation import *
import openpyxl as op
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

# Constants
a1 = 20
a2 = 10
b1 = 15
b2 = 20
theta = 30
delta = 0.001
# P_START = (0.000000, 50000.000000, 5000.000000)
# P_TARGET = (100000.000000, 59652.343380, 5022.001164)
P_START = (0.000000, 50000.000000, 5000.000000)
P_TARGET = (100000.000000, 74860.5488999781, 5499.61109489643)
l_len = math.sqrt(math.pow((P_TARGET[0]-P_START[0]), 2)+math.pow((P_TARGET[1]-P_START[1]), 2)+math.pow((P_TARGET[2]-P_START[2]), 2))
eAB = ((P_TARGET[0]-P_START[0])/l_len, (P_TARGET[1]-P_START[1])/l_len, (P_TARGET[2]-P_START[2])/l_len)
count = 0
qiedian = [P_START]

# set-decorate
# Control the use of greedy Rules
# Closure should be learned


class DataProcessor(object):
    def __init__(self, path):
        self.path = path
        return

    # Get Data from Excel
    # Could think about Transformation
    def get_source(self):
        df = pd.read_excel(self.path)
        return df[['X坐标（单位: m）', 'Y坐标（单位:m）', 'Z坐标（单位: m）', '校正点类型', '第三问点标记']]

    @staticmethod
    # Find available area of solution
    def find_avaliable(p_data, greedObj, p_last, flag=1):
        t = 0
        global qiedian
        narrow_data_0 = p_data[((p_data['X坐标（单位: m）'] < (greedObj.p_cur[0]+1*greedObj.d_max)) &
                                (p_data['X坐标（单位: m）'] > greedObj.p_cur[0]) &
                                (p_data['Y坐标（单位:m）'] < (greedObj.p_cur[1]+1*greedObj.d_max)) &
                                (p_data['Y坐标（单位:m）'] > (greedObj.p_cur[1]-1*greedObj.d_max)) &
                                (p_data['Z坐标（单位: m）'] < (greedObj.p_cur[2]+1*greedObj.d_max)) &
                                (p_data['Z坐标（单位: m）'] > (greedObj.p_cur[2]-1*greedObj.d_max)) &
                                ((p_data['校正点类型'] == greedObj.cate) |
                                 (p_data['校正点类型'] == 'A 点') |
                                 (p_data['校正点类型'] == 'B点'))
                                )][['X坐标（单位: m）',
                                    'Y坐标（单位:m）',
                                    'Z坐标（单位: m）',
                                    '第三问点标记']]
        # print(narrow_data_0)
        list_0 = narrow_data_0.index.tolist()
        narrow_data_0['dist_line'] = None
        # 612, 326
        if 326 in narrow_data_0.index.tolist():
            t = 1
            min_l = (30 - max(greedObj.tor[0], greedObj.tor[1]))/delta
            coord = narrow_data_0.loc[326, :]
            square = math.pow((coord[0]-greedObj.p_cur[0]), 2) + \
                     math.pow((coord[1]-greedObj.p_cur[1]), 2) + \
                     math.pow((coord[2]-greedObj.p_cur[2]), 2)
            dist_calc = math.sqrt(square)
            if dist_calc < min_l:
                return narrow_data_0, t
            else:
                print('直飞也到达不了')
                t = 0
        for index in list_0:
            p_temp = narrow_data_0.loc[index, :]
            dist_calc = 0
            if flag == 1:
                square = math.pow((p_temp[0]-greedObj.p_cur[0]), 2) + \
                         math.pow((p_temp[1]-greedObj.p_cur[1]), 2) + \
                         math.pow((p_temp[2]-greedObj.p_cur[2]), 2)
                dist_calc = math.sqrt(square)
            elif flag == 2:
                p_O, e_vertical = calc_O_coord(p_last, greedObj.p_cur, p_temp)
                if p_O is not None:
                    if p_O == 1:
                        square = math.pow((p_temp[0]-greedObj.p_cur[0]), 2) + \
                                 math.pow((p_temp[1]-greedObj.p_cur[1]), 2) + \
                                 math.pow((p_temp[2]-greedObj.p_cur[2]), 2)
                        dist_calc = math.sqrt(square)
                    else:
                        p_D = fsolve(calc_D, [greedObj.p_cur[0], greedObj.p_cur[1], greedObj.p_cur[2]], args=(p_last, greedObj.p_cur, p_temp, p_O, e_vertical))
                        # Assert p_D to check
                        eOD = (p_D[0]-p_O[0], p_D[1]-p_O[1], p_D[2]-p_O[2])
                        mm_OD = math.sqrt(math.pow((p_D[0]-p_O[0]), 2) + \
                                          math.pow((p_D[1]-p_O[1]), 2) + \
                                          math.pow((p_D[2]-p_O[2]), 2))
                        eOB = (greedObj.p_cur[0]-p_O[0], greedObj.p_cur[1]-p_O[1], greedObj.p_cur[2]-p_O[2])
                        beta = math.acos(np.dot(eOD, eOB)/(200*mm_OD))
                        if beta > math.pi/2:
                            print('Solution Should be checked')
                            # dist_calc = 1e6
                            dist_calc = 200*beta + math.sqrt(math.pow((p_temp[0]-p_O[0]), 2) + \
                                                             math.pow((p_temp[1]-p_O[1]), 2) + \
                                                             math.pow((p_temp[2]-p_O[2]), 2))
                        else:
                            dist_calc = 200*beta + math.sqrt(math.pow((p_temp[0]-p_O[0]), 2) + \
                                                             math.pow((p_temp[1]-p_O[1]), 2) + \
                                                             math.pow((p_temp[2]-p_O[2]), 2))
            narrow_data_0.loc[index, 'dist_line'] = dist_calc
            if dist_calc >= 1*greedObj.d_max:#-400*math.pi:
                narrow_data_0 = narrow_data_0.drop([index])
        if narrow_data_0.shape[0] < 1:
            raise ValueError('No Available choice')
        return narrow_data_0, t


class GreedyObject(object):
    def __init__(self, rule_flag, vi=0, hi=0):
        self.rule_ctrl = rule_flag
        self.tor = (vi, hi)
        self.cate = 1
        self.p_cur = (0.0, 0.0, 0.0)
        self.d_max = 0
        self.result_line = []
        self.result_length = 0
        self.coord_line = []
        self.coord_line.append(P_START)
        return

    def category(self):
        # v_flag = 0
        # h_flag = 0
        temp_a = (a1-self.tor[0], a2-self.tor[1])
        temp_b = (b1-self.tor[0], b2-self.tor[1])
        if temp_a[0] <= temp_a[1]:
            min_a = temp_a[0]
        else:
            min_a = temp_a[1]
        if temp_b[0] <= temp_b[1]:
            min_b = temp_b[0]
        else:
            min_b = temp_b[1]
        if min_a <= min_b:
            # v_flag = 1
            # First Time Choice
            if self.tor[0] == 0 and self.tor[1] == 0:
                self.cate = 1
                self.d_max = min_a/delta
                return
            if self.tor[0] is not 0:
                self.cate = 1
                self.d_max = min_a/delta
            else:
                self.cate = 0
                self.d_max = min_b/delta
        else:
            # h_flag = 1
            if self.tor[1] is not 0:
                self.cate = 0
                self.d_max = min_b/delta
            else:
                self.cate = 1
                self.d_max = min_a/delta
        return

    def choose(self, avaliable_data):
        list_index = avaliable_data.index.tolist()
        comp_list = []
        du_list = []
        for i in list_index:
            p_temp = avaliable_data.loc[i, :]
            t_projection = calc_projection(p_temp, self.p_cur, self.d_max, self.rule_ctrl)
            # Compare To Choose With angle and line-length
            comp_list.append((str(i), t_projection, avaliable_data.loc[i, ['dist_line']]))
        result_list = sorted(comp_list, key=lambda x: x[1], reverse=True)
        # 轮盘赌
        cum = 0
        for item in result_list:
            du_list.append(item[1])
            cum += item[1]
        du_cumsum = np.cumsum(du_list)
        rand_t = np.random.uniform(0, 1, size=[1, 1])[0][0]
        if rand_t < du_cumsum[0]/cum:
            return result_list[0]
        for i in range(1, len(result_list)):
            if (rand_t >= du_cumsum[i-1]/cum) and (rand_t < du_cumsum[i]/cum):
                return result_list[i]

    def after_choose(self, avaiable_data, best_choice):
        b_index = int(best_choice[0])
        b_series = avaiable_data.loc[b_index, :]
        dist_cost = b_series['dist_line']
        self.p_cur = (b_series['X坐标（单位: m）'], b_series['Y坐标（单位:m）'], b_series['Z坐标（单位: m）'])
        is_cls = b_series['第三问点标记']
        # Update vi,hi
        self.tor = (self.tor[0]+dist_cost*delta, self.tor[1]+dist_cost*delta)
        print(self.tor)
        if self.rule_ctrl == 1 or self.rule_ctrl == 2:
            if self.cate:
                self.tor = (0, self.tor[1])
            else:
                self.tor = (self.tor[0], 0)
        elif self.rule_ctrl == 3:
            if is_cls == 1:
                tmp = np.array(np.random.uniform(0, 1, size=[1, 1]))[0][0]
                print(tmp)
                if self.cate:
                    if tmp >= 0.2:
                        self.tor = (0, self.tor[1])
                    else:
                        self.tor = (min(self.tor[0], 5), self.tor[1])
                else:
                    if tmp >= 0.2:
                        self.tor = (self.tor[0], 0)
                    else:
                        self.tor = (self.tor[0], min(self.tor[1], 5))
            else:
                if self.cate:
                    self.tor = (0, self.tor[1])
                else:
                    self.tor = (self.tor[0], 0)
        print(self.tor)
        return

    def run(self, origin_data):
        global count
        global qiedian
        print('Start Searching')
        t1 = time.time()
        greed_obj.p_cur = P_START
        print(P_START)
        greed_obj.category()
        ava_data, _ = DataProcessor.find_avaliable(origin_data, greed_obj, P_START, 1)
        prime_choice = greed_obj.choose(ava_data)
        greed_obj.result_line.append(prime_choice[0])
        greed_obj.result_length += prime_choice[2]
        greed_obj.after_choose(ava_data, prime_choice)
        greed_obj.coord_line.append(greed_obj.p_cur)
        print(greed_obj.p_cur)
        # *******************************************
        try:
            while True:
                greed_obj.category()
                ava_data, t_flag = DataProcessor.find_avaliable(origin_data, greed_obj, greed_obj.coord_line[-2], 1)
                # Ending
                if t_flag:
                    greed_obj.result_length += math.sqrt(math.pow((P_TARGET[0]-greed_obj.p_cur[0]), 2) +\
                                                         math.pow((P_TARGET[1]-greed_obj.p_cur[1]), 2) +\
                                                         math.pow((P_TARGET[2]-greed_obj.p_cur[2]), 2))
                    break
                prime_choice = greed_obj.choose(ava_data)
                greed_obj.result_line.append(prime_choice[0])
                greed_obj.result_length += prime_choice[2]
                greed_obj.after_choose(ava_data, prime_choice)
                greed_obj.coord_line.append(greed_obj.p_cur)
                print(greed_obj.p_cur)
            print(P_TARGET)
            print('Reaching Target')
            print('Finish')
            print(greed_obj.result_line)
            with open('case2.txt', 'a') as f:
                f.write('0 ')
                for item in greed_obj.result_line[0:-1]:
                    f.write(item)
                    f.write(' ')
                f.write(greed_obj.result_line[-1])
                f.write(' 326')
                f.write('\n')
            print('实际规划路程: %f' % greed_obj.result_length)
            llength = math.sqrt(math.pow((P_TARGET[0]-P_START[0]), 2) +\
                                math.pow((P_TARGET[1]-P_START[1]), 2) +\
                                math.pow((P_TARGET[2]-P_START[2]), 2))
            print('A-B直线距离: %f' % llength)
            greed_obj.coord_line.append(P_TARGET)
            x_l = []
            y_l = []
            z_l = []
            for item in greed_obj.coord_line:
                x_l.append(item[0])
                y_l.append(item[1])
                z_l.append(item[2])
            # fig = plt.figure()
            # ax = Axes3D(fig)
            # ax.plot3D(x_l, y_l, z_l, c='r')
            # ax.set_xlabel('x')
            # ax.set_ylabel('y')
            # ax.set_zlabel('z')
            # plt.show()
            count += 1
            t2 = time.time()
            print('总用时: %f' % (t2 - t1))
            return
        except ValueError as e:
            print(e)
            # print('尝试失败一次')
            return 99


# Const P_TARGET
def calc_projection(p_avaliable, p_cur, dmax, flag=1):
    result_f = 0
    e_try = (p_avaliable[0]-p_cur[0], p_avaliable[1]-p_cur[1], p_avaliable[2]-p_cur[2])
    result = e_try[0]*eAB[0] + e_try[1]*eAB[1] + e_try[2]*eAB[2]
    e_try_model = math.sqrt(math.pow(e_try[0], 2) + \
                            math.pow(e_try[1], 2) + \
                            math.pow(e_try[2], 2))
    cos_angle = result/e_try_model
    angle = math.acos(cos_angle)
    if flag is 1:
        # if greed_obj.cate:
        #     limit = b2-(greed_obj.tor[1] + p_avaliable[4]*delta)
        # else:
        #     limit = a1-(greed_obj.tor[0] + p_avaliable[4]*delta)
        result_f = 1*result*math.cos(angle)# + 4*limit/delta
    elif flag == 2:
        if greed_obj.cate:
            limit = b2-(greed_obj.tor[1] + p_avaliable[4]*delta)
        else:
            limit = a1-(greed_obj.tor[0] + p_avaliable[4]*delta)
        result_f = result*math.cos(angle) + 4*limit/delta - 2*(12000-dmax)
    elif flag == 3:
        if greed_obj.cate:
            limit = b2-(greed_obj.tor[1] + p_avaliable[4]*delta)
        else:
            limit = a1-(greed_obj.tor[0] + p_avaliable[4]*delta)
        # result_f = 1*result*math.cos(angle) + 0.2*limit/delta
        result_f = 1*result*math.cos(angle)
    return result_f


# For Testing
if __name__ == '__main__':
    # TDD *****************************************************************************
    # df_test = pd.read_excel('test1.xlsx')
    # print(df_test[['编号', 'X坐标（单位: m）', 'Y坐标（单位:m）', 'Z坐标（单位: m）']])
    # dObj = DataProcessor('test1.xlsx')
    # df_test = dObj.get_source()
    # print(df_test['Y坐标（单位:m）'])
    # print(df_test)
    # **************************************
    # Get method should be override
    # p_cur = df_test.loc[0, :]
    # **************************************
    # print(p_cur[0], p_cur[1], p_cur[2])
    # narrow_data_0 = df_test[(df_test['X坐标（单位: m）'] < (p_cur[0]+15000)) &
    #                         (df_test['Y坐标（单位:m）'] < (p_cur[1]+15000)) &
    #                         (df_test['Y坐标（单位:m）'] > (p_cur[1]-15000)) &
    #                         (df_test['Z坐标（单位: m）'] < (p_cur[2]+15000)) &
    #                         (df_test['Z坐标（单位: m）'] > (p_cur[2]-15000)) &
    #                         ((df_test['校正点类型'] == 1) | (df_test['校正点类型'] == 'A 点') | (df_test['校正点类型'] == 'B点'))
    #                         ][['X坐标（单位: m）', 'Y坐标（单位:m）', 'Z坐标（单位: m）']]
    # list = narrow_data_0.index.tolist()
    # narrow_data_0 = narrow_data_0.drop([0])
    # print(narrow_data_0.drop([0]))
    # print(narrow_data_0.shape[0])
    # list_0 = narrow_data_0.index.tolist()
    # narrow_data_0['dist_line'] = 0.0
    # for index in list_0:
    #     p_temp = narrow_data_0.loc[index, :]
    #     square = math.pow((p_temp[0]-p_cur[0]), 2) + \
    #              math.pow((p_temp[1]-p_cur[1]), 2) + \
    #              math.pow((p_temp[2]-p_cur[2]), 2)
    #     dist_calc = math.sqrt(square)
    #     narrow_data_0.loc[index, 'dist_line'] = dist_calc
    #     if dist_calc >= 15000:
    #         narrow_data_0 = narrow_data_0.drop([index])
    # print(narrow_data_0)
    # print(narrow_data_0.shape[0])
    # list_choice = narrow_data_0.index.tolist()
    # greedyone = GreedyObject(rule_flag=1)
    # greedyone.choose(narrow_data_0, p_cur)
    # *******************************************
    # Init Process
    dObj = DataProcessor('test2.xlsx')
    origin_data = dObj.get_source()
    # greed_obj = GreedyObject(1)
    # greed_obj.run(origin_data)
    # Not using Thread for now
    for i in range(0, 500):
        greed_obj = GreedyObject(3)
        greed_obj.__init__(3)
        greed_obj.run(origin_data)
    print('成功: %d次' % count)
    print('成功概率为: %f' % (count/500))

# case1
# Start Searching
# (0.0, 50000.0, 5000.0)
# (13.387919852713356, 13.387919852713356)
# (0, 13.387919852713356)
# (11392.9607416196, 56973.0182393612, 4097.85801775604)
# (11.596245586699835, 24.98416543941319)
# (11.596245586699835, 0)
# (19161.9638903652, 65574.6630601265, 3741.19548925368)
# (14.22779621469767, 2.6315506279978362)
# (0, 2.6315506279978362)
# (21051.2140034336, 64394.270631266, 2340.31489767007)
# (16.825995976673227, 19.457546604671062)
# (16.825995976673227, 0)
# (36978.9721462768, 62570.817708528, 7448.70804901168)
# (23.193624706858234, 6.3676287301850065)
# (0, 6.3676287301850065)
# (43317.2421050901, 62101.400590118, 7839.44727615169)
# (14.972984357892956, 21.340613088077962)
# (14.972984357892956, 0)
# (57582.3792740119, 64320.5720267624, 3868.1250444089)
# (20.95012860805725, 5.977144250164292)
# (0, 5.977144250164292)
# (63446.6597331125, 65392.200782765, 4301.80683281052)
# (16.03346244849564, 22.010606698659934)
# (16.03346244849564, 0)
# (78740.8838682736, 69517.1610105627, 1823.23278512447)
# (22.887029947029824, 6.853567498534185)
# (0, 6.853567498534185)
# (84799.7329800997, 70649.2108792224, 4819.93063308241)
# (100000.0, 59652.34338, 5022.001164)
# Reaching Target
# Finish
# ['503', '311', '569', '75', '524', '194', '450', '341', '83']
# 实际规划路程: 113408.696556
# A-B直线距离: 100464.761070
# 总用时: 0.623001
# case2
# Start Searching
# (0.0, 50000.0, 5000.0)
# (5.655760961595715, 5.655760961595715)
# (0, 5.655760961595715)
# (2959.76373112204, 54815.7311771262, 4809.83181049582)
# (9.799596729693368, 15.455357691289084)
# (9.799596729693368, 0)
# (12712.8372282571, 53865.1451047564, 4887.54630795409)
# (15.133750053659025, 5.334153323965658)
# (0, 5.334153323965658)
# (17780.0238454461, 52287.8820953331, 5425.18268066295)
# (13.921985777966604, 19.256139101932263)
# (13.921985777966604, 0)
# (28165.2376874816, 61559.6633087463, 5480.81169914034)
# (19.446311179345287, 5.5243254013786816)
# (0, 5.5243254013786816)
# (33371.0408367161, 59710.965868434, 5490.93523215335)
# (11.252042644972965, 16.776368046351646)
# (11.252042644972965, 0)
# (44286.2042253251, 57515.6466878164, 7118.27833656385)
# (16.603642889139508, 5.3516002441665425)
# (0, 5.3516002441665425)
# (47236.3361975397, 61603.8072585053, 5322.92609587536)
# (9.436726707112685, 14.788326951279227)
# (9.436726707112685, 0)
# (55874.0996157838, 65143.360341756, 6705.82813363083)
# (18.15390257286562, 8.717175865752935)
# (0, 8.717175865752935)
# (64420.2214315759, 64125.8260844612, 5321.06063713932)
# (5.776163625358746, 14.49333949111168)
# (5.776163625358746, 0)
# (69704.8897957998, 66433.0855333312, 4985.05417486715)
# (15.260882021008982, 9.484718395650237)
# (0, 9.484718395650237)
# (79005.7527529546, 68248.8267170088, 5381.1794718486)
# (9.834209701690867, 19.318928097341104)
# (9.834209701690867, 0)
# (87932.9914306055, 72373.7379514945, 5346.57662950522)
# (18.874085553469406, 9.039875851778541)
# (0, 9.039875851778541)
# (90959.6233036866, 80891.8083125556, 5383.07655321574)
# (100000.0, 74860.5488999781, 5499.61109489643)
# Reaching Target
# Finish
# ['140', '163', '114', '8', '309', '121', '123', '231', '160', '92', '93', '61', '166']
# 实际规划路程: 119996.549492
# A-B直线距离: 103045.118773
# 总用时: 0.803285
