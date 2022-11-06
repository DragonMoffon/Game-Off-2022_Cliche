from arcade.resources import add_resource_handle, resolve_resource_path
from pyglet.image import load

from src.engine_window import EngineWindow
from src.input import Input


def main():
    add_resource_handle("assets", "resources")
    add_resource_handle("data", "data")
    # TODO: Pick between default and saved button bindings.
    Input.process_buttons(resolve_resource_path(":data:/buttons_axis_defaults.json"))
    engine = EngineWindow()
    engine.set_icon(load(resolve_resource_path(":assets:/textures/dragon-bakery-splash.png")))
    engine.run()
