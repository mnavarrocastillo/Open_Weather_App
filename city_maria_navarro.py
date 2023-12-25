class City:

    def __init__(self, id, name, state, country, longitude, latitude):
        self.id = id
        self.name = name
        self.state = state
        self.country = country
        self.longitude = float(longitude)
        self.latitude = float(latitude)

    def __str__(self):
        return f'{self.id}:{self.name}:{self.state}:{self.country}:{self.longitude}:{self.latitude}'
