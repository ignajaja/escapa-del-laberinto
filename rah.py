import pygame
import sys

# Configuración inicial
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 60
TAMANO_CELDA = 40

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
GRIS = (128, 128, 128)

class Terreno:
    """Clase base para tipos de terreno"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = BLANCO
    
    def puede_pasar_jugador(self):
        return True
    
    def puede_pasar_enemigo(self):
        return True
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, 
                        (self.x * TAMANO_CELDA, self.y * TAMANO_CELDA, 
                         TAMANO_CELDA, TAMANO_CELDA))
        pygame.draw.rect(pantalla, NEGRO, 
                        (self.x * TAMANO_CELDA, self.y * TAMANO_CELDA, 
                         TAMANO_CELDA, TAMANO_CELDA), 1)

class Camino(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = BLANCO

class Muro(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = GRIS
    
    def puede_pasar_jugador(self):
        return False
    
    def puede_pasar_enemigo(self):
        return False

class Tunel(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = AZUL
    
    def puede_pasar_enemigo(self):
        return False

class Liana(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = VERDE
    
    def puede_pasar_jugador(self):
        return False

class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energia = 100
        self.corriendo = False
    
    def mover(self, dx, dy, mapa):
        nueva_x = self.x + dx
        nueva_y = self.y + dy
        
        if mapa.puede_pasar_jugador(nueva_x, nueva_y):
            self.x = nueva_x
            self.y = nueva_y
            
            if self.corriendo and self.energia > 0:
                self.energia -= 0.5
    
    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, ROJO, (self.x * TAMANO_CELDA + TAMANO_CELDA // 2, self.y * TAMANO_CELDA + TAMANO_CELDA // 2),TAMANO_CELDA // 3)

class Mapa:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.terrenos = []
        self.generar_basico()
    
    def generar_basico(self):
        """Genera un mapa simple para pruebas"""
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                # Bordes son muros
                if x == 0 or x == self.ancho - 1 or y == 0 or y == self.alto - 1:
                    fila.append(Muro(x, y))
                # Algunos obstáculos internos
                elif (x + y) % 7 == 0:
                    fila.append(Muro(x, y))
                elif x % 5 == 0:
                    fila.append(Tunel(x, y))
                elif y % 5 == 0:
                    fila.append(Liana(x, y))
                else:
                    fila.append(Camino(x, y))
            self.terrenos.append(fila)
    
    def puede_pasar_jugador(self, x, y):
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            return self.terrenos[y][x].puede_pasar_jugador()
        return False
    
    def dibujar(self, pantalla):
        for fila in self.terrenos:
            for terreno in fila:
                terreno.dibujar(pantalla)

class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Escapa del Laberinto")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        # Crear mapa y jugador
        self.mapa = Mapa(20, 15)
        self.jugador = Jugador(1, 1)
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
    
    def actualizar(self):
        teclas = pygame.key.get_pressed()
        
        # Correr con Shift
        self.jugador.corriendo = teclas[pygame.K_LSHIFT]
        
        # Movimiento
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.jugador.mover(0, -1, self.mapa)
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.jugador.mover(0, 1, self.mapa)
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.jugador.mover(-1, 0, self.mapa)
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.jugador.mover(1, 0, self.mapa)
        
        # Recuperar energía cuando no corre
        if not self.jugador.corriendo and self.jugador.energia < 100:
            self.jugador.energia += 0.2
    
    def dibujar(self):
        self.pantalla.fill(NEGRO)
        self.mapa.dibujar(self.pantalla)
        self.jugador.dibujar(self.pantalla)
        
        # Dibujar barra de energía
        pygame.draw.rect(self.pantalla, ROJO, (10, 10, 200, 20))
        pygame.draw.rect(self.pantalla, VERDE, 
                        (10, 10, int(self.jugador.energia * 2), 20))
        
        pygame.display.flip()
    
    def ejecutar(self):
        while self.corriendo:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()