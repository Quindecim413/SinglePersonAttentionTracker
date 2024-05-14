from enum import Enum
from pathlib import Path
import socket
from pydantic import TypeAdapter
import requests
from pydantic.dataclasses import dataclass

from common.dtos.utils import PersonId

class ConnectionEventsNames(Enum):
    connect='/connect'
    disconnect='/disconnect'
    active_project_download='/active_project_download'
    generated_head_data='/generated_head_data'
    generated_scene_obj_aggregated_hits='/generated_aggregated_hits'
    generated_cast_result='/generated_cast_result'
    request_state='/request_state'
    recieved_project_changed='/recieved_project_changed'
    recieved_current_person_id='/recieved_current_person_id'
    recieved_others_head_data='/recieved_others_head_data'
    recieved_others_aggregated_hits='/recieved_others_aggregated_hits'
    recieved_others_cast_result='/recieved_others_cast_result'
    recieved_state='/recieved_state'



def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to a free port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.
    
def get_ip():
    # This function is designed to fetch the local IP address of the server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def download_file(url:str, save_path:Path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    # return save_path
                
@dataclass(frozen=True)
class PersonIdData:
    person_id:PersonId|None

PersonIdDataAdapter = TypeAdapter(PersonIdData)