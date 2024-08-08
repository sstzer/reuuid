import json
import os
import requests
from pathlib import Path

world_name='world'
list_file=['ops.json','banned-players.json','whitelist.json','usercache.json']
list_dir=[['playerdata','.dat'],['playerdata','.dat_old'],['advancements','.json'],['stats','.json']]
ignors=['']


class Player:
    def __init__(self,name: str,uuid: str,online_uuid: str):
        self.name=name
        self.uuid=uuid
        self.online_uuid=online_uuid


def get_uuid(user_name: str):
    if 'bot_' in user_name or 'BOT_' in user_name or 'Bot_' in user_name:
        return None
    try:
        resp=requests.get(f"https://api.mojang.com/users/profiles/minecraft/{user_name}")
        data=resp.json()
        if uuid:=data.get('id'):
            return f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError:
        print(f"Error decoding JSON for user: {user_name}")
    return None


def get_players() -> list[Player]:
    players=[]
    with open('usercache.json','r') as file:
        data=json.load(file)
    for player in data:
        print(f'getting uuid {player["name"]}')
        if online_uuid:=get_uuid(player['name']):
            if online_uuid!=player['uuid']:
                players.append(Player(player['name'],player['uuid'],online_uuid))
    return players


def modify_json(players: list[Player],filename: str) -> None:
    uuid_map={player.name:player.online_uuid for player in players}
    with open(filename,'r+') as file:
        tmp=json.load(file)
        for data in tmp:
            if data['name'] in uuid_map:
                data['uuid']=uuid_map[data['name']]
        file.seek(0)
        file.truncate(0)
        file.write(json.dumps(tmp,indent=4))


def modify_dir(players: list[Player],directory: str,ext: str) -> None:
    os.chdir(Path(directory))
    for player in players:
        old_file=Path(f"{player.uuid}{ext}")
        new_file=Path(f"{player.online_uuid}{ext}")
        if old_file.exists():
            if new_file.exists():
                new_file.unlink()
            old_file.rename(new_file)
    os.chdir(Path('..'))


def main() -> None:
    os.chdir(Path('server'))
    players=get_players()
    for filename in list_file:
        print(f'modifying file {filename}')
        modify_json(players,filename)
    os.chdir(Path(world_name))
    for directory,ext in list_dir:
        print(f'modifying dir {directory}')
        modify_dir(players,directory,ext)
    print('OK')


if __name__=="__main__":
    main()
