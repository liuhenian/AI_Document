# 1 环境需求
首先确保系统包是最新的，并安装 Python 3.10+（Ubuntu 24 默认自带 Python 3.12，完全满足要求）。

```
# 安装 pip 和 venv（如果未安装） 虚拟环境
sudo apt install -y python3-pip python3-venv

# 创建项目目录
mkdir langgraph-demo && cd langgraph-demo

# 创建 Python 虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装需要的python库
pip install -U langgraph langchain-openai python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

配置API
```
# 配置API秘钥
vim .env

# 将以下内容写入
# .env
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 如果使用代理或第三方兼容 API，取消注释并修改
# OPENAI_BASE_URL="https://api.your-provider.com/v1"

```
