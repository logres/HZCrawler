# 说明

## 环境

安装python, 执行pip install -r requirements.txt, 然后 python main.py.


## Task配置

通过添加Task，能够让爬虫运行时，将爬取到的数据存储到指定的文件中，并支持增量存储。

修改 tasks.json

```json
  {
    "task_id": "task_001",  
    "device_id": "WL071534400",
    "property_name": "met_bar",
    "mode": "incremental",
  },
```

1. task_id: 任务ID， 随意
2. device_id: 设备ID, 在网页获取
3. property_name: 设备属性名称，遵循以下映射
   1. 风速: met_wind_speed
   2. 风向: met_wind_direction
   3. 大气压: met_bar
   4. 气温: met_temp
   5. 湿度: met_humi
   6. 浪级: wave_scale
4. mode: 存储模式，增量存储incremental, 全量模式full

其他字段不需要手动编辑，会自动生成。

## config配置

修改 config.json

```json
{
    "x_access_token": "6783d1c41059556afa13ab9c82a5057c",
    "base_url": "https://main-api-lightpole.weilanit.com",
}
```
base_url不需要修改, 登入系统后，按下F12，查看网络请求，找到请求头中的x_access_token，复制到配置文件中即可。


