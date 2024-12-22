"""
Build the cities database
"""
import json


class CapitalesBuiler:

    def __init__(self,
                 result_path: str = "./capitales.json",
                 cities_dataset_path: str = "./datasets/cities5000.csv",
                 countries_dataset_path: str = "./datasets/countries-codes.csv"):
        self.result_path = result_path
        self.cities_dataset_path = cities_dataset_path
        self.countries_dataset_path = countries_dataset_path
        self.cities = []
        self.countries_name = {}
        self.result = []

        self._open_cities_dataset()
        self._open_countries_dataset()

    def _open_cities_dataset(self):
        with open(self.cities_dataset_path, "r", encoding="utf-8") as file:
            for line in file:
                city = line.split(";")
                coords = city[-1].split(", ")
                pre_append = city[:-1] + coords
                self.cities.append(pre_append)

    def _open_countries_dataset(self):
        with open(self.countries_dataset_path, "r", encoding="utf-8") as file:
            for line in file:
                country = line.split(";")
                self.countries_name[country[1]] = country[7]

    def filter_cities(self, min_pop: int = 0, is_capital: bool = True):
        for city in self.cities:
            if ((is_capital and city[5] == "PPLC") or (not is_capital)) and int(city[12]) >= min_pop:
                try:
                    self.result.append({
                        "capital_name": city[1],
                        "country_name": self.countries_name[city[6]],
                        "country_code": city[6],
                        "capital_population": int(city[12]),
                        "capital_lat": float(city[-2]),
                        "capital_lon": float(city[-1]),
                        "capital_id": int(city[0])
                    })
                except KeyError:
                    print("code not found:", city[6], city[1])

    def write_json(self):
        with open(self.result_path, "w", encoding="utf-8") as file:
            json.dump(self.result, file)


class CitiesBuiler:

    def __init__(self,
                 result_path: str = "./cities.json",
                 cities_dataset_path: str = "./datasets/cities5000.csv",
                 countries_dataset_path: str = "./datasets/countries-codes.csv"):
        self.result_path = result_path
        self.cities_dataset_path = cities_dataset_path
        self.countries_dataset_path = countries_dataset_path
        self.cities = []
        self.countries_name = {}
        self.result = []

        self._open_cities_dataset()
        self._open_countries_dataset()

    def _open_cities_dataset(self):
        with open(self.cities_dataset_path, "r", encoding="utf-8") as file:
            for line in file:
                city = line.split(";")
                coords = city[-1].split(", ")
                pre_append = city[:-1] + coords
                self.cities.append(pre_append)

    def _open_countries_dataset(self):
        with open(self.countries_dataset_path, "r", encoding="utf-8") as file:
            for line in file:
                country = line.split(";")
                self.countries_name[country[1]] = country[7]

    def filter_cities(self, min_pop: int = 5000, is_capital: bool = False):
        for city in self.cities[1:]:
            if ((is_capital and city[5] == "PPLC") or (not is_capital)) and int(city[12]) >= min_pop:
                try:
                    self.result.append({
                        "city_name": city[1],
                        "country_name": self.countries_name[city[6]],
                        "country_code": city[6],
                        "city_population": int(city[12]),
                        "city_lat": float(city[-2]),
                        "city_lon": float(city[-1]),
                        "city_id": int(city[0])
                    })
                except KeyError:
                    print("code not found:", city[6], city[1])
                except ValueError:
                    print("id bugé")

    def write_json(self):
        with open(self.result_path, "w", encoding="utf-8") as file:
            json.dump(self.result, file)


builder = CitiesBuiler()
builder.filter_cities()
builder.write_json()
print(builder.result[10000])