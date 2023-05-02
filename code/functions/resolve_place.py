def read_place() -> dict:
    places = {}
    with open("functions/places.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            pl = line.split(",")
            places[pl[0]] = pl[1].strip("\n")
            
    return places


def resolve_place(place: str) -> str:
    places = read_place()
    return places.get(place, "no place")
