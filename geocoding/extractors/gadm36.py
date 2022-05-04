from typing import Any, Dict, Generic, Iterator, TypeVar

from abc import ABC, abstractmethod
from pathlib import Path

import fiona
from attr import define
from geojson import Polygon

from geocoding.convertors.geojson import to_polygons

GADM_PATH = "/Users/a-garikhanov/Documents/gadm36_levels_shp"
LAYER_NAME = "gadm36_0"
RESOLUTION = 7


class GADMBaseModel(ABC):
    @classmethod
    @abstractmethod
    def from_shapefile_object(cls, obj: Dict[str, Any]) -> "GADMBaseModel":
        pass


@define
class GADMCountry(GADMBaseModel):
    """
    Information about country from GADM.
    (https://gadm.org/metadata.html)
    """

    id: int
    "Alternative unique identifier"

    name: str
    "Official name in latin script"

    code: str
    "Preferred unique ID, starts with the ISO 3166-1 alpha-3 country code"

    geometry: list[Polygon]
    "List of polygons representing country boundaries"

    @classmethod
    def from_shapefile_object(cls, obj: Dict[str, Any]) -> "GADMCountry":
        return cls(
            id=int(obj["id"]),
            name=obj["properties"]["NAME_0"],
            code=obj["properties"]["GID_0"],
            geometry=to_polygons(obj["geometry"]),
        )


@define
class GADMCountrySubdivision(GADMBaseModel):
    """
    Information about country subdivision (administrative unit) from GADM.
    (https://gadm.org/metadata.html)
    """

    id: int
    "Alternative unique identifier"

    name: str
    "Official name in latin script"

    code: str
    "Preferred unique ID, starts with the ISO 3166-1 alpha-3 country code"

    geometry: list[Polygon]
    "List of polygons representing subdivision boundaries"

    other_names: list[str]
    "Alternative names in usage for the place"

    localized_names: list[str]
    "Official names in a non-latin script"

    administrative_type: str
    "Administrative type in English"

    localized_administrative_type: str
    "Administrative type in local language"

    country_code: str
    "Preferred unique ID of the country"

    country_name: str
    "Official country name in latin script"

    @classmethod
    def from_shapefile_object(cls, obj: Dict[str, Any]) -> "GADMCountrySubdivision":
        return GADMCountrySubdivision(
            id=int(obj["id"]),
            name=obj["properties"]["NAME_1"],
            code=obj["properties"]["GID_1"],
            geometry=to_polygons(obj["geometry"]),
            other_names=(obj["properties"]["VARNAME_1"] or "").split("|"),
            localized_names=(obj["properties"]["NL_NAME_1"] or "").split("|"),
            administrative_type=obj["properties"]["ENGTYPE_1"],
            localized_administrative_type=obj["properties"]["TYPE_1"],
            country_code=obj["GID_0"],
            country_name=obj["NAME_0"],
        )


GADMModelType = TypeVar("GADMModelType", bound=GADMBaseModel)


class GADMBaseExtractor(Generic[GADMModelType]):
    """
    Extracts info and geojson from GADM dataset.
    """

    layer_name: str
    model_class: type[GADMModelType]

    def __init__(self, path: Path) -> None:
        self.path = path

    # @abstractmethod
    # @property
    # def layer_name(self) -> str:
    #     """Name of the layer from GADM shapefile."""
    #
    # @abstractmethod
    # @property
    # def model_class(self) -> type[GADMModelType]:
    #     """GADM Model specific to objects from the layer."""

    def read_shapefile(self, path: Path, layer_name: str) -> Iterator[GADMModelType]:
        with fiona.open(path, layer=layer_name) as src:
            for obj in src:
                yield self.model_class.from_shapefile_object(obj)

    def __iter__(self) -> Iterator[GADMModelType]:
        return self.read_shapefile(self.path, self.layer_name)


class CountriesExtractor(GADMBaseExtractor[GADMCountry]):
    """
    Extracts info and geojson of all countries in the world from GADM dataset.
    """

    layer_name: str = "gadm36_0"
    model_class = GADMCountry
