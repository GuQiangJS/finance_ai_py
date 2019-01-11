安装 [QUANTAXIS](https://github.com/QUANTAXIS/QUANTAXIS/)

> https://github.com/QUANTAXIS/QUANTAXIS/blob/master/Documents/install.md
> 
> `pip install quantaxis`

---

建议使用 [QADataStruct](https://github.com/QUANTAXIS/QUANTAXIS/blob/master/QUANTAXIS/QAData/QADataStruct.py) 数据类型。

如果需要使用 [QADataStruct](https://github.com/QUANTAXIS/QUANTAXIS/blob/master/QUANTAXIS/QAData/QADataStruct.py) 数据类型 需要将数据下载到本地。

首先本地需要安装 [MongoDB](https://www.mongodb.com/download-center/community)

> [https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)

数据下载到本地可以使用 [update_x.py](https://github.com/QUANTAXIS/QUANTAXIS/blob/master/config/update_x.py)

[update_date.py](https://github.com/QUANTAXIS/QUANTAXIS/blob/master/config/update_data.py)用来每日更新数据

数据下载完成后的使用参考 [从本地mongodb中读取数据.ipynb](从本地mongodb中读取数据.ipynb)

---

* `calculator.py` 计算器

* `ploter.py` 画图器

* `quantaxis_ext.py` 数据读取器

* `simulate.py` 模拟器

* `units.py` 帮助类

* `update_data.py` 日常数据更新器（更新到本地mongodb）

* `update_x.py` 数据下载器（下载到本地mongodb）（比`update_data.py` 多了一个下载股票信息至本地。其他下载股票和指数分钟线数据的代码暂时被屏蔽）