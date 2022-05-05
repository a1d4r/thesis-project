from geojson import Polygon

from geocoding.processing.h3 import fill_polygons_by_hexagons


def test_polygons_to_hexagons():
    polygon1 = Polygon(
        [
            [
                (-122.4089866999972145, 37.813318999983238),
                (-122.3544736999993603, 37.7198061999978478),
                (-122.4798767000009008, 37.8151571999998453),
                (-122.4089866999972145, 37.813318999983238),
            ]
        ]
    )
    polygon2 = Polygon(
        [
            [
                (-123.4089866999972145, 38.813318999983238),
                (-123.3544736999993603, 38.7198061999978478),
                (-123.4798767000009008, 38.8151571999998453),
                (-123.4089866999972145, 38.813318999983238),
            ]
        ]
    )
    hexagons = fill_polygons_by_hexagons([polygon1, polygon2], resolution=7)
    assert set(hexagons) == {
        608692970585063423,
        608692970719281151,
        608692970752835583,
        608692970769612799,
        608692970819944447,
        608692971927240703,
        608692972027903999,
        608693007629156351,
        608693007662710783,
        608693007729819647,
        608693008434462719,
        608693008484794367,
    }
