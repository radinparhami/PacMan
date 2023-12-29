from pygame import draw, Rect, display, image
from random import choice


class ObjectCore:
    def __init__(self, x: int, y: int, s: int, lw: int, loc: tuple):
        self.x, self.y, self.s, self.lw = x, y, s, lw
        self.cdt, self.loc = (self.x, self.y), loc

    @property
    def get_center(self) -> tuple:
        return self.x + self.s / 2, self.y + self.s / 2

    def get_center_for_shape(self, shape: image) -> tuple:
        center, shape = self.get_center, shape.get_size()
        return center[0] - shape[0] / 2, center[1] - shape[1] / 2

    def inside(self, x, y, s, pos, shape):
        xx, yy = shape.get_size()
        return x <= pos[0] + xx / 2 <= x + s and y <= pos[1] + yy / 2 <= y + s

    def object_model(self, mode: tuple) -> tuple:
        return mode[0] - self.lw + self.lw / 2, mode[1] - self.lw, self.s + mode[1] + self.lw - 1


def get_side(
        screen: display,
        action: str,
        core: ObjectCore,
        color: list | tuple = (255, 255, 255),
):
    action = action.lower()
    if action == "q":
        return draw.rect(
            screen, 'white',
            Rect(core.x, core.y, core.s, core.s)
        )
    x, y, s, lw = core.x, core.y, core.s, core.lw
    if action in ['r', 'l']:
        if action == "r":
            x += s + lw
        x, y_1, y_2 = core.object_model((x, y))
        return draw.line(
            screen, color,
            (x, y_1),
            (x, y_2),
            lw
        )
    elif action in ['t', 'd']:
        if action == "d":
            y += s + lw
        y, x_1, x_2 = core.object_model((y, x))
        return draw.line(
            screen, color,
            (x_1, y),
            (x_2, y),
            lw
        )


def array_map(
        screen: display,
        map: list | tuple,
        def_size: int, space_between: int,
        color: list | tuple
):
    columns = []
    for y_i, y_d in enumerate(map):
        rows = []
        for x_i, x_d in enumerate(y_d):
            if x_d or x_d == '':
                core = ObjectCore(
                    space_between + ((def_size + space_between) * x_i),
                    space_between + ((def_size + space_between) * y_i),
                    def_size, space_between, (y_i, x_i)
                )
                for crd in x_d:
                    get_side(screen, crd, core, color)
                rows.append(core)
        columns.append(rows)
    return columns


class CdtSelector:
    def __init__(
            self, map_org: list | tuple,
            map_obj: array_map,
            except_w: list | None = None,
            exception_w: list | None = None
    ):
        self.map_org, self.map_obj, self.except_w, self.exception_w = map_org, map_obj, except_w or [], exception_w or []

    def set_except(self, result: list):
        return [obj for obj in result + self.exception_w if
                (obj if isinstance(obj, tuple) else obj.cdt) not in self.except_w]

    def have(self, root, string='trld', any_ok=False):
        wc = [s in root for s in string]
        return any(wc) if any_ok else all(wc)

    def array_filter(
            self, filter_w
    ):
        result = [x_b for y_o, y_b in zip(self.map_org, self.map_obj) for x_o, x_b in zip(y_o, y_b) if
                  filter_w(x_o, x_b) or x_b.cdt in self.exception_w]
        self.exception_w.clear()
        return self.set_except(result)

    def get_intersections(self, only_cdt=False):
        intersections = []
        for y_i, y_d in enumerate(self.map_org):
            for x_i, x_d in enumerate(y_d):
                if not self.have(x_d, any_ok=True) and y_i != len(self.map_org) - 1 and x_i != len(y_d) - 1:
                    if self.have(y_d[x_i - 1], 'td') and self.have(y_d[x_i + 1], 'td'):
                        if self.have(self.map_org[y_i + 1][x_i], 'rl') and self.have(self.map_org[y_i - 1][x_i], 'rl'):
                            intersections.append(self.map_obj[y_i][x_i])
        return self.set_except(
            [obj for obj in ([obj.cdt for obj in intersections] if only_cdt else intersections)]
        )

    def is_possible(self, loc, direction, available_points):
        y, x = loc
        ok = (
            y != len(self.map_obj) - 1 and direction == 'd' and self.map_obj[y + 1][x],
            y != 0 and direction == 't' and self.map_obj[y - 1][x],
            x != len(self.map_obj[y]) - 1 and direction == 'r' and self.map_obj[y][x + 1],
            x != 0 and direction == 'l' and self.map_obj[y][x - 1],
        )
        next_ok = any(ok) and [i for i in ok if i and i.cdt in available_points]
        return next_ok and any(next_ok) and next_ok[0]

    def get_random_path(self, last_pos_obj: ObjectCore, available_points: list, inters: list):
        path, rp, anti_crash = [last_pos_obj], choice('rtld'), []
        reflex = {'t': 'd', 'd': 't', 'r': 'l', 'l': 'r'}
        while len(path) != 10 and len(anti_crash) != 3:
            if not anti_crash or len(path) in anti_crash:
                anti_crash.append(len(path))
            else:
                anti_crash.clear()
            if path and path[-1].cdt in inters:
                rp = choice('td') if rp in 'rl' else choice('rl')
            point = self.is_possible(last_pos_obj.loc, rp, available_points)
            if point:
                path.append(point)
                last_pos_obj = point
            else:
                rp = reflex[rp]
        return self.set_except(path)


def get_centers(obj_one, array_two, shape):
    return [obj.get_center_for_shape(shape) for obj in obj_one if obj.cdt in array_two]


def get_space(cdt_one, cdt_two, shape, scale=3):
    cdt_two = cdt_two.get_center_for_shape(shape)
    x, y = list(map(int, cdt_one))
    xx, yy = list(map(int, cdt_two))
    if y == yy:
        step = +scale if xx > x else -scale
        return [(x, y) for x in range(x, xx + step, step)][:-1] + [cdt_two]
    step = +scale if yy > y else -scale
    return [(x, y) for y in range(y, yy + step, step)][:-1] + [cdt_two]




def mouse_inside(cdt_one, cdt_two, cdt_tree):
    return all([x <= z <= y for x, y, z in zip(cdt_one, cdt_two, cdt_tree)])
