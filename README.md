# NightKin

Discord webhook to display real-time updates of players on V Rising servers. Using Steam A2P API
![Image 1](https://github.com/mnjm/NightKin/blob/7da78d18317642ce8e9f5b92f2484bf05f5f970f/FangBot-Image1.png)

![Image 2](https://github.com/mnjm/NightKin/blob/f6778f21efc0f6d07484b8263352c311d28a851d/FangBot-Update.png)

## Configuration

### Create config.json file that contains
```json
{
    "botname": "NightKin",
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
```bash
export NIGHT_WEBHOOK_URLS='{"server1": "<webhook_link>", "server2": "<webhook_link>"}' 
```
### To enable castle territories, enable Metrics API in `ServerHostSettings.json` and configure the outgoing port
```json
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
