# 1 数据库用户名密码

``` 
redis的密码
用户名：auth
密码： uA+SThCdZ:ZX8G&qh@
```

# 2 redis 数据结构

``` c
apm_device_info
{
    "1.1.1.1": {
        "whole_device_type": BOX | AC | VSU | VAC | CHASSIS | CHASSIS-VSU,
        "device_name": "AC_RGOS",
        "project": "11.9WPL9",
        "health_score": 90
    },
    ...
}

apm_device_cards
{
    "1.1.1.1": [
        "EXP_JOB1",
        "EXP_JOB2",
    ]
}

apm_card_info
{
    "EXP_JOB1": {
        "device_id": "1",
        "slot_id": "30",
        "software_number": "M123"，
        "product": "S7610",
        "comp_type": "A",
        "health_score": 90
    }
}
```

# 3 获取项目信息接口
```
[http://build.ruijie.com.cn/ngcf/interface/task_msg/get_task_by_softnum.jhtml?softNum=MHX9OAV07192026&topic=1C301E4269B0E26F]
```