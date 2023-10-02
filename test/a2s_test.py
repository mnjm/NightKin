from steam import game_servers as gs
import sys

TIMEOUT = 120

def main():
    # server_info = ("144.126.153.234", 31115)
    server_info = (sys.argv[1], int(sys.argv[2]))
    info = gs.a2s_info(server_info, timeout=TIMEOUT)
    print(info)
    players = gs.a2s_players(server_info, timeout=TIMEOUT)
    print(players)

if __name__ == "__main__":
    main()
