import pygame, random #pygame es la librería que vamos a usar para mostrar graficamente el juego


ANCHO_VEN = 800
ALTO_VEN = 600
TAMANO_ESPACIO = 40

class Espacio:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = "#ffffff"

    def jugador_pasa(self):
        return True
    
    def enemigo_pasa(self):
        return True
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, (self.x * TAMANO_ESPACIO, self.y * TAMANO_ESPACIO, TAMANO_ESPACIO, TAMANO_ESPACIO))
        pygame.draw.rect(pantalla, "#000000", (self.x * TAMANO_ESPACIO, self.y * TAMANO_ESPACIO, TAMANO_ESPACIO, TAMANO_ESPACIO), 1)

class Camino(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#e3ff97"

class Muro(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#888888"

    def jugador_pasa(self):
        return False
    def enemigo_pasa(self):
        return False
    
class Liana(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#80ff80"

    def jugador_pasa(self):
        return False
    def enemigo_pasa(self):
        return True
    
class Tunel(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#b66c2f"

class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energia = 100
        self.corriendo = False
    
    def mover(self, mx, my, mapa):
        px = self.x + mx # px es la posición en la que va a quedar x
        py = self.y + my # py es la posición en la que va a quedar y
        print(self.x, self.y, px, py)
        
        if mapa.jugador_pasa(px, py):
            self.x = px
            self.y = py

            if self.corriendo and self.energia > 0:
                self.energia -= 1

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, 'white', ((self.x * TAMANO_ESPACIO)+(TAMANO_ESPACIO //2), (self.y * TAMANO_ESPACIO)+(TAMANO_ESPACIO //2)), TAMANO_ESPACIO//3)

class Mapa:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.espacios = []
        self.generar_basico()

    def generar_basico(self):
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                terreno = random.randint(0, 10)
                if x == 0 or x == self.ancho -1 or y == 0 or y == self.alto-1:
                    fila.append(Muro(x,y))
                
                elif terreno == 1:
                    fila.append(Muro(x,y))
                elif terreno == 2:
                    fila.append(Liana(x,y))
                elif terreno == 3:
                    fila.append(Tunel(x, y))
                else:
                    fila.append(Camino(x, y))

            self.espacios.append(fila)

    def jugador_pasa(self, x, y):
        if 0<=x < self.ancho and 0<=y < self.alto:
            return self.espacios[y][x].jugador_pasa()
        return False
    
    def dibujar(self, pantalla):
        for fila in self.espacios:
            for espacio in fila:
                espacio.dibujar(pantalla)


class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VEN, ALTO_VEN))
        self.reloj = pygame.time.Clock()
        self.running = True

        self.mapa = Mapa(20,15)
        self.jugador = Jugador(1,1)

    def cerrar(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.running = False

    def actualizar(self):

        entradas = pygame.key.get_pressed()
        self.jugador.corriendo = entradas[pygame.K_LSHIFT]


        if entradas[pygame.K_w] or entradas[pygame.K_UP]:
            self.jugador.mover(0,-1, self.mapa)
        if entradas[pygame.K_s] or entradas[pygame.K_DOWN]:
            self.jugador.mover(0,1, self.mapa)
        if entradas[pygame.K_d] or entradas[pygame.K_RIGHT]:
            self.jugador.mover(1,0, self.mapa)
        if entradas[pygame.K_a] or entradas[pygame.K_LEFT]:
            self.jugador.mover(-1,0, self.mapa)
            
        if not self.jugador.corriendo and self.jugador.energia < 100:
            self.jugador.energia += 0.5
        

    def dibujar(self):
        self.pantalla.fill("#000000")
        self.mapa.dibujar(self.pantalla)
        self.jugador.dibujar(self.pantalla)

        pygame.draw.rect(self.pantalla, "#ff0000", (10,10, int(self.jugador.energia*2), 20))

        pygame.display.flip()

    def ejecutar(self):
        while self.running:
            self.cerrar()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        
        pygame.quit()
    
if __name__ == "__main__":
        juego=Juego()
        juego.ejecutar()
