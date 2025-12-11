import requests, json
from config import Config


class HafasAPI:

    def __init__(self):
        self._config = Config

    def get_suggestions(self, search: str):
        # HAFAS API endpoint for VMT (Verkehrsverbund Mittelthüringen)
        url = "https://vmt.eks-prod-euc1.hafas.cloud/bin/mgate.exe?rnd=1762548971124"

        payload = {
            "id": "8e4cnq4q6q8s9gwg",
            "ver": "1.78",
            "lang": "deu",
            "auth": {"type": "AID", "aid": "web-vmt-qdr6c6y8s4cvfmfw"},
            "client": {"id": "VMT", "type": "WEB", "name": "webapp", "l": "vs_vmt", "v": 10010},
            "formatted": False,
            "svcReqL": [{"req": {"input": {"field": "S", "loc": {"type": "S", "dist": 1000, "name": search}, "maxLoc": 7}}, "meth": "LocMatch", "id": "1|1|"}]
        }

        response = requests.post(url, json=payload)
        data = response.json()
        suggestions = data["svcResL"][0]["res"]["match"]["locL"]
        stops = []
        for suggestion in suggestions:
            stop = Stop()
            stop.lid=suggestion["lid"],
            stop.extid=suggestion.get("extId", ""),
            stop.name=suggestion["name"],
            stop.lat=suggestion["crd"]["x"],
            stop.lon=suggestion["crd"]["y"],
            stop.pCls=suggestion.get("pCls", 0),
            stop.is_main_mast=suggestion.get("isMainMast", False),
            stop.is_meta_station=suggestion.get("isMetaStation", False)
            
            stops.append(stop)
        return stops

    def get_stop(self, search: str):
        return self.get_suggestions(search)[0]

class Stop:
    lid: str
    extid: str
    name: str
    lat: float
    lon: float
    pCls: int
    is_main_mast: bool
    is_meta_station: bool = False

if __name__ == '__main__':
    hafas = HafasAPI()
    pass
