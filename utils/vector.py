import math


class Vector(object):
    """根据坐标轴列表输入 创建向量, 并创建该向量所处的空间维度"""
    def __init__(self, coordinates):
        super(Vector, self).__init__()
        try:
            if not coordinates:
                raise ValueError
            self.coordinates = tuple(coordinates)
            self.dimension = len(coordinates)
        except ValueError:
            raise ValueError('The coordinates must be nonempty')
        except TypeError:
            raise TypeError('The coordinates must be an iterable')

    # '''能够使python的内置print函数 输出向量坐标轴'''

    def __str__(self):
        return 'Vector: {}'.format(self.coordinates)

    def __eq__(self, v):
        return self.coordinates == v.coordinates

    # 计算向量长度
    def magnitude(self):
        coordinates_squared = [x ** 2 for x in self.coordinates]
        return math.sqrt(sum(coordinates_squared))

    # 将向量归一化
    def normalized(self):
        try:
            magnitude = self.magnitude()
            return [x * (1. / magnitude) for x in self.coordinates]
        except ZeroDivisionError:
            raise Exception('Cannot normalized the zero myVector2')
