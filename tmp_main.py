import subprocess
import requests
from tmp_yclass import yClass
import pickle

# 创建一个包含yClass的list
yList = []
yList.append(yClass("info1", [[1, 2], [3, 4]]))
yList.append(yClass("info2", [[5, 6], [7, 8]]))
yList.append(yClass("info3", [[9, 10], [11, 12]]))

# 创建一个空list存储子程序返回的按钮信息
ansList = []

# 通过subprocess调用子程序
p = subprocess.Popen(['streamlit', 'run', 'tmp_st_app.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# 循环将yList中的元素发送给子程序，并接收子程序返回的按钮信息
for y in yList:
    # 序列化yClass
    data = pickle.dumps(y)

    p.stdin.write(data)
    p.stdin.flush()
    ans = p.stdout.readline()

    if ans == "A":
        ansList.append(y)

# 关闭子程序
p.kill()

# 打印ansList的长度
print("ansList的长度为：", len(ansList))
