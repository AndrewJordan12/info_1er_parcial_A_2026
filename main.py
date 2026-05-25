import logging
import arcade
import pymunk

from game_object import Bird, Column, Pig, YellowBird, BlueBird, BlackBird
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
PIG_TYPE = 3
LIMIT_TYPE = 4
LIMIT_MARGIN = 300

LEVEL_MAP = {
    1: {'columns': 3, 'pigs': 3, 'score': 100, 'bird': 1},
    2: {'columns': 4, 'pigs': 4, 'score': 100, 'bird': 2},
    3: {'columns': 4, 'pigs': 7, 'score': 100, 'bird': 3},
    4: {'columns': 5, 'pigs': 7, 'score': 100, 'bird': 4},
    5: {'columns': 6, 'pigs': 7, 'score': 100, 'bird': 3},
}
LEVELS = len(LEVEL_MAP)

class App(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("assets/img/background3.png")
        # crear espacio de pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.level = 1
        # agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        floor_shape.collision_type = GROUND_TYPE
        self.space.add(floor_body, floor_shape)

        left_wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        left_wall_shape = pymunk.Segment(left_wall_body,[-LIMIT_MARGIN, 0],[20, HEIGHT],0.0)

        right_wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        right_wall_shape = pymunk.Segment(right_wall_body,[WIDTH - 20, 0],[WIDTH + LIMIT_MARGIN, HEIGHT],0.0)

        roof_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        roof_shape = pymunk.Segment(roof_body, [-LIMIT_MARGIN, HEIGHT -20],[WIDTH + LIMIT_MARGIN, HEIGHT + LIMIT_MARGIN], 0.0)

        left_wall_shape.collision_type = LIMIT_TYPE
        left_wall_shape.sensor = True
        right_wall_shape.collision_type = LIMIT_TYPE
        right_wall_shape.sensor = True
        roof_shape.collision_type = LIMIT_TYPE
        roof_shape.sensor = True

        self.space.add(left_wall_body, left_wall_shape)
        self.space.add(right_wall_body, right_wall_shape)
        self.space.add(roof_body, roof_shape)

        handler = self.space.add_collision_handler(BIRD_TYPE, LIMIT_TYPE)
        handler.begin = self.onBirdHitLimit

        handler = self.space.add_collision_handler(BIRD_TYPE, GROUND_TYPE)
        handler.begin = self.onBirdHitGround

        handler = self.space.add_collision_handler(BIRD_TYPE, PIG_TYPE)
        handler.post_solve = self.onBirdHitPig
        
        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        self.actualBird = None
        self.isAiming = False
        self.addLevel()

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False
        self.score = 0
        self.birdsOnAir = []
        self.birdsOnGround = []
        # agregar un collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler

    def getLevelInfo(self):
        return LEVEL_MAP.get(self.level, LEVEL_MAP[LEVELS])

    def removeSprite(self, obj):
        if obj is None:
            return
        obj.remove_from_sprite_lists()
        if obj in self.sprites:
            self.sprites.remove(obj)
        if obj in self.world:
            self.world.remove(obj)
        if obj in self.birds:
            self.birds.remove(obj)
        if obj in self.birdsOnAir:
            self.birdsOnAir.remove(obj)
        if obj in self.birdsOnGround:
            self.birdsOnGround.remove(obj)
        self.space.remove(obj.shape, obj.body)
            
    def addLevel(self):
        self.add_columns()
        self.add_pigs()

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        #logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in list(self.world):
                if obj.shape in arbiter.shapes:
                    self.removeSprite(obj)

        return True

    def add_columns(self):
        num_columns = self.getLevelInfo()['columns']
        xs = [(((WIDTH // 2) + i * 60) % WIDTH) for i in range(num_columns)]
        for x in xs:
            self.add_column(x, 50)

    def add_column(self, x, y):
        column = Column(x, y, self.space)
        self.sprites.append(column)
        self.world.append(column)

    def add_pigs(self):
        num_pigs = self.getLevelInfo()['pigs']
        xs = [(((WIDTH // 2) + i * 60) % WIDTH) for i in range(num_pigs)]
        for x in xs:
            self.add_pig(x, 100)

    def add_pig(self, x, y):
        pig = Pig(x, y, self.space)
        pig.shape.collision_type = PIG_TYPE
        self.sprites.append(pig)
        self.world.append(pig)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)  # actualiza la simulacion de las fisicas
        self.sprites.update(delta_time)

    def levelUp(self):
        if self.level >= LEVELS:
            self.level = 1
        else:
            self.level += 1
        self.reset()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.actualBird is not None and self.actualBird in self.birdsOnAir:
                self.applySpecialAbility(self.actualBird)
            else:
                self.isAiming = True
                self.start_point = Point2D(x, y)
                self.end_point = Point2D(x, y)
                self.draw_line = True
                #logger.debug(f"Start Point: {self.start_point}")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT and self.isAiming:
            self.end_point = Point2D(x, y)
            #logger.debug(f"Dragging to: {self.end_point}")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT and self.isAiming:
            #logger.debug(f"Releasing from: {self.end_point}")
            self.draw_line = False
            self.isAiming = False
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)
            self.actualBird = self.createLevelBird(impulse_vector, self.start_point.x, self.start_point.y)
            
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.levelUp()

    def on_draw(self):
        self.clear()
        # arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y,
                             arcade.color.BLACK, 3)

    def createLevelBird(self, impulse_vector, x, y):
        level = self.getLevelInfo()['bird']
        return self.createBird(level, impulse_vector, x, y , self.space,)

    def createBird(self, birdId, impulse_vector, x, y , space, image_path=None):
        if image_path is None:
            image_path = "assets/img/red-bird3.png"

        createMap = {
            1: lambda: Bird(image_path, impulse_vector, x, y, space),
            2: lambda: YellowBird(impulse_vector, x, y, space, "assets/img/yellow.png"),
            3: lambda: BlueBird(impulse_vector, x, y, space, "assets/img/blue.png"),
            4: lambda: BlackBird(impulse_vector, x, y, space, "assets/img/red-bird3.png")
        }
        bird = createMap.get(birdId)()
        bird.shape.collision_type = BIRD_TYPE
        self.sprites.append(bird)
        self.birds.append(bird)
        self.birdsOnAir.append(bird)
        return bird

    def onBirdHitGround(self, arbiter, space, data):
        for bird in list(self.birdsOnAir):
            if bird.shape in arbiter.shapes:
                self.birdsOnAir.remove(bird)
                self.birdsOnGround.append(bird)
                if bird == self.actualBird:
                    self.actualBird = None
                break
        return True

    def onBirdHitLimit(self, arbiter, space, data):
        for bird in list(self.birdsOnAir):
            if bird.shape in arbiter.shapes:
                self.removeSprite(bird)
                if bird == self.actualBird:
                    self.actualBird = None
                break
        return True
    
    def onBirdHitPig(self, arbiter, space, data):
        for pig in list(self.world):
            if pig.shape in arbiter.shapes:
                self.removeSprite(pig)
                self.score += 50
                print(f"Score: {self.score}")
                scoreGoal = self.getLevelInfo()['score']
                if self.score >= scoreGoal:
                    self.levelUp()
                break
        return True

    def applySpecialAbility(self, bird):
        def addBlueBirds(data):
            original = data.get('original')
            if original is not None:
                self.removeSprite(original)

            posx, posy = data['pos']
            vectors = data['vectors']
            imagePath = data['image_path']
            for vector in vectors:
                self.createBird(3, vector, posx, posy, self.space, imagePath)

        handleMap = {
            3:  addBlueBirds
        }
        if bird.id == 1:
            return
        result = bird.special()
        if result is not None:
            handleMap.get(bird.id, lambda x: None)(result)
            self.actualBird = None

    def reset(self):
        for obj in list(self.sprites):
            self.removeSprite(obj)
        self.sprites.clear()
        self.birds.clear()
        self.world.clear()
        self.birdsOnAir.clear()
        self.birdsOnGround.clear()
        self.start_point = Point2D()
        self.end_point = Point2D()
        self.draw_line = False
        self.isAiming = False
        self.actualBird = None
        self.score = 0
        self.addLevel()

def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    game = App()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()