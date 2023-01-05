
import numpy as np
import random
import time


'''
                   _ooOoo_
                  o8888888o
                  88" . "88
                  (| -_- |)
                  O\  =  /O
               ____/`---'\____
             .'  \\|     |//  `.
            /  \\|||  :  |||//  \
           /  _||||| -:- |||||-  \
           |   | \\\  -  /// |   |
           | \_|  ''\---/''  |   |
           \  .-\__  `-`  ___/-. /
         ___`. .'  /--.--\  `. . __
      ."" '<  `.___\_<|>_/___.'  >' "".
     | | :  `- \`.;`\ _ /`;.`/ - `  : | |
     \  \ `-.   \_ __\ /__ _/   .-` /  /
======`-.____`-.___\_____/___.-`____.-'======
                   `=---='
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            佛祖保佑       永无BUG
'''

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(0)


class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        # You are white or black
        self.color = color
        # the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need to add your decision to your candidate_list. The system will get the end of your candidate_list as your decision.
        self.candidate_list = []
        self.tree = []
        self.valid_list = []
        self.treedepth = 6
        self.ans = (-1, -1)
        self.turn = 0
        self.scorelist = []
        if color == 1:
            self.turn = 1
        self.point = [[-500, 25, -10, -5, -5, -10, 25, -500],
                      [25, 45,  -1, -1, -1,  -1, 45,   25],
                      [-10, -1,  -3, -2, -2,  -3, -1,  -10],
                      [-5, -1,  -2, -1, -1,  -2, -1,   -5],
                      [-5, -1,  -2, -1, -1,  -2, -1,   -5],
                      [-10, -1,  -3, -2, -2,  -3, -1,  -10],
                      [25, 45,  -1, -1, -1,  -1, 45,   25],
                      [-500, 25, -10, -5, -5, -10, 25, -500]]

    def go(self, chessboard):
        st = time.time()
        self.turn += 2
        self.candidate_list.clear()
        self.ans = (-1, -1)
        self.candidate_list = self.valid_point(chessboard, self.color)

        ap = self.minmax(chessboard, 1, self.color, -100000, 100000)

        if self.ans == (-1, -1):
            return []

        ed = time.time()
        print('old:',ed-st,'ab:',ap)
        return self.candidate_list

    def search(self, chessboard, depth, color):
        if depth == self.treedepth:
            return self.score(chessboard)

        valid_location = self.valid_point(chessboard, color)
        if len(valid_location) == 0:
            if self.turn > 60 - self.treedepth:
                return self.final_score(chessboard)
            return self.score(chessboard)

        score = -100000
        for location in valid_location:
            s = self.search(self.reverse(
                chessboard, location, color), depth+1, 0-color)
            if score < s:
                score = s
                if depth == 1:
                    self.ans = location

        return score

    def minmax(self, chessboard, depth, color, alpha, beta):  # state = 0, min; state = 1, max
        if depth == self.treedepth:
            if color == self.color:  # 这一层本是max点，上一层是min层
                return (self.score(chessboard), 100000)
            else:  # 上一层是max层
                return (self.score(chessboard), -100000)

        valid_location = self.valid_point(chessboard, color)

        if len(valid_location) == 0:
            if color == self.color:  # 这一层本是max点，上一层是min层
                if self.turn > 60 - self.treedepth:
                    return (self.final_score(chessboard), 100000)
                max_ = max(self.minmax(chessboard, depth+1, 0-color, alpha, beta))
                if alpha<max_: alpha=max_
            else:  # 上一层是max层
                if self.turn > 60 - self.treedepth:
                    return (self.final_score(chessboard), -100000)
                min_ = min(self.minmax(chessboard, depth+1, 0-color, alpha, beta))
                if beta>min_: beta=min_

        best = -100000
        for point in valid_location:
            cb_next = self.reverse(chessboard, point, color)
            score = self.minmax(cb_next, depth+1, 0-color, alpha, beta)

            if depth == 1:  # 在层数为1的时候，额外记录下结果
                self.scorelist.append(max(score))
                if best < max(score):
                    best = max(score)
                    self.ans = point
                    self.candidate_list.remove(self.ans)
                    self.candidate_list.append(self.ans)
                    

            if color == self.color:  # max node
                max_ = max(score)
                if alpha < max_:
                    alpha = max_
            else:  # min node
                min_ = min(score)
                if beta > min_:
                    beta = min_
            # 剪枝
            if alpha >= beta:
                break

        return (alpha, beta)

    def score(self, chessboard):
        res = 0
        for i in range(8):
            for j in range(8):
                res += self.color * chessboard[i][j] * self.point[i][j]
        return res

    def final_score(self, chessboard):
        res = 0
        # print(chessboard)
        for i in range(8):
            for j in range(8):
                res += - self.color * chessboard[i][j]
        return res

    def valid_point(self, chessboard, color):
        orient = [(1, 0), (-1, 0), (0, 1), (0, -1),
                  (1, -1), (-1, -1), (-1, 1), (1, 1)]
        valid_list = []
        for i in range(8):
            for j in range(8):
                if chessboard[i][j] == 0:
                    for ori in orient:
                        x = i + ori[0]
                        y = j + ori[1]
                        if x >= 0 and x < 8 and y >= 0 and y < 8 and chessboard[x][y] == 0 - color:
                            n = 1
                            validity = False
                            while i+ori[0]*n >= 0 and i+ori[0]*n < 8 and j+ori[1]*n >= 0 and j+ori[1]*n < 8:
                                if chessboard[ori[0]*n+i][ori[1]*n+j] == 0 - color:
                                    n += 1
                                elif chessboard[ori[0]*n+i][ori[1]*n+j] == color:
                                    valid_list.append((i, j))
                                    validity = True
                                    break
                                else:
                                    break
                            if validity:
                                break
        return valid_list

    def reverse(self, chessboard, put, color):
        orient = [(1, 0), (-1, 0), (0, 1), (0, -1),
                  (1, -1), (-1, -1), (-1, 1), (1, 1)]
        res = np.copy(chessboard)
        i = put[0]
        j = put[1]
        for ori in orient:
            x = put[0] + ori[0]
            y = put[1] + ori[1]
            # 周围该方向有一个不同颜色的棋子
            if x >= 0 and x < 8 and y >= 0 and y < 8 and chessboard[x][y] == 0 - color:
                n = 1
                validity = False
                # 判断是否可以翻转
                while i+ori[0]*n >= 0 and i+ori[0]*n < 8 and j+ori[1]*n >= 0 and j+ori[1]*n < 8:
                    if chessboard[ori[0]*n+i][ori[1]*n+j] == 0 - color:
                        n += 1
                    elif chessboard[ori[0]*n+i][ori[1]*n+j] == color and n != 1:
                        validity = True
                        break
                    else:
                        break
                if validity:  # 如果可以翻转则翻转
                    for k in range(0, n):
                        res[ori[0]*k+i][ori[1]*k+j] = color
        return res
