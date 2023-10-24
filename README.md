# FangBot

Webhook based discord bot that fetches information from VRising servers and displays it in discord.
![Image 1](https://github.com/mnjm/FangBot/blob/7da78d18317642ce8e9f5b92f2484bf05f5f970f/FangBot-Image1.png)

![Image 2](https://github.com/mnjm/FangBot/blob/f6778f21efc0f6d07484b8263352c311d28a851d/FangBot-Update.png)

## Configuration

### Create config.json file that contains
```
{
    "botname": "FangBot",
    "bot_avatar_url": "https://havi-x.github.io/hosted-images/TSR/BatWithFang.jpeg",
    "a2s_timeout": 20,
    "update_interval": 300,
    "embed_color": "#FF0000",
    "servers_info": {
        "server1": {
            "vr_ip": "<VRising server IP>",
            "vr_query_port": <VRising query port>,
            "last_message_id": 0,
            "timezone": "Asia/Kolkata",
            "vr_metrics_port": 0
        },
        "server2": {
            "vr_ip": "<VRising server IP>",
            "vr_query_port": <VRising query port>,
            "last_message_id": 0,
            "timezone": "Asia/Kolkata",
            "vr_metrics_port": 0
        }
    }
}
```
### Load webhook urls into environment vars
```
export FANGBOT_WEBHOOK_URLS='{"server1": "<webhook_link>", "server2": "<webhook_link>"}' 
```
### To enable castle territories, enable Metrics API in `ServerHostSettings.json` and configure the outgoing port
```
{
  "Name": "VRising Server",
  ...
  "API": {
    "Enabled": true,
    "BindPort": <outgoing port>
  },
  ...
}
```
  And mention the port in `config.json` in `vr_metrics_port`

## Run
`python main.py config.json`
