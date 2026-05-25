(La descripcion de uso está más abajo)
# Infografia UPB I/2026 - 1er parcial A (Angry Birds)

## Descripcion

Este repositorio contiene el codigo base para el proyecto de tipo A.

Implementa la mecanica fundamental de un clon de Angry Birds usando
`arcade` para el render y `pymunk` para la simulacion fisica. Usted
debera completar el codigo fuente e implementar funcionalidades
adicionales.

## Requisitos y ejecucion

Este proyecto usa [uv](https://docs.astral.sh/uv/) para gestionar Python
y las dependencias. Una vez instalado uv:

```bash
# clone (o forkee) el repositorio y entre a la carpeta
git clone <su-fork>.git
cd info_1er_parcial_A_2026

# correr el juego (uv crea el entorno automaticamente)
uv run main.py
```
### DESCRIPCIÓN DE USO ACÁ

## SlingShot

El usuario hace clic en un `start_point`,
arrastra hasta un `end_point` y suelta. El pajaro debe salir disparado en
la direccion OPUESTA al arrastre (como una resortera real):

```
    start (clic)  *<------ arrastre ------ * end (soltar)
                   --------> lanzamiento
```
No se podrá lanzar otro Bird hasta que el Bird lanzado haya aplicado su habilidad especial.
En el caso del Bird base o rojo (Nivel 1), no se podrá lanzar otro hasta que este haya salido de limites o tocado el suelo.

## Pajaros con habilidad especial (`game_object.py`)

Se probaran los pajaros en cada nivel, presionar la tecla espacio para cambiar de nivel o cumplir la lógica de cambio de nivel descrita en Sistema de Niveles. Para probar las habilidades especiales solo hacer click izquierdo, , los Birds pueden aplicar su habilidad especial solamente
mientras se encuentran en el aire.

- **YellowBird** - al hacer clic izquierdo mientras esta en vuelo,
  multiplica su impulso por `power_multiplier` (default 2) en la
  direccion actual de movimiento. Solo una vez por pajaro. 
  NIVEL: 2

- **BlueBird** - al hacer clic izquierdo mientras esta en vuelo, se
  reemplaza por 3 BlueBirds con direcciones separadas +30, 0 y -30
  grados respecto a la direccion actual. La magnitud de la velocidad se
  preserva. Solo una vez por pajaro.
  NIVEL: 3 y 5

- **BlackBird** - al hacer clic izquierdo mientras esta en vuelo, este escala
  su tamaño y masa por default en 3. Solo una vez por pajaro.
  NIVEL: 4

### Sistema de niveles (main.py)

Existen 5 niveles
Se puede cambiar entre niveles presionando la tecla espacio o mediante 
llegar a los puntos requeridos por el nivel (default de 100 pts)
Para ganar puntos se debe golpear a los Pigs con los Birds mediante el Slingshot,
cada Pig vale 50 pts.

