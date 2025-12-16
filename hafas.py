import requests, json
from config import Config
from datetime import datetime
from shared import ConnectionError, RequestException


class Stop:
    lid: str
    extid: str
    full_name: str
    display_name: str
    locality: str
    lat: float
    lon: float
    pCls: int
    stop_type: str
    is_main_mast: bool
    is_meta_station: bool = False


class Departure:
    line_nr: str
    line_name: str
    line_type: str
    destination: str
    departure_time: datetime.time


class HafasAPI:

    selected_stop: Stop
    
    endpoint_url: str = "https://vmt.eks-prod-euc1.hafas.cloud/bin/mgaate.exe"#?rnd=1762548971124"


    def __init__(self):
        self._config = Config


    def get_suggestions(self, search: str, amount: int = 7) -> list[Stop]:

        if not search or len(search) < 2:
            return []

        payload = {
            "id": "8e4cnq4q6q8s9gwg",
            "ver": "1.78",
            "lang": "deu",
            "auth": {"type": "AID", "aid": "web-vmt-qdr6c6y8s4cvfmfw"},
            "client": {"id": "VMT", "type": "WEB", "name": "webapp", "l": "vs_vmt", "v": 10010},
            "formatted": False,
            "svcReqL": [{"req": {"input": {"field": "S", "loc": {"type": "S", "dist": 1000, "name": search}, "maxLoc": amount}}, "meth": "LocMatch", "id": "1|1|"}]
        }

        try:
            response = requests.post(self.endpoint_url, json=payload)
            if not response.ok:
                raise RequestException(response.status_code)
        except Exception as e:
            raise ConnectionError(e.args)
        
        data = response.json()
        suggestions = data["svcResL"][0]["res"]["match"]["locL"]

        stops = []
        for suggestion in suggestions:

            stop = Stop()
            stop.lid=suggestion.get("lid", "")
            stop.extid=suggestion.get("extId", "")
            stop.full_name=suggestion.get("name", "")
            stop.locality = self._get_locality(stop.full_name)
            stop.display_name = stop.full_name
            stop.lat=suggestion["crd"].get("x", 0)
            stop.lon=suggestion["crd"].get("y", 0)
            stop.pCls=suggestion.get("pCls", 0)
            stop.stop_type=suggestion.get("type", "")
            stop.is_main_mast=suggestion.get("isMainMast", False)
            stop.is_meta_station=suggestion.get("meta", False)
            
            stops.append(stop)
        return stops
    

    def _get_locality(self, full_stop_name: str):
        return full_stop_name.split(", ")[0] if ", " in full_stop_name else None


    def get_stop(self, search: str) -> Stop:

        if not search or len(search) < 2:
            return None

        return self.get_suggestions(search)[0]


    def set_selected_stop(self, stop: Stop) -> None:
        self.selected_stop = stop


    def get_departures(self,  amount: int = 5) -> list[Departure]:
        
        if not self.selected_stop:
            return []

        payload = {
            "id":"2egwnxwx4q8hhwcs",
            "ver":"1.78",
            "lang":"deu",
            "auth": {"type":"AID", "aid":"web-vmt-qdr6c6y8s4cvfmfw"},
            "client": {"id":"VMT", "type":"WEB", "name":"webapp", "l":"vs_vmt", "v":10010},
            "formatted":False,
            "svcReqL":[{"req":{"jnyFltrL":[{"type":"PROD", "mode":"INC", "value":296}], "stbLoc": {"name": self.selected_stop.full_name, "lid": self.selected_stop.lid, "extId": self.selected_stop.extid, "eteId": f"sq|{self.selected_stop.stop_type}|{self.selected_stop.full_namename}|{self.selected_stop.extid}|{self.selected_stop.lat}|{self.selected_stop.lon}"}, "type":"DEP", "sort":"PT", "maxJny":amount}, "meth":"StationBoard", "id":"1|4|"}]
        }

        response = requests.post(self.endpoint_url, json=payload)
        data = response.json()

        lines = data["svcResL"][0]["res"]["common"]["prodL"]
        journeys = data["svcResL"][0]["res"]["jnyL"]

        departures: list[Departure] = []
        for i in range(amount):
            dep = Departure()

            dep.line_name = lines[i]["name"]
            dep.line_nr = lines[i]["number"]
            dep.line_type = lines[i]["cls"]
            dep.destination = journeys[i]["dirTxt"]
            dep.departure_time = datetime.strptime((journeys[i]["stbStop"]["dTimeS"][:4]), "%H%M").time()

            departures.append(dep)
        
        return departures

        

if __name__ == '__main__':
    hafas = HafasAPI()

    res = hafas.get_suggestions("Bürgel")

    for r in res:
        print(r.full_name)
        print(r.pCls)
        print(r.is_main_mast)
        print(r.is_meta_station)