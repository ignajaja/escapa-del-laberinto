import pygame, random, json #pygame es la librería que vamos a usar para mostrar graficamente el juego
import tkinter as tk
from tkinter import messagebox


ANCHO_VEN = 800
ALTO_VEN = 600
TAMANO_ESPACIO = 40

class Puntajes:
    def __init__(self, nombre, pantalla):
        self.nombre = nombre

    def ordenar(self):
        for i in range(len(self.puntajes)):
            for j in range(i+1, len(self.puntajes)):
                if self.puntajes[j]['puntaje'] > self.puntajes[i]['puntaje']:
                    self.puntajes[i], self.puntajes[j] = self.puntajes[j], self.puntajes[i]

    
    def guardar(self):
        with open('puntajes.json', 'w') as a:
            
            json.dump(self.puntajes, a)


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
    def __init__(self, x, y, nombre):
        self.x = x
        self.y = y
        self.energia = 100
        self.corriendo = False
        self.vel = 2
        self.vel_corriendo = 3
    
    def mover(self, mx, my, mapa):
        px = self.x + mx # px es la posición en la que va a quedar x
        py = self.y + my # py es la posición en la que va a quedar y
        
        if mapa.jugador_pasa(px, py):
            self.x = px
            self.y = py

            if self.corriendo and self.energia > 0:
                self.energia -= 1

    def correr(self, correr):
        if correr and self.energia > 0:
            self.corriendo = True
        else:
            self.corriendo = False

    def consumir_energia(self, can):
        self.energia = max(0, self.energia - can)
    
    def recuperar_energia(self, can):
        self.energia = min(100, self.energia + can)


    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, '#000000', ((self.x * TAMANO_ESPACIO)+(TAMANO_ESPACIO //2), (self.y * TAMANO_ESPACIO)+(TAMANO_ESPACIO //2)), TAMANO_ESPACIO//3)


class Enemigo:
    def __init__(self, x, y, vel):
        self.x = x
        self.y = y
        self.vel = vel
        self.vivo = True
        self.timeout = 0

    def perseguir(self, pos_jug_x, pos_jug_y, mapa):
        dx = pos_jug_x - self.x
        dy = pos_jug_y - self.y

        if abs(dx) > abs(dy):
            if dx > 0 and mapa.enemigo_pasa(self.x +1, self.y):
                self.x += 1
            elif dx > 0 and mapa.enemigo_pasa(self.x -1, self.y):
                self.x -= 1
        else:
            if dx > 0 and mapa.enemigo_pasa(self.x, self.y +1):
                self.y += 1
            elif dx > 0 and mapa.enemigo_pasa(self.x, self.y -1):
                self.y -= 1

    def escapar(self, pos_jug_x,  pos_jug_y, mapa):
        dx = self.x - pos_jug_x 
        dy = self.y - pos_jug_y 

        

class Mapa:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.espacios = []
        self.generar_mapa()

    def generar_mapa(self):
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                terreno = random.randint(0, 10)
                fila.append(terreno)
            self.espacios.append(fila)

        # self.crear_terreno()

        # self.asegurar_camino()

    def jugador_pasa(self, x, y):
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            terreno = self.obtener_terreno(x,y)
            return terreno.jugador_pasa()
        return False
            #     if x == 0 or x == self.ancho -1 or y == 0 or y == self.alto-1:
            #         fila.append(Muro(x,y))
                
            #     elif terreno == 1:
            #         fila.append(Muro(x,y))
            #     elif terreno == 2:
            #         fila.append(Liana(x,y))
            #     elif terreno == 3:
            #         fila.append(Tunel(x, y))
            #     else:
            #         fila.append(Camino(x, y))

            # self.espacios.append(fila)

    def jugador_pasa(self, x, y):
        if 0<=x < self.ancho and 0<=y < self.alto:
            return self.espacios[y][x].jugador_pasa()
        return False
    
    def dibujar(self, pantalla):
        for fila in self.espacios:
            for espacio in fila:
                espacio.dibujar(pantalla)


class Juego:
    def __init__(self, nombre):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VEN, ALTO_VEN))
        self.reloj = pygame.time.Clock()
        self.running = True
        self.nombre = nombre

        self.mapa = Mapa(20,15)
        self.jugador = Jugador(1,1, nombre)

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


class Puntajes:
    def __init__(self):
        self.puntajes = []

    def cargar_puntajes(self):
        try:
            with open('puntajes.json', 'r', encoding='utf-8') as a:
                self.puntajes = json.load(a)
        except:
            messagebox.showerror("Error", "Error cargando puntajes")
    
    def guardar_puntajes(self):
        try:
            with open("puntajes.json", "w", encoding='utf-8') as a:
                json.dump(self.puntajes, a, indent=4)
        except:
            messagebox.showerror("Error", "Error al guardar puntajes")
    
    def agregar_puntaje(self, nombre, puntaje):
        punt = {
            nombre: puntaje
        }
        self.puntajes.append(punt)
        self.puntajes.sort(key=lambda x: x['puntaje'], reverse=True)
        self.guardar_puntajes()

class VentanaPrincipal:
    def __init__(self):
        self.nombre = None
        self.ventana = tk.Tk()
        self.ventana.title("Escapa del laberinto")
        self.mostrar()

    def iniciar_juego():
        juego=Juego()
        juego.ejecutar()

    def mostrar(self):
        tk.Label(self.ventana,text='Escapa del laberinto', font=("Arial", 18, "bold"),fg="#000000").pack(pady=20)
        tk.Label(self.ventana,text='Ingrese su nombre para iniciar:', font=("Arial", 15, "bold"), fg="#000000").pack(pady=10)
        self.entry_nombre = tk.Entry(self.ventana, font=("Arial", 14)); self.entry_nombre.pack(pady=10); self.entry_nombre.insert(0, 'Jugador')
        self.entry_nombre.bind('<Return>', lambda event: VentanaPrincipal.iniciar_juego())
        tk.Button(self.ventana, text='Iniciar Juego', font=("Arial", 14), command=VentanaPrincipal.iniciar_juego).pack(pady=20)

    def validar_nombre(self):
        nombre = self.entry_nombre.get().strip()
        if not len(nombre) == 3:
            messagebox.showwarning("Error", "El nombre debe de tener 3 dígitos")
            return False
        return True
    
    def iniciar_juego(self):
        if self.validar_nombre():
            self.nombre = self.entry_nombre.get()
            self.ventana.destroy()

    

    def mostrar_puntajes(self):

    def ejecutar(self):
        self.ventana.mainloop()
        return self.nombre

    
def iniciar():
    ventana_principal = VentanaPrincipal()
    nombre = ventana_principal.ejecutar()

    if nombre == None:
        nombre = 'Jugador'

    juego = Juego(nombre)
    juego.ejecutar()
    root = tk.TK()
    root.withdraw()
    root.destroy()


if __name__ == "__main__":
    iniciar()

