"""
判断某个坐标是否在某个封闭区域内
"""


# 判断该点是否在该条线上

# point:点坐标,如:[113.775698, 30.236892]
# o : 该条线的起点
# d : 该条线的终点
def is_in_line(point, o, d):
    # 先判断该点是否在线段范围内,如果不在,
    # 则就算在该方程的直线上但也不在该线段上
    # print("point", point, o, d)
    if o[1] > point[1] and d[1] > point[1]:  # 该点纵坐标小于线段最小纵坐标
        return False
    if o[1] < point[1] and d[1] < point[1]:  # 该点纵坐标大于线段最大纵坐标
        return False
    if o[0] > point[0] and d[0] > point[0]:  # 该点横坐标小于线段最小横坐标
        return False
    if o[0] < point[0] and d[0] < point[0]:  # 该点横坐标大于线段最大横坐标
        return False

    # 若线段为垂直直线,则该点的横坐标等于该线段的横坐标才说明在该线段上
    if o[0] == d[0]:
        return True if point[0] == o[0] else False

    # 通过输入的两个点计算一元一次方程,通过输入x,计算y
    a = (d[1] - o[1]) / (d[0] - o[0])
    b = (d[0] * o[1] - o[0] * d[1]) / (d[0] - o[0])
    y = a * point[0] + b
    return True if y == point[1] else False


# 假设以该点向右水平做射线,判断该点是否与该线段有交点(当射线与线段下端点相交时为False)
# point:点坐标,如:[113.775698, 30.236892]
# o : 该条线的起点
# d : 该条线的终点
def is_ray_intersects_segment(point, o, d):
    if o[1] == d[1]:  # 如果线段是水平直线,则直接无交点
        return False
    # 先判断该点是否在线段范围内,如果不在,
    # 则就算在该方程的直线上但也不在该线段上
    if o[1] > point[1] and d[1] > point[1]:  # 该点纵坐标小于等于线段最小纵坐标
        return False
    if o[1] < point[1] and d[1] < point[1]:  # 该点纵坐标大于等于线段最大纵坐标
        return False
    if o[1] == point[1] and d[1] > point[1]:  # 若o点为下端点且交点为下端点时
        return False
    if d[1] == point[1] and o[1] > point[1]:  # 交d点为下端点且交点为下端点时
        return False

    # 注释部分为 先求出一元一次方程求交点
    # 若线段为垂直直线,则该点的横坐标应该小于该点的横坐标才能有交点
    # if o[0] == d[0]:
    #     return True if point[0] < o[0] else False
    #
    # # 通过输入的两个点计算一元一次方程,通过输入x,计算y
    # a = (d[1] - o[1]) / (d[0] - o[0])
    # b = (d[0] * o[1] - o[0] * d[1]) / (d[0] - o[0])
    # x = (point[1] - b) / a

    # 利用三角形比例关系求交点
    x = d[0] - (d[0] - o[0]) * (d[1] - point[1]) / (d[1] - o[1])
    # 如果该点的横坐标小于相同水平线上交点的横坐标,则有交点
    return True if point[0] < x else False


"""
判断是否在矩形区域内
point_coord:点坐标,如:[113.775698, 30.236892]
polygon_coords:封闭多边形,如:[[[113.76708006000003,30.231097985000019],
[113.77808006000006,30.231097985000019],[113.76708006000003,30.231097985000019]]]
is_contains_edge: 是否包含边界,如果为true,那么在边界上时也算在多边形内
"""


def is_point_in_polygon(point_coord, polygon_coords, is_contains_edge):
    intersect_count = 0  # 交点个数
    for polygon in polygon_coords:
        # 循环每条边
        for i in range(len(polygon) - 1):
            # print("i", polygon[i])
            origin_point = polygon[i]
            destination_point = polygon[i + 1]
            # print("origin_point", origin_point)
            # 是否包含存在直线上的点
            if is_in_line(point_coord, origin_point, destination_point):
                return True if is_contains_edge else False

            if is_ray_intersects_segment(point_coord, origin_point, destination_point):
                # 有交点就加1
                intersect_count += 1
    return True if intersect_count % 2 == 1 else False
