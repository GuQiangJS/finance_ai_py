# 安装说明

## For Python 3.5

> `zipline` 对Python3.5以上版本支持有问题，需要使用Python3.5版本。
> [The latest zipline-1.1.1 is not supported by Python 3.6?](https://github.com/quantopian/zipline/issues/1938)
> Sorry for the trouble. Zipline should run on python 3.6, but we don't have conda packages for it. We have 2.7, 3.4, and 3.5. If you have a local compiler toolchain set up properly, you should be able to pip install zipline in your 3.6 environment.

1. 创建 conda 工作区

    `conda create -n finance35 python=3.5`

2. 激活工作区

    `conda activate finance35`

3. 安装 zipline

    `conda install -c quantopian zipline`

4. 安装 cvxopt

    `conda install -c conda-forge cvxopt`

5. 安装 TA-Lib

    `conda install -c quantopian ta-lib`

6. 安装 pyfoilo

    `pip install pyfolio`

7. 安装 QUANTAXIS

    ~~`pip install quantaxis`~~ 改为使用 `pip install git+https://github.com/GuQiangJS/QUANTAXIS.git --upgrade` 或者下载代码至本地安装

    ```
    $ git clone https://github.com/GuQiangJS/QUANTAXIS.git
    $ cd QUANTAXIS
    $ pip install
    ```

    > 从我个人Fork的分支安装只是解决了我个人遇到的不支持Python3.5以上版本的情况，不代表所有代码均支持。

    > 坑爹的代码 (**`async`**) 不支持 Python3.5
    >
    > [PEP 530 -- Asynchronous Comprehensions](https://www.python.org/dev/peps/pep-0530/)
    >
    > ```python
    > try:
    >     res = pd.DataFrame([item async for item in cursor])
    > except SyntaxError:
    >     print('THIS PYTHON VERSION NOT SUPPORT "async for" function')
    >     pass
    > ```

8. 安装 pyecharts_snapshot

    `pip install pyecharts_snapshot`

9. 重新安装 pytdx

    ```batchfile
    pip uninstall pytdx
    pip install pytdx
    ```

10. 安装 nb_conda_kernels（用于jupyter中可选Python运行环境）

    `conda install ipykernel`，
    `python -m ipykernel install --user --name finance35 --display-name finance_py_35`

11. 安装 portfolioopt

    `pip install portfolioopt` 或者 `pip install git+https://github.com/czielinski/portfolioopt.git --upgrade`

12. 安装 python.app

    `conda install -c conda-forge python.app`
    > 对于在Mac下运行来说，需要安装这个。**并且以 pythonw 方式运行**。否则会出现以下错误：
    > ImportError: Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a framework. See the Python documentation for more information on installing Python as a framework on Mac OS X. Please either reinstall Python as a framework, or try one of the other backends. If you are using (Ana)Conda please install python.app and replace the use of 'python' with 'pythonw'. See 'Working with Matplotlib on OSX' in the Matplotlib FAQ for more information.
    > https://matplotlib.org/faq/osx_framework.html#conda

---

### sphinxcontrib-napoleon

https://github.com/sphinx-contrib/napoleon

`pip install sphinxcontrib-napoleon`

### jupyter 插件

https://github.com/ipython-contrib/jupyter_contrib_nbextensions

```batchfile
conda install -c conda-forge jupyter_contrib_nbextensions
# Install nbextension files, and edits nbconvert config files
jupyter contrib nbextension install --user
# Install yapf for code prettify
pip install yapf
# Install autopep8
pip install autopep8
# Jupyter extensions configurator 
pip install jupyter_nbextensions_configurator
# Enable nbextensions_configurator
jupyter nbextensions_configurator enable --user
```

[Jupyter Notebook 小贴士](http://blog.leanote.com/post/carlking5019/Jupyter-Notebook-Tips)

> 如果选择了 `autopep8` ，还需要安装 `pip install autopep8`

查看插件是否启动 `http://localhost:8888/nbextensions`

### node.js

`conda install -c conda-forge nodejs`

### jupyter 支持进度条

https://tqdm.github.io/

`conda install -c conda-forge tqdm`

> 需要先安装 `ipywidgets`。`conda install -c conda-forge ipywidgets`
> 貌似暂时只能用在 jupyter notebook 中。

### pylint

https://www.pylint.org/#install

[如何使用Pylint 来规范Python 代码风格 - IBM](https://www.ibm.com/developerworks/cn/linux/l-cn-pylint/index.html)

`pip install pylint # see note`