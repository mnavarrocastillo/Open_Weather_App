import json

from city_maria_navarro import City

from collections import defaultdict

class GIS:
    city_list_filename = 'data\\city.list.json'

    f = open(city_list_filename, encoding='UTF-8')
    cities = json.load(f)
    f.close()

    @classmethod
    def get_countries(cls):
        countries = list()
        for c in cls.cities:
            if c['country'] not in countries and c['country'] != '':
                countries.append(c['country'])
        return countries

    @classmethod
    # TEST Maria: changed to account for multiple chosen countries
    def get_cities_by_country(cls, countries, limit_per_country=50):
        city_list_as_dict = dict()
        city_count_by_country = defaultdict(int)

        for c in cls.cities:
            if c['country'] in countries and city_count_by_country[c['country']] < limit_per_country:
                city = City(c['id'], c['name'], c['state'], c['country'],
                            c['coord']['lon'], c['coord']['lat'])
                city_list_as_dict[city.name] = city
                city_count_by_country[c['country']] += 1
        return city_list_as_dict

    @classmethod
    def get_us_states(cls):
        states = list()
        for c in cls.cities:
            if c['country'] == 'US' and c['state'] not in states and c['state'] != '':
                states.append(c['state'])
        return states

    @classmethod
    # TEST Maria: changed to account for multiple chosen US states
    def get_cities_by_us_state(cls, states, limit_per_state=50):
        city_list_as_dict = dict()
        city_count_by_state = defaultdict(int)
        for c in cls.cities:
            if c['country'] == 'US' and c['state'] in states and city_count_by_state[c['state']] < limit_per_state:
                city = City(c['id'], c['name'], c['state'], c['country'],
                            c['coord']['lon'], c['coord']['lat'])
                city_list_as_dict[city.name] = city
                city_count_by_state[c['state']] += 1
        return city_list_as_dict