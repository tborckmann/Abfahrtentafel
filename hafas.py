import requests, json
from config import Config
from datetime import datetime


class Stop:
    lid: str
    extid: str
    name: str
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
    # HAFAS VMT endpoint URL
    endpoint_url: str = "https://vmt.eks-prod-euc1.hafas.cloud/bin/mgate.exe"#?rnd=1762548971124"


    def __init__(self):
        self._config = Config


    def get_suggestions(self, search: str) -> list[Stop]:

        if not search or len(search) < 2:
            return []

        payload = {
            "id": "8e4cnq4q6q8s9gwg",
            "ver": "1.78",
            "lang": "deu",
            "auth": {"type": "AID", "aid": "web-vmt-qdr6c6y8s4cvfmfw"},
            "client": {"id": "VMT", "type": "WEB", "name": "webapp", "l": "vs_vmt", "v": 10010},
            "formatted": False,
            "svcReqL": [{"req": {"input": {"field": "S", "loc": {"type": "S", "dist": 1000, "name": search}, "maxLoc": 7}}, "meth": "LocMatch", "id": "1|1|"}]
        }

        response = requests.post(self.endpoint_url, json=payload)
        data = response.json()
        suggestions = data["svcResL"][0]["res"]["match"]["locL"]

        stops = []
        for suggestion in suggestions:

            stop = Stop()
            stop.lid=suggestion.get("lid", "")
            stop.extid=suggestion.get("extId", "")
            stop.name=suggestion.get("name", "")
            stop.lat=suggestion["crd"].get("x", 0)
            stop.lon=suggestion["crd"].get("y", 0)
            stop.pCls=suggestion.get("pCls", 0)
            stop.stop_type=suggestion.get("type", "")
            stop.is_main_mast=suggestion.get("isMainMast", False)
            stop.is_meta_station=suggestion.get("meta", False)
            
            stops.append(stop)
        return stops


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
            "auth": {
            	"type":"AID",
            	"aid":"web-vmt-qdr6c6y8s4cvfmfw"},

            "client": {
            	"id":"VMT",
            	"type":"WEB",
            	"name":"webapp",
            	"l":"vs_vmt",
            	"v":10010},

            "formatted":False,
            "svcReqL":[{
            	"req":{
            		"jnyFltrL":[{
            			"type":"PROD",
            			"mode":"INC",
            			"value":296}],
            		"stbLoc": {
            			"name": self.selected_stop.name,
            			"lid": self.selected_stop.lid,
            			"extId": self.selected_stop.extid,
            			"eteId": f"sq|{self.selected_stop.stop_type}|{self.selected_stop.name}|{self.selected_stop.extid}|{self.selected_stop.lat}|{self.selected_stop.lon}",   # bsp: "sq|S|Jena, Zeiss-Werk|153045|11570052|50915639"
            			},
            		"type":"DEP",
            		"sort":"PT",
            		"maxJny":amount # Anzahl der Abfahrten
            		},
            	"meth":"StationBoard",
            	"id":"1|4|"
            }]
        }

        response = requests.post(self.endpoint_url, json=payload)
        data = response.json()

        #with open("./Responses/Abfahrten Response.json", "w", encoding="utf-8") as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)

        lines = data["svcResL"][0]["res"]["common"]["prodL"]
        journeys = data["svcResL"][0]["res"]["jnyL"]

        departures: list[Departure] = []
        for i in range(amount):
            dep = Departure()

            dep.line_name = lines[i]["name"]
            dep.line_nr = lines[i]["number"]
            dep.line_type = lines[i]["cls"]
            dep.destination = journeys[i]["dirTxt"]
            #print(journeys[i]["stbStop"]["dTimeS"][:4])
            dep.departure_time = datetime.strptime((journeys[i]["stbStop"]["dTimeS"][:4]), "%H%M").time()

            departures.append(dep)
        
        return departures

        

if __name__ == '__main__':
    hafas = HafasAPI()
    res = hafas.get_stop("Jena, Stadtzentrum Löbdergraben")
    hafas.set_selected_stop(res)
    deps = hafas.get_departures(5)
    for dep in deps:
        print(f"Linie {dep.line_nr} nach {dep.destination} um {dep.departure_time.strftime('%H:%M')}")