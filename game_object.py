import math
import arcade
import pymunk
from game_logic import ImpulseVector


class Bird(arcade.Sprite):
    """
    Bird class. This represents an angry bird. All the physics is handled by Pymunk,
    the init method only set some initial properties
    """
    def __init__(
        self,
        image_path: str,
        impulse_vector: ImpulseVector,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 5,
        radius: float = 12,
        max_impulse: float = 300,
        power_multiplier: float = 20,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)
        self.scale = (radius * 2) / max(self.width, self.height)
        # body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        impulse = min(max_impulse, impulse_vector.impulse) * power_multiplier
        impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
        # apply impulse
        body.apply_impulse_at_local_point(impulse_pymunk.rotated(impulse_vector.angle))
        # shape
        shape = pymunk.Circle(body, radius)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer

        space.add(body, shape)

        self.body = body
        self.shape = shape
        self.space = space
        self.max_impulse = max_impulse
        self.id = 1
        self.abilityUsed = False

    def update(self, delta_time):
        """
        Update the position of the bird sprite based on the physics body position
        """
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class Pig(arcade.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 0.4,
        collision_layer: int = 0,
    ):
        super().__init__("assets/img/pig_failed.png", 0.1)
        moment = pymunk.moment_for_circle(mass, 0, self.width / 2 - 3)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Circle(body, self.width / 2 - 3)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self, delta_time):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class PassiveObject(arcade.Sprite):
    """
    Passive object that can interact with other objects.
    """
    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)

        moment = pymunk.moment_for_box(mass, (self.width, self.height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (self.width, self.height))
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self, delta_time):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class Column(PassiveObject):
    def __init__(self, x, y, space):
        super().__init__("assets/img/column.png", x, y, space)


class YellowBird(Bird):
    """
    Variante del Bird que, mientras esta en vuelo, puede recibir un "boost".

    Comportamiento esperado:
    - Si el usuario hace clic izquierdo mientras este pajaro esta en vuelo,
      su impulso se multiplica por `power_multiplier` (default 2) aplicado
      en la direccion ACTUAL de movimiento.
    - El boost solo deberia aplicarse una vez (no acumular en cada clic).
    - Recomendacion: usar "assets/img/yellow.png" como sprite.

    Pista: para aplicar el boost, usar
        self.body.apply_impulse_at_local_point(...)
    con un vector en la direccion actual de la velocidad del cuerpo
    (self.body.velocity).
    """

    def __init__(self, impulse_vector, x, y, space, image_path="assets/img/yellow.png"):
        super().__init__(
            image_path,
            impulse_vector,
            x,
            y,
            space,
        )
        self.id = 2
    
    def special(self):
        if self.abilityUsed:
            return
        self.boost()
    
    def boost(self, power_multiplier=2):
        velocity = self.body.velocity
        if velocity.length == 0:
            return
        impulse = min(self.max_impulse, velocity.length) * power_multiplier
        impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
        self.body.apply_impulse_at_local_point(impulse_pymunk.rotated(velocity.angle))
        self.abilityUsed = True

class BlueBird(Bird):
    """
    Variante del Bird que se divide en 3 al hacer clic en vuelo.

    Comportamiento esperado:
    - Si el usuario hace clic izquierdo mientras este pajaro esta en vuelo,
      instantaneamente se reemplaza por 3 BlueBirds con direcciones de
      vuelo separadas por +30, 0 y -30 grados respecto a la direccion
      actual. La magnitud de la velocidad se preserva.
    - La division solo deberia ocurrir una vez por pajaro.
    - Recomendacion: usar "assets/img/blue.png" como sprite.

    Pista: para crear los 2 nuevos pajaros se necesita acceso al
    pymunk.Space y a las SpriteLists del juego. El metodo puede devolver
    los nuevos pajaros para que main.py los agregue, o recibir las listas
    como argumento. Esa decision de diseno es parte del ejercicio.
    """

    def __init__(self, impulse_vector, x, y, space, image_path="assets/img/blue.png"):
        super().__init__(
            image_path,
            impulse_vector,
            x,
            y,
            space
        )
        self.image_path = image_path
        self.id = 3

    def special(self):
        if self.abilityUsed:
            return None
        else:
            return self.split()

    def split(self, separationAngle = 30):
        self.abilityUsed = True
        velocity = self.body.velocity
        speed = velocity.length
        offset = math.radians(separationAngle)
        scaled = speed * 5 / 20
        angles = [velocity.angle - offset, velocity.angle, velocity.angle + offset]
        vectors = [ImpulseVector(a, scaled) for a in angles]

        data = {
            'vectors': vectors,
            'pos': (self.center_x, self.center_y),
            'image_path': self.image_path,
            'original': self,        
        }
        return data

class BlackBird(Bird):
    def __init__(self, impulse_vector, x, y, space, image_path="assets/img/red-bird3.png"):
        super().__init__(
            image_path,
            impulse_vector,
            x,
            y,
            space
        )
        self.image_path = image_path
        self.id = 4

    def special(self):
        if self.abilityUsed:
            return None
        else:
            self.getBig()

    def getBig(self, scale_factor=3):
        self.abilityUsed = True
        scale_x, scale_y = self.scale
        self.scale = (scale_x * scale_factor, scale_y * scale_factor)
        new_radius = self.shape.radius * scale_factor
        self.shape.unsafe_set_radius(new_radius)
        self.body.mass *= scale_factor * scale_factor
        self.body.moment = pymunk.moment_for_circle(self.body.mass, 0, new_radius)
        if self.shape.space is not None:
            self.shape.space.reindex_shape(self.shape)

    