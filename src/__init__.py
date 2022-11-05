from arcade.resources import add_resource_handle, resolve_resource_path
from pyglet.image import load

from src.engine_window import EngineWindow


def main():
    add_resource_handle("assets", "resources")
    add_resource_handle("data", "data")
    engine = EngineWindow()
    engine.set_icon(load(resolve_resource_path(":assets:/textures/dragon-bakery-splash.png")))
    engine.run()
