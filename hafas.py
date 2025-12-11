import requests, json
from config import Config


class Stop:
    lid: str
    extid: str
    name: str
    lat: float
    lon: float
    pCls: int
    is_main_mast: bool
    is_meta_station: bool = False


class HafasAPI:

    selected_stop: Stop

    def __init__(self):
        self._config = Config

    def get_suggestions(self, search: str) -> list[Stop]:

        if not search or len(search) < 2:
            return []
        # HAFAS API endpoint for VMT (Verkehrsverbund Mittelthüringen)
        url = "https://vmt.eks-prod-euc1.hafas.cloud/bin/mgate.exe"#?rnd=1762548971124"

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
            stop.lid=suggestion.get("lid", "")
            stop.extid=suggestion.get("extId", "")
            stop.name=suggestion.get("name", "")
            stop.lat=suggestion["crd"].get("x", 0)
            stop.lon=suggestion["crd"].get("y", 0)
            stop.pCls=suggestion.get("pCls", 0)
            stop.is_main_mast=suggestion.get("isMainMast", False)
            stop.is_meta_station=suggestion.get("meta", False)
            
            stops.append(stop)
        return stops

    def get_stop(self, search: str) -> Stop:
        if not search or len(search) < 2:
            return None

        return self.get_suggestions(search)[0]


if __name__ == '__main__':
    hafas = HafasAPI()
    res = hafas.get_stop("Herman")
    print(f"Found stop: {res.name} (LID: {res.lid})")
