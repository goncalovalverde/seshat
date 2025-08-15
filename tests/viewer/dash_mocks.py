import pandas as pd

class DummyTM:
    name = 'Dummy Project'
    pbi_types = ['Total', 'Bug', 'Feature']
    workflow = ['To Do', 'In Progress', 'Done']
    # Use datetime64[ns] directly, which is pandas default
    cycle_data = pd.DataFrame({
        'To Do': [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-02')],
        'In Progress': [pd.Timestamp('2024-01-03'), pd.Timestamp('2024-01-04')],
        'Done': [pd.Timestamp('2024-01-05'), pd.Timestamp('2024-01-06')]
    })
    has_story_points = False
    def draw_throughput(self, *a, **k): return {}
    def draw_defect_percentage(self, *a, **k): return {}
    def draw_lead_time(self, *a, **k): return {}
    def draw_net_flow(self, *a, **k): return {}
    def draw_lead_time_hist(self, *a, **k): return {}
    def draw_all_cycle_time_hist(self, *a, **k): return [{}]
    def draw_wip(self, *a, **k): return {}
    def draw_start_stop(self, *a, **k): return {}
    def draw_velocity(self, *a, **k): return {}
    def draw_story_points(self, *a, **k): return {}
    def draw_cfd(self, *a, **k): return {}
