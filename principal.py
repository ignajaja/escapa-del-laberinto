import pygame, random, json #pygame es la librería que vamos a usar para mostrar graficamente el juego
import tkinter as tk
from tkinter import messagebox


ANCHO_VEN = 800
ALTO_VEN = 600
TAMANO_ESPACIO = 40

class Puntajes:
    def __init__(self):
        self.archivo = "puntajes.json"
        self.puntajes = []
        self.cargar_punt()
    
    def cargar_punt(self):
        try:
            with open(self.archivo, 'r', encoding='utf-8') as a:
                self.puntajes = json.load(a)
        except:
            messagebox.showerror("Error", "Error al cargar los puntajes")
    
    def guardar_punt(self):
        try:
            with open(self.archivo, 'w') as a:
                    json.dump(self.puntajes, a, indent=4)
        except:
            messagebox.showerror("Error", "Error al guardar puntajes")

    def agregar_punt(self, nombre, puntaje, tipo):
        nuevo = {
            "nombre": nombre,
            "puntaje": puntaje,
            "tipo": tipo
        }
        self.puntajes.append(nuevo)
        self.puntajes.sort(key=lambda x: x['puntaje'], reverse=True)
        self.guardar_punt()


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

class Salida(Espacio):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.color = "#002fff"

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
        self.nombre = nombre
        self.energia = 100
        self.corriendo = False
    
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
        self.salida = (ancho-2, alto-2)
        self.generar_mapa()

    def generar_mapa(self):
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                terreno = random.randint(1,13)
                if (x,y) == self.salida:
                    fila.append(Salida(x,y))
                
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
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            terreno = self.obtener_terreno(x,y)
            return terreno.jugador_pasa()
        return False

    def jugador_pasa(self, x, y):
        if 0<=x < self.ancho and 0<=y < self.alto:
            return self.espacios[y][x].jugador_pasa()
        return False
    
    def dibujar(self, pantalla):
        for fila in self.espacios:
            for espacio in fila:
                espacio.dibujar(pantalla)


class Juego:
    def __init__(self, nombre, tipo):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VEN, ALTO_VEN))
        self.reloj = pygame.time.Clock()
        self.running = True
        self.jugador = Jugador(1,1,nombre)
        self.tipo = tipo
        self.tiempo_ini = pygame.time.get_ticks()
        self.tiempo = 0
        self.mapa = Mapa(20,15)
        self.juego_termi = False
        self.juego_ganad = False
        self.puntajes = Puntajes()
    
        pygame.display.set_caption("Escapa del laberinto")

    def verificar_salida(self):
        if (self.jugador.x, self.jugador.y) == self.mapa.salida:
            return True
        return False
    
    def calcular_puntaje(self):
        return 1000 - (self.tiempo/1000)

    def finalizar(self):
        self.juego_termi = True
        self.juego_ganad = True

        segundos = self.tiempo/1000
        puntaje = self.calcular_puntaje()
        self.puntajes.agregar_punt(self.jugador.nombre, puntaje, self.tipo)

    def cerrar(self):
        for evento in pygame.event.get():
            if evento.type ==pygame.QUIT:
                self.running = False

    def actualizar(self):
        if self.juego_termi:
            return
        self.tiempo = pygame.time.get_ticks() - self.tiempo_ini

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
        if self.verificar_salida():
            self.finalizar()
        

    def dibujar(self):
        self.pantalla.fill("#000000")
        self.mapa.dibujar(self.pantalla)
        self.jugador.dibujar(self.pantalla)
        self.texto_pygame = pygame.font.Font(None, 28)

        pygame.draw.rect(self.pantalla, "#ff0000", (10,10, int(self.jugador.energia*2), 20))

        if self.juego_termi and self.juego_ganad:
            pantalla_victoria = pygame.Surface((ANCHO_VEN, ALTO_VEN))
            pantalla_victoria.fill("#000000")
            self.pantalla.blit(pantalla_victoria,(0,0))

            texto_victoria = self.texto_pygame.render("Victoria", True, "#fffb00")
            self.pantalla.blit(texto_victoria, (ANCHO_VEN//2, ALTO_VEN//2))

            puntaje = self.calcular_puntaje()
            texto_puntaje = self.texto_pygame.render(f"{puntaje}", True, "#ffffff")
            self.pantalla.blit(texto_puntaje, (ANCHO_VEN//2, ALTO_VEN//2-40))


        pygame.display.flip()

    def ejecutar(self):
        while self.running:
            self.cerrar()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        
        pygame.quit()

class VentanaPrincipal:
    def __init__(self):
        self.nombre = None
        self.ventana = tk.Tk()
        self.ventana.title("Escapa del laberinto")
        self.mostrar()


    def mostrar(self):
        tk.Label(self.ventana,text='Escapa del laberinto', font=("Arial", 18, "bold"),fg="#000000").pack(pady=20)
        tk.Label(self.ventana,text='Ingrese su nombre para iniciar:', font=("Arial", 15, "bold"), fg="#000000").pack(pady=10)
        self.entry_nombre = tk.Entry(self.ventana, font=("Arial", 14)); self.entry_nombre.pack(pady=10); self.entry_nombre.insert(0, 'Jugador')
        tk.Label(self.ventana,text='Ingrese 1 para jugar de escapista\ny 2 para cazador:', font=("Arial", 15, "bold"), fg="#000000").pack(pady=10)
        self.entry_tipo = tk.Entry(self.ventana, font=("Arial", 14)); self.entry_tipo.pack(pady=10); self.entry_tipo.insert(0, '1')
        
        tk.Button(self.ventana, text='Iniciar Juego', font=("Arial", 14), command=self.iniciar_juego).pack(pady=20)

    def validar_nombre(self):
        nombre = self.entry_nombre.get().strip()
        if not len(nombre) == 3:
            messagebox.showwarning("Error", "El nombre debe de tener 3 dígitos")
            return False
        return True
    
    def validar_tipo(self):
        tipo = self.entry_tipo.get().strip()
        if not (tipo == "1" or tipo == "2"):
            messagebox.showwarning("Error", "El tipo debe ser 1 o 2")
            return False
        return True
    
    def iniciar_juego(self):
        if self.validar_nombre() and self.validar_tipo():
            self.nombre = self.entry_nombre.get()
            self.tipo = self.entry_tipo.get()
            self.ventana.destroy()

    def mostrar_puntajes(self):
        archivo_punt = Puntajes()
        puntajes = archivo_punt.puntajes

        if not puntajes:
            return messagebox.showinfo("Puntajes", "No hay puntajes")
        
        ventana_puntajes = tk.Toplevel(self.ventana)
        ventana_puntajes.title("Puntajes")
        tk.Label("Puntajes más altos")
        panel_izq = tk.Frame(ventana_puntajes).pack(side='left', fill='both', padx=(0,10))
        panel_der = tk.Frame(ventana_puntajes).pack(side='right', fill='both', padx=(0,10))

        texto_esc = tk.Text(panel_izq, font=("Arial", 10, "bold")); texto_esc.pack()
        texto_caz = tk.Text(panel_der, font=("Arial", 10, "bold")); texto_caz.pack()

        texto_esc.insert("Escapistas: \n")
        count = 0
        for i, puntaje in enumerate(puntajes):
            if puntaje['tipo'] == "1" and count!=5:
                texto_esc.insert(f"{i+1} - {puntaje['nombre']}: {[puntaje['puntaje']]}\n")
                count += 1
                break
            break

        texto_caz.insert("Cazadores: \n")
        count = 0
        for j, puntaje in enumerate(puntajes):
            if puntaje['tipo'] == "2" and count!=5:
                texto_caz.insert(f"{j+1} - {puntaje['nombre']}: {[puntaje['puntaje']]}\n")
                count += 1
                break
            break


    def ejecutar(self):
        self.ventana.mainloop()
        return self.nombre, self.tipo

    
def iniciar():
    ventana_principal = VentanaPrincipal()
    nombre, tipo = ventana_principal.ejecutar()

    if nombre == None:
        nombre = 'JUG'
    if tipo == None:
        tipo = "1"

    juego = Juego(nombre, tipo)
    juego.ejecutar()
    root = tk.Tk()
    root.withdraw()
    root.destroy()


if __name__ == "__main__":
    iniciar()

