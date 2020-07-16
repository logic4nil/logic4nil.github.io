## tensorflow环境搭建

1. 安装virtualenv
   
    ```
    pip3 install virtualenv
    python3 -m virtualenv --system-site-packages ./py3
    # --sytem-site-packages: 
    #    give the virtual environment access to the system site-packages dir
    ```

2. tensorflow基础环境搭建
    ```
    source ./py3/bin/active 
    pip3 install tensorflow keras jupyter
   ```

3. jupyter交互环境
    ```
    python -m ipykernel install --user --name=py3
    jupyter kernelspec list # 查看所有juypter kernel
    jupyter notebook 
    ```
