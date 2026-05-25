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
## Pajaros con habilidad especial (`game_object.py`)

Se probaran los pajaros en cada nivel, presionar espacio para cambiar de nivel.

- **YellowBird** - al hacer clic izquierdo mientras esta en vuelo,
  multiplica su impulso por `power_multiplier` (default 2) en la
  direccion actual de movimiento. Solo una vez por pajaro.

- **BlueBird** - al hacer clic izquierdo mientras esta en vuelo, se
  reemplaza por 3 BlueBirds con direcciones separadas +30, 0 y -30
  grados respecto a la direccion actual. La magnitud de la velocidad se
  preserva. Solo una vez por pajaro.

- **BlackBird** - al hacer clic izquierdo mientras esta en vuelo, este escala
  su tamaño y masa por default en 3. Solo una vez por pajaro.

### Sistema de niveles

Existen 5 niveles
Para avanzar se debe golpear a los Pigs con los Birds, cada Pig da 50 pts 
Cada nivel tiene un nivel de puntos requerido de 100 pts

Se puede cambiar entre niveles presionando espacio

