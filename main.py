import math
import logging
import arcade
import pymunk

from game_object import Bird, Column, Pig, YellowBird, BlueBird
from game_logic import get_impulse_vector, Point2D, get_distance

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 1400
HEIGHT = 600
TITLE = "Angry birds"
GRAVITY = -900
BIRD_TYPE = 1
GROUND_TYPE = 2


class App(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("assets/img/background3.png")
        # crear espacio de pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        floor_shape.collision_type = GROUND_TYPE
        self.space.add(floor_body, floor_shape)

        handler = self.space.add_collision_handler(BIRD_TYPE, GROUND_TYPE)
        handler.begin = self.onBirdHitGround

        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        self.add_columns()
        self.add_pigs()

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False
        self.level = 1
        self.birdTypes = 3
        self.birdsOnAir = []
        self.birdsOnGround = []
        # agregar un collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in self.world:
                if obj.shape in arbiter.shapes:
                    obj.remove_from_sprite_lists()
                    self.space.remove(obj.shape, obj.body)

        return True

    def add_columns(self):
        for x in range(WIDTH // 2, WIDTH, 400):
            column = Column(x, 50, self.space)
            self.sprites.append(column)
            self.world.append(column)

    def add_pigs(self):
        pig1 = Pig(WIDTH / 2, 100, self.space)
        self.sprites.append(pig1)
        self.world.append(pig1)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)  # actualiza la simulacion de las fisicas
        self.sprites.update(delta_time)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.applySpecialAbility()
            self.start_point = Point2D(x, y)
            self.end_point = Point2D(x, y)
            self.draw_line = True
            logger.debug(f"Start Point: {self.start_point}")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            self.end_point = Point2D(x, y)
            logger.debug(f"Dragging to: {self.end_point}")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            logger.debug(f"Releasing from: {self.end_point}")
            self.draw_line = False
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)
            self.createLevelBird(self.level, impulse_vector, self.start_point.x, self.start_point.y, self.space)   
            
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.level += 1
            self.reset()

    def on_draw(self):
        self.clear()
        # arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y,
                             arcade.color.BLACK, 3)

    def createLevelBird(self, level, impulse_vector, x, y , space):
        level = ((level - 1) % self.birdTypes) + 1
        return self.createBird(level, impulse_vector, x, y , space)

    def createBird(self, birdId, impulse_vector, x, y , space, image_path=None):
        if image_path is None:
            image_path = "assets/img/red-bird3.png"

        createMap = {
            1: lambda: Bird(image_path, impulse_vector, x, y, space),
            2: lambda: YellowBird(impulse_vector, x, y, space, "assets/img/yellow.png"),
            3: lambda: BlueBird(impulse_vector, x, y, space, "assets/img/blue.png")
        }
        bird = createMap.get(birdId)()
        bird.shape.collision_type = BIRD_TYPE
        self.sprites.append(bird)
        self.birds.append(bird)
        self.birdsOnAir.append(bird)
        return bird

    def onBirdHitGround(self, arbiter, space, data):
        for bird in self.birdsOnAir:
            if bird.shape in arbiter.shapes:
                self.birdsOnAir.remove(bird)
                self.birdsOnGround.append(bird)
                break
        return True

    def applySpecialAbility(self):
        def addBlueBirds(data):
            original = data.get('original')
            if original is not None:
                original.remove_from_sprite_lists()
                self.space.remove(original.shape, original.body)
                if original in self.birdsOnAir:
                    self.birdsOnAir.remove(original)

            posx, posy = data['pos']
            vectors = data['vectors']
            imagePath = data['image_path']
            for vector in vectors:
                bird = self.createBird(1, vector, posx, posy, self.space, imagePath)

        handleMap = {
            3:  addBlueBirds
        }
        for bird in self.birdsOnAir:
            if bird.id == 1:
                continue
            result = bird.special()
            if result is not None:
                handleMap.get(bird.id, lambda x: None)(result)

    def reset(self):
        for obj in self.sprites:
            obj.remove_from_sprite_lists()
            self.space.remove(obj.shape, obj.body)
        self.sprites.clear()
        self.birdsOnAir.clear()
        self.birdsOnGround.clear()
        self.add_columns()
        self.add_pigs()

def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    game = App()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()