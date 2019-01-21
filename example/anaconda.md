## For Python 3.6

### 直接使用 [finance_36.yml](https://anaconda.org/guqiangjs/finance_36) 安装。

### 或者单独安装流程：

1. 创建 conda 工作区

    `conda create -n finance_36 python=3.6`

2. 激活工作区

    `conda activate finance_36`

3. 安装 zipline

    ~~`conda install -c Quantopian zipline`~~ 改为使用 `pip install zipline`

    > 使用这个语句安装会把Python降版
    > ```Batchfile
    > The following packages will be DOWNGRADED:
    > 
    > python:            3.6.8-h9f7ef89_0                   --> 2.7.15-hcb6e200_5
    > vc:                14.1-h0510ff6_4                    --> 9-h7299396_1
    > 
    > Proceed ([y]/n)? n
    > ```
    > [The latest zipline-1.1.1 is not supported by Python 3.6?](https://github.com/quantopian/zipline/issues/1938)
    > 
    > Sorry for the trouble. Zipline should run on python 3.6, but we don't have conda packages for it. We have 2.7, 3.4, and 3.5. If you have a local compiler toolchain set up properly, you should be able to pip install zipline in your 3.6 environment.

4. 安装 cvxopt

    `conda install -c conda-forge cvxopt`

5. 安装 TA-Lib

    ~~`conda install -c quantopian ta-lib`~~

    > 会将 Python3.6 降版至 3.5

    ~~`pip install ta-lib`。无论是下载 [ta-lib-0.4.0-msvc.zip](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip) 还是 [https://github.com/afnhsn/TA-Lib_x64 ](https://github.com/afnhsn/TA-Lib_x64)。虽然用 `nmake` 编译不出错，但是安装时还是会有以下错误。~~

    >```Batchfile
    > Creating library build\temp.win-amd64-3.6\Release\talib\_ta_lib.cp36-win_amd64.lib and object build\temp.win-amd64-3.6\Release\talib\_ta_lib.cp36-win_amd64.exp
    > Generating code
    > c:\users\guqiang\appdata\local\temp\pip-build-c6h7q2na\ta-lib\talib\_ta_lib.c(243658) : fatal error C1002: compiler is out of heap space in pass 2
    > LINK : fatal error LNK1257: code generation failed
    > error: command 'C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\VC\\BIN\\x86_amd64\\link.exe' failed with exit status 1257
    > ```

    所以改为使用 `pip install TA_Lib-0.4.17-cp36-cp36m-win_amd64.whl`

    > You might also try these unofficial windows binaries for both 32-bit and 64-bit:
    > 
    > https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

6. 安装 pyfoilo

    `pip install pyfolio`

7. 安装 QUANTAXIS

    `pip install quantaxis`

8. 安装 pyecharts_snapshot

    `pip install pyecharts_snapshot`

9. 重新安装 pytdx

    `pip uninstall pytdx`，`pip install pytdx`

10. 安装 nb_conda_kernels（用于jupyter中可选Python运行环境）

    `conda install ipykernel`，
    `python -m ipykernel install --user --name finance_36 --display-name finance_py_36`

11. 安装 portfolioopt

    `pip install portfolioopt`

---

## jupyter lab 插件

https://github.com/ipython-contrib/jupyter_contrib_nbextensions

---

## For Python 3.5.6

1. 创建 conda 工作区

    `conda create -n finance356 python=3.5.6`

2. 激活工作区

    `conda activate finance356`

3. 安装 zipline

    `conda install -c quantopian zipline`

4. 安装 cvxopt

    `conda install -c conda-forge cvxopt`

5. 安装 TA-Lib

    `conda install -c quantopian ta-lib`

6. 安装 pyfoilo

    `pip install pyfolio`

7. 安装 QUANTAXIS

    `pip install quantaxis`

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
