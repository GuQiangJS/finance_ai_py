## For Python 3.5

1. 创建 conda 工作区

    `conda create -n finance_35 python=3.5`

2. 激活工作区

    `conda activate finance_35`

3. 安装 zipline

    `conda install -c Quantopian zipline`

4. 安装 cvxopt

    `conda install -c conda-forge cvxopt`

5. 安装 TA-Lib

    `conda install -c quantopian ta-lib`

6. 安装 pyfoilo

    `pip install pyfolio`

## For Python 3.6

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

6. 安装 pyfoilo

    `pip install pyfolio`
