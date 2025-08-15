
import viewer.dash
from tests.viewer.dash_mocks import DummyTM

import types
import pytest

def make_dash():
    config = {'debug': False}
    projects = [DummyTM()]
    return viewer.dash.Dash(projects, config)

def test_dash_class_exists():
    assert hasattr(viewer.dash, 'Dash')

def test_show_main_dash():
    dash = make_dash()
    layout = dash.show_main_dash()
    assert layout is not None

def test_show_hist_dash():
    dash = make_dash()
    layout = dash.show_hist_dash()
    assert layout is not None

def test_show_raw_data():
    dash = make_dash()
    layout = dash.show_raw_data()
    assert layout is not None

def test_show_wip_dash():
    dash = make_dash()
    layout = dash.show_wip_dash()
    assert layout is not None

def test_show_throughput_dash():
    dash = make_dash()
    layout = dash.show_throughput_dash()
    assert layout is not None

def test_show_cfd():
    dash = make_dash()
    layout = dash.show_cfd()
    assert layout is not None

def test_show_pivottable():
    dash = make_dash()
    layout = dash.show_pivottable()
    assert layout is not None

def test_menu_pbi_types():
    dash = make_dash()
    menu = dash.menu_pbi_types('main', 0)
    assert menu is not None

def test_navbar():
    dash = make_dash()
    nav = dash.navbar()
    assert nav is not None
