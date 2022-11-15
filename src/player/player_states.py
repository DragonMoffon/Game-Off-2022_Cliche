from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from src.player.player import PlayerCharacter

from arcade import Sprite, load_texture

from src.player.player_data import PlayerData

from src.input import Input, Button
from src.clock import Clock


class PlayerState:

    def __init__(self, _switch: "PlayerStateSwitch", _source: "PlayerCharacter", _name: str):
        self._switch: "PlayerStateSwitch" = _switch
        self._data: PlayerData = _source.p_data
        self._source: "PlayerCharacter" = _source
        self._hitbox = None
        self._name = _name

    def __repr__(self):
        return f"State({self._name})"

    def __str__(self):
        return self._name

    def p_into_state(self):
        raise NotImplementedError()

    def p_out_of_state(self):
        raise NotImplementedError()

    def p_update(self):
        raise NotImplementedError()

    def p_find_state(self):
        raise NotImplementedError()

    def p_collision_bottom(self, _collision: Sprite):
        self._data.vel_y = max(0.0, self._data.vel_y)

    def p_collision_top(self, _collision: Sprite):
        self._data.vel_y = min(0.0, self._data.vel_y)

    def p_collision_left(self, _collision: Sprite):
        self._data.vel_x = max(0.0, self._data.vel_x)

    def p_collision_right(self, _collision: Sprite):
        self._data.vel_x = min(0.0, self._data.vel_x)

    def p_jump(self, _button: Button):
        pass

    def p_crouch(self, _button: Button):
        pass

    def p_horizontal(self, _value: float):
        pass


class StandState(PlayerState):

    def __init__(self, _switch, _source):
        super().__init__(_switch, _source, "stand")

    def p_into_state(self):
        self._data.vel_x = 0.0
        self._data.vel_y = 0.0

        # TODO: Add Animation Control

    def p_out_of_state(self):
        pass

    def p_update(self):
        _acc_y = 0.0
        if not self._data.on_ground:
            _acc_y = -self._data.c_base_gravity * Clock.delta_time

        self._data.acc_y = _acc_y
        self._data.vel_y += _acc_y

    def p_find_state(self):
        if Clock.frame_length(self._data.forgiven_jump_frames) <= self._data.c_jump_buffer_frames:
            self._data.vel_y = self._data.c_base_jump_speed
            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")
        elif self._data.vel_y < 0.0 or not self._data.on_ground:
            self._data.forgiven_edge_frames = Clock.frame
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("fall")

    def p_crouch(self, _button: Button):
        if (self._data.direction < 0.0 and
                self._source.p_hitbox.check_ledge_horizontal_left(self._source.p_chamber.sprite_lists['all_ground'])):
            self._data.vel_x = 0.0
            self._data.vel_y = 0.0

            _target = self._source.p_hitbox.bottom_collisions[0]
            self._data.top = _target.top
            self._data.left = _target.left

            self._data.direction = 1.0
            self._data.at_ledge = True
            self._switch.set_state("ledge_hold")
        elif (self._data.direction > 0.0 and
                self._source.p_hitbox.check_ledge_horizontal_right(self._source.p_chamber.sprite_lists['all_ground'])):
            self._data.vel_x = 0.0
            self._data.vel_y = 0.0

            _target = self._source.p_hitbox.bottom_collisions[0]
            self._data.top = _target.top
            self._data.left = _target.right

            self._data.direction = -1.0
            self._data.at_ledge = True
            self._switch.set_state("ledge_hold")



    def p_jump(self, _button: Button):
        self._data.vel_y = self._data.c_base_jump_speed * _button.pressed
        self._data.forgiven_edge_frames = 0
        self._data.forgiven_jump_frames = 0
        self._switch.set_state("jump")

    def p_horizontal(self, _value: float):
        if _value:
            self._data.direction = _value / abs(_value)
            self._switch.set_state("run")


class RunState(PlayerState):

    def __init__(self, _switch, _source):
        super().__init__(_switch, _source, "run")

    def p_into_state(self):
        pass

    def p_out_of_state(self):
        pass

    def p_update(self):
        # find horizontal acceleration
        _target_velocity = self._data.c_max_vel * Input.get_axis("HORIZONTAL")

        _acc_x = self._data.c_max_dec
        if _target_velocity:
            if self._data.vel_x / _target_velocity < 0:
                _acc_x = self._data.c_max_turn
            else:
                _acc_x = self._data.c_max_acc
                if abs(_target_velocity) < abs(self._data.vel_x):
                    _target_velocity = self._data.vel_x

        _diff = _target_velocity - self._data.vel_x
        _acc_x = min(abs(_diff), _acc_x * Clock.delta_time) * (_diff / abs(_diff)) if _diff else 0

        # find vertical acceleration
        _acc_y = 0.0
        if not self._data.on_ground:
            _acc_y = -self._data.c_base_gravity * Clock.delta_time

        self._data.acc = _acc_x, _acc_y
        self._data.vel_x += _acc_x
        self._data.vel_y += _acc_y

        if self._data.vel_x:
            self._data.direction = self._data.vel_x / abs(self._data.vel_x)

    def p_find_state(self):
        _next_state = self._name
        if Clock.frame_length(self._data.forgiven_jump_frames) <= self._data.c_jump_buffer_frames:
            self._data.vel_y = self._data.c_base_jump_speed
            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")
        elif self._data.vel_y < 0.0 or not self._data.on_ground:
            self._data.forgiven_edge_frames = Clock.frame
            return self._switch.set_state("fall")
        elif self._data.vel_x == 0.0:
            return self._switch.set_state("stand")

    def p_jump(self, _button: Button):
        self._data.vel_y = self._data.c_base_jump_speed * _button.pressed
        self._data.forgiven_edge_frames = 0
        self._data.forgiven_jump_frames = 0
        self._switch.set_state("jump")

    def p_horizontal(self, _value: float):
        if _value:
            self._data.direction = _value / abs(_value)


class JumpState(PlayerState):

    def __init__(self, _switch, _source):
        super().__init__(_switch, _source, "jump")

    def p_into_state(self):
        pass

    def p_out_of_state(self):
        pass

    def p_update(self):
        # find horizontal acceleration
        _target_velocity = self._data.c_max_vel * Input.get_axis("HORIZONTAL")

        _acc_x = self._data.c_max_dec_air
        if _target_velocity:
            if self._data.vel_x / _target_velocity < 0:
                _acc_x = self._data.c_max_turn_air
            else:
                _acc_x = self._data.c_max_acc_air
                if abs(_target_velocity) < abs(self._data.vel_x):
                    _target_velocity = self._data.vel_x

        _diff = _target_velocity - self._data.vel_x
        _acc_x = min(abs(_diff), _acc_x * Clock.delta_time) * (_diff / abs(_diff)) if _diff else 0

        # find vertical acceleration
        _acc_y = -self._data.c_base_gravity * Clock.delta_time
        if Input.get_button("JUMP"):
            _acc_y = -self._data.c_jump_gravity * Clock.delta_time

        self._data.acc = _acc_x, _acc_y
        self._data.vel_x += _acc_x
        self._data.vel_y += _acc_y

        if self._data.vel_x:
            self._data.direction = self._data.vel_x / abs(self._data.vel_x)

    def p_find_state(self):
        if self._data.vel_y < 0.0:
            return self._switch.set_state("fall")

    def p_collision_bottom(self, _collision: Sprite):
        self._data.vel_y = max(0.0, self._data.vel_y)
        if self._data.vel_x:
            self._switch.set_state("run")
        else:
            self._switch.set_state("stand")

    def p_collision_left(self, _collision: Sprite):
        self._data.at_ledge = False
        if (Clock.frame_length(Input.get_button("DASH").press_frame) <= self._data.c_dash_buffer_frames and
                self._data.vel_y):
            _acc_y = (abs(self._data.vel_x) * 0.75) * (self._data.vel_y / abs(self._data.vel_y))
            self._data.vel_y += _acc_y

        elif (self._data.direction < 0 and Input.get_axis("HORIZONTAL").value < 0.0 and
                self._data.y < _collision.top and self._data.vel_y < self._data.c_max_vel and
                Clock.frame_length(self._data.blocked_ledge_frames) > self._data.c_ledge_buffer_frames and
                self._source.p_hitbox.check_ledge_vertical_left(self._source.p_chamber.sprite_lists["ground"])):

            self._data.vel_y = 0.0
            self._data.vel_x = 0.0
            self._data.top = _collision.top
            self._data.at_ledge = True

            return self._switch.set_state("ledge_hold")

        self._data.vel_x = max(0.0, self._data.vel_x)
        self._switch.set_state("wall_slide")

    def p_collision_right(self, _collision: Sprite):
        self._data.at_ledge = False
        if (Clock.frame_length(Input.get_button("DASH").press_frame) <= self._data.c_dash_buffer_frames * 2 and
                self._data.vel_y):
            _acc_y = (abs(self._data.vel_x) * 0.75) * (self._data.vel_y / abs(self._data.vel_y))
            self._data.vel_y += _acc_y

        elif (self._data.direction > 0 and Input.get_axis("HORIZONTAL").value > 0.0 and
                self._data.y < _collision.top and self._data.vel_y < self._data.c_max_vel and
                Clock.frame_length(self._data.blocked_ledge_frames) > self._data.c_ledge_buffer_frames and
                self._source.p_hitbox.check_ledge_vertical_right(self._source.p_chamber.sprite_lists["ground"])):

            self._data.vel_y = 0.0
            self._data.vel_x = 0.0
            self._data.top = _collision.top
            self._data.at_ledge = True

            return self._switch.set_state("ledge_hold")

        self._data.vel_x = max(0.0, self._data.vel_x)
        self._switch.set_state("wall_slide")

    def p_collision_top(self, _collision: Sprite):
        if self._data.vel_x:
            if Clock.frame_length(Input.get_button("DASH").press_frame) <= self._data.c_dash_buffer_frames:
                _acc_x = (abs(self._data.vel_y) / 4.0) * (self._data.vel_x / abs(self._data.vel_x))
                self._data.vel_x += _acc_x

        self._data.vel_y = min(0.0, self._data.vel_y)
        return self._switch.set_state("fall")


class FallState(PlayerState):

    def __init__(self, _switch, _source):
        super().__init__(_switch, _source, "fall")

    def p_into_state(self):
        pass

    def p_out_of_state(self):
        pass

    def p_update(self):
        # find horizontal acceleration
        _target_velocity = self._data.c_max_vel * Input.get_axis("HORIZONTAL")

        _acc_x = self._data.c_max_dec_air
        if _target_velocity:
            if self._data.vel_x / _target_velocity < 0:
                _acc_x = self._data.c_max_turn_air
            else:
                _acc_x = self._data.c_max_acc_air
                if abs(_target_velocity) < abs(self._data.vel_x):
                    _target_velocity = self._data.vel_x

        _diff = _target_velocity - self._data.vel_x
        _acc_x = min(abs(_diff), _acc_x * Clock.delta_time) * (_diff / abs(_diff)) if _diff else 0

        # find vertical acceleration
        _acc_y = -self._data.c_base_gravity * Clock.delta_time

        self._data.acc = _acc_x, _acc_y
        self._data.vel_x += _acc_x
        self._data.vel_y += _acc_y

        if self._data.vel_x:
            self._data.direction = self._data.vel_x / abs(self._data.vel_x)

    def p_find_state(self):
        pass

    def p_jump(self, _button: Button):
        if Clock.frame_length(self._data.forgiven_edge_frames) <= self._data.c_edge_buffer_frames:
            self._data.vel_y = self._data.c_base_jump_speed * _button.pressed
            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")

        self._data.forgiven_jump_frames = Clock.frame

    def p_collision_bottom(self, _collision: Sprite):
        if self._data.vel_x:
            if Clock.frame_length(Input.get_button("DASH").press_frame) <= self._data.c_dash_buffer_frames:
                _acc_x = (abs(self._data.vel_y) / 2.0) * (self._data.vel_x / abs(self._data.vel_x))
                self._data.vel_x += _acc_x

            self._switch.set_state("run")
        else:
            self._switch.set_state("stand")

        self._data.vel_y = max(0.0, self._data.vel_y)

    def p_collision_left(self, _collision: Sprite):
        self._data.at_ledge = False
        if (Clock.frame_length(Input.get_button("DASH").press_frame) <= self._data.c_dash_buffer_frames and
                self._data.vel_y):
            _acc_y = (abs(self._data.vel_x) / 2.0) * (self._data.vel_y / abs(self._data.vel_y))
            self._data.vel_y += _acc_y

        elif (self._data.direction < 0 and Input.get_axis("HORIZONTAL").value < 0.0 and
                self._data.y < _collision.top and
                Clock.frame_length(self._data.blocked_ledge_frames) > self._data.c_ledge_buffer_frames and
                self._source.p_hitbox.check_ledge_vertical_left(self._source.p_chamber.sprite_lists["ground"])):

            self._data.vel_y = 0.0
            self._data.vel_x = 0.0
            self._data.top = _collision.top
            self._data.at_ledge = True

            return self._switch.set_state("ledge_hold")

        self._data.vel_x = max(0.0, self._data.vel_x)
        self._switch.set_state("wall_slide")

    def p_collision_right(self, _collision: Sprite):
        self._data.at_ledge = True
        if (Clock.frame_length(Input.get_button("DASH").press_frame) <= self._data.c_dash_buffer_frames and
                self._data.vel_y):
            _acc_y = (abs(self._data.vel_x) / 2.0) * (self._data.vel_y / abs(self._data.vel_y))
            self._data.vel_y += _acc_y

        elif (self._data.direction > 0 and Input.get_axis("HORIZONTAL").value > 0.0 and
                self._data.y < _collision.top and
                Clock.frame_length(self._data.blocked_ledge_frames) > self._data.c_ledge_buffer_frames and
                self._source.p_hitbox.check_ledge_vertical_right(self._source.p_chamber.sprite_lists["ground"])):

            self._data.vel_y = 0.0
            self._data.vel_x = 0.0
            self._data.top = _collision.top
            self._data.at_ledge = True

            return self._switch.set_state("ledge_hold")

        self._data.vel_x = min(0.0, self._data.vel_x)
        self._switch.set_state("wall_slide")

    def p_collision_top(self, _collision: Sprite):
        if self._data.vel_x:
            if Clock.frame_length(Input.get_button("DASH").press_frame) <= self._data.c_dash_buffer_frames:
                _acc_x = (abs(self._data.vel_y) / 4.0) * (self._data.vel_x / abs(self._data.vel_x))
                self._data.vel_x += _acc_x

        self._data.vel_y = min(0.0, self._data.vel_y)


class WallSlideState(PlayerState):

    def __init__(self, _switch, _source):
        super().__init__(_switch, _source, "wall_slide")

    def p_into_state(self):
        self._data.forgiven_edge_frames = 0

    def p_out_of_state(self):
        pass

    def p_update(self):
        # find horizontal acceleration
        _target_velocity = self._data.c_max_vel * Input.get_axis("HORIZONTAL")

        _acc_x = self._data.c_max_dec_air
        if _target_velocity:
            if self._data.vel_x / _target_velocity < 0:
                _acc_x = self._data.c_max_turn_air
            elif abs(_target_velocity) > abs(self._data.vel_x):
                _acc_x = self._data.c_max_acc_air

        _diff = _target_velocity - self._data.vel_x
        _acc_x = min(abs(_diff), _acc_x * Clock.delta_time) * (_diff / abs(_diff)) if _diff else 0

        _acc_y = 0.0
        if not self._data.on_ground:
            if ((Input.get_axis("HORIZONTAL") and not Input.get_button("DASH")) and
                    (self._data.direction == -1 * self._data.on_left or
                     self._data.direction == 1 * self._data.on_right)):
                if self._data.vel_y <= 0:
                    _acc_y = -self._data.c_down_slide_gravity * Clock.delta_time
                else:
                    _acc_y = -self._data.c_up_slide_gravity * Clock.delta_time
            else:
                _acc_y = -self._data.c_base_gravity * Clock.delta_time

        self._data.acc = _acc_x, _acc_y
        self._data.vel_x += _acc_x
        self._data.vel_y += _acc_y

    def p_find_state(self):
        _next_state = self._name
        if Clock.frame_length(self._data.forgiven_jump_frames) <= self._data.c_jump_buffer_frames:
            self._data.vel_y = self._data.c_base_jump_speed * 1.5
            _acc = self._data.c_base_jump_speed
            if Input.get_button("DASH"):
                _acc += self._data.c_dash_jump_speed
            self._data.vel_x = _acc * -self._data.direction

            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")
        elif not self._data.on_left and not self._data.on_right:
            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("fall")

    def p_jump(self, _button: Button):
        self._data.vel_y = _button.pressed * self._data.c_base_jump_speed * 1.5
        if self._data.on_right and not self._data.on_left:
            _acc_x = -self._data.c_base_jump_speed
            if Input.get_button("DASH"):
                _acc_x -= self._data.c_dash_jump_speed
            self._data.vel_x = _button.pressed * _acc_x

            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")
        elif self._data.on_left and not self._data.on_right:
            _acc_x = self._data.c_base_jump_speed
            if Input.get_button("DASH"):
                _acc_x += self._data.c_dash_jump_speed
            self._data.vel_x = _button.pressed * _acc_x

            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")

    def p_crouch(self, _button: Button):
        pass

    def p_horizontal(self, _value: float):
        self._data.direction = self._data.direction if not _value else _value / abs(_value)

    def p_collision_bottom(self, _collision: Sprite):
        self._data.vel_y = max(0.0, self._data.vel_y)
        self._switch.set_state("stand")

    def p_collision_right(self, _collision: Sprite):
        self._data.vel_x = 0.0
        if (self._data.direction > 0 and Input.get_axis("HORIZONTAL").value > 0.0 and self._data.y < _collision.top and
                Clock.frame_length(self._data.blocked_ledge_frames) > self._data.c_ledge_buffer_frames and
                self._data.vel_y < self._data.c_max_vel and
                self._source.p_hitbox.check_ledge_vertical_right(self._source.p_chamber.sprite_lists["ground"])):

            self._data.vel_y = 0.0
            self._data.top = _collision.top
            self._data.at_ledge = True

            return self._switch.set_state("ledge_hold")

    def p_collision_left(self, _collision: Sprite):
        self._data.vel_x = 0.0
        if (self._data.direction < 0 and Input.get_axis("HORIZONTAL").value < 0.0 and self._data.y < _collision.top and
                Clock.frame_length(self._data.blocked_ledge_frames) > self._data.c_ledge_buffer_frames and
                self._data.vel_y < self._data.c_max_vel and
                self._source.p_hitbox.check_ledge_vertical_left(self._source.p_chamber.sprite_lists["ground"])):
            self._data.vel_y = 0.0
            self._data.top = _collision.top
            self._data.at_ledge = True

            return self._switch.set_state("ledge_hold")


class LedgeHoldState(PlayerState):

    def __init__(self, _switch, _source):
        super().__init__(_switch, _source, "ledge_hold")

    def p_into_state(self):
        pass

    def p_out_of_state(self):
        pass

    def p_update(self):
        pass

    def p_find_state(self):
        print(self._data.on_right, self._data.on_left, self._data.direction)
        if self._data.on_ground:
            self._data.at_ledge = False
            self._data.blocked_ledge_frames = Clock.frame
            return self._switch.set_state("stand")
        elif ((self._data.on_right and self._data.direction < 0.0) or
                (self._data.on_left and self._data.direction > 0.0)):
            self._data.at_ledge = False
            self._data.blocked_ledge_frames = Clock.frame
            return self._switch.set_state("fall")

    def p_jump(self, _button: Button):
        self._data.at_ledge = False
        self._data.blocked_ledge_frames = Clock.frame
        if self._data.on_right and not self._data.on_left:
            _acc_y = self._data.c_base_jump_speed
            if Input.get_button("DASH"):
                _acc_y = self._data.c_dash_jump_speed * 1.5
            self._data.vel_y = _button.pressed * _acc_y

            self._data.vel_x = -self._data.c_base_jump_speed * 0.5
            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")
        elif self._data.on_left and not self._data.on_right:
            _acc_y = self._data.c_base_jump_speed
            if Input.get_button("DASH"):
                _acc_y = self._data.c_dash_jump_speed * 1.5
            self._data.vel_y = _button.pressed * _acc_y

            self._data.vel_x = self._data.c_base_jump_speed * 0.5
            self._data.forgiven_edge_frames = 0
            self._data.forgiven_jump_frames = 0
            return self._switch.set_state("jump")

    def p_crouch(self, _button: Button):
        self._data.at_ledge = False
        self._data.blocked_ledge_frames = Clock.frame
        self._switch.set_state("wall_slide")

    def p_horizontal(self, _value: float):
        if _value:
            self._data.direction = _value / abs(_value)


class PlayerStateSwitch:

    def __init__(self, _source: "PlayerCharacter"):
        self._data: PlayerData = _source.p_data
        self._source: "PlayerCharacter" = _source
        self._states: Dict[str, PlayerState] = {"stand": StandState(self, _source),
                                                "run": RunState(self, _source),
                                                "ledge_hold": LedgeHoldState(self, _source),
                                                "jump": JumpState(self, _source),
                                                "fall": FallState(self, _source),
                                                "wall_slide": WallSlideState(self, _source)}

        self._current_state: PlayerState = self._states['fall']

        # TODO: remove placeholder variables
        self._state_name = Sprite()
        self._state_name_textures = {_name:
                                     load_texture(":assets:/textures/placeholder_state_names.png", x=32 * i,
                                                  width=32, height=16)
                                     for i, _name in enumerate(self._states.keys())}
        self._state_name.texture = self._state_name_textures['fall']

    def find_state(self):
        self._current_state.p_find_state()

    def set_state(self, _state):
        self._state_name.texture = self._state_name_textures[_state]
        _new_state = self._states[_state]
        if _new_state != self._current_state:
            self._current_state.p_out_of_state()
            _new_state.p_into_state()

            self._current_state = _new_state

    def state_update(self):
        self._current_state.p_update()

    def collision_bottom(self, _collision: Sprite):
        self._current_state.p_collision_bottom(_collision)

    def collision_top(self, _collision: Sprite):
        self._current_state.p_collision_top(_collision)

    def collision_left(self, _collision: Sprite):
        self._current_state.p_collision_left(_collision)

    def collision_right(self, _collision: Sprite):
        self._current_state.p_collision_right(_collision)

    @property
    def state(self):
        return self._current_state

    def p_jump(self, _button: Button):
        self._current_state.p_jump(_button)

    def p_crouch(self, _button: Button):
        self._current_state.p_crouch(_button)

    def p_horizontal(self, _value: float):
        self._current_state.p_horizontal(_value)

    def debug_draw(self):
        self._state_name.draw(pixelated=True)

    def debug_update_pos(self):
        self._state_name.position = self._data.x, self._data.top + 16
