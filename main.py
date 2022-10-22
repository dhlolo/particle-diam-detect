# 这是一个示例 Python 脚本。

# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。
import cv2
import numpy as np
import math
import sys

def test_cv(filepath):
    lena = cv2.imread(filepath)
    cv2.imshow('image', lena)
    cv2.waitKey(0)

def cv_show(name, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)  # 等待时间，毫秒级
    cv2.destroyAllWindow()

def get_distance(point1, point2):
    square = math.pow(point2[0] - point1[0], 2) + math.pow(point2[1] - point1[1], 2)
    return math.sqrt(square)

def get_particle_diam(box):
    w = get_distance(box[0], box[1])
    h = get_distance(box[2], box[1])
    return min(w, h)

def analyse_particle_diam(filepath):
    img = cv2.imread(filepath)
    # 电镜图像内容
    content = img[0:690,0:1278]
    # TODO: 标尺内容
    # TODO: OCR相关暂时跳过，在Mn对照组采用的20.00KX中，使用人工读标尺 36pt -> 200nm 截取参考： https://docs.opencv.org/4.1.2/d3/df2/tutorial_py_basic_ops.html#:~:text=by%20invalid%20datatype.-,Image%20ROI,-Sometimes%2C%20you%20will
    scale = img[693:768,0:150]
    # 灰度处理
    gray = cv2.cvtColor(content, cv2.COLOR_BGR2GRAY)
    # 使用自适应阈值分析进行图像二值化
    dst = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 101, 1)
    # 形态学去噪
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, element)  # 开运算去噪
    # 轮廓检测函数
    contours, hierarchy = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 绘制轮廓
    cv2.drawContours(dst, contours, -1, (120, 0, 0), 2)
    count = 0  # 颗粒总数
    ares_avrg = 0  # 面积平均
    diam_qvrg = 0  # 粒径平均
    # 遍历找到的所有米粒
    for cont in contours:
        ares = cv2.contourArea(cont)
        # 过滤面积小于50的形状
        if ares < 50:
            continue
        # if ares > 3000:
        #     continue
        # 计算包围性状的粒径
        rect = cv2.minAreaRect(cont)  # 最小外接矩形
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        diam = get_particle_diam(box)
        if diam / 36 * 200 > 3000:
            continue
        count += 1
        ares_avrg += ares
        diam_qvrg += diam
        # 打印出每个颗粒的粒径
        print("{}-粒径:{}".format(count, diam / 36 * 200), end="  ")
        # 提取矩形坐标（x,y）
        rect = cv2.boundingRect(cont)
        # 打印坐标
        print("x:{} y:{}".format(rect[0], rect[1]))
        # 绘制矩形
        cv2.rectangle(img, rect, (0, 0, 255), 1)
        # 防止编号到图片之外（上面）,因为绘制编号写在左上角，所以让最上面的颗粒的y小于10的变为10个像素
        y = 10 if rect[1] < 10 else rect[1]
        # 在颗粒左上角写上编号
        cv2.putText(img, str(count), (rect[0], y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 255, 0), 1)
        # print('编号坐标：',rect[0],' ', y)
    print('个数', count)
    print("颗粒平均粒径:{}".format(round(diam_qvrg / count / 36 * 200, 2)))  # 打印出每个颗粒的粒径

    cv2.namedWindow("imgshow", 2)  # 创建一个窗口
    cv2.imshow('imgshow', img)  # 显示原始图片（添加了外接矩形）

    cv2.namedWindow("dst", 2)  # 创建一个窗口
    cv2.imshow("dst", dst)  # 显示灰度图

    cv2.waitKey()

if __name__ == '__main__':
    path = sys.argv[0]
    analyse_particle_diam(path)
