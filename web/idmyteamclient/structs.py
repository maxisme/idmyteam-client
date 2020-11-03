from idmyteam.structs import Struct, FaceCoordinates

from idmyteamclient.models import Member


class ClassifiedImage(Struct):
    def __init__(
        self,
        id: str,
        img: str,
        is_classified: bool,
        member: Member,
        coordinates: FaceCoordinates,
    ):
        self.id = id
        self.img = img
        self.is_classified = is_classified
        self.member = member
        self.coordinates = coordinates
