# 1 button的配置
```json
"actionButtons": {
        "defaultColor": "white",           // 按钮默认文字颜色
        "commands": [
            // 每个按钮一个对象
            {
                "name": "开始",      // 必填，显示在状态栏
                "command": "python3 main.py", // 必填，如 "npm run dev"
                "terminalName": "test1",   // 关键！指定终端名称，同名复用
                "tooltip": "悬停提示",       // 可选
                "singleInstance": false,    // 是否每次点击都新建终端
                "focus": false,             // 执行后是否聚焦终端
                "ignoreClear": false,       // 是否在执行前清屏
            },
        ]
    }
```

# 2 clang 配置