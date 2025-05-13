import pygame
import sys
import random

pygame.init()
pygame.mixer.init()

# Ses efektleri
bomb_drop_sound      = pygame.mixer.Sound("ses/bomba_dusme_efekti.wav")
bomb_explosion_sound = pygame.mixer.Sound("ses/bomba_patlama.wav")
game_over_sound      = pygame.mixer.Sound("ses/game_over.wav")
heart_collect_sound  = pygame.mixer.Sound("ses/kalp_toplama.wav")
plane_sound = pygame.mixer.Sound("ses/ucak.wav")
pygame.mixer.music.load("ses/arkaplan_muzigi.wav")   
pygame.mixer.music.set_volume(0.4)                  
pygame.mixer.music.play(-1) 
plane_sound.play(-1)

# Ekran boyutu ve pencere ayarları
WIDTH, HEIGHT = 905, 660
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kalp Yağmuru")

# FPS ayarı
clock = pygame.time.Clock()

# Arka plan yükleme
background = pygame.image.load("arkaplan/arkaplan.png")

# Karakter yükleme ve animasyon ayarları
sprite_sheet = pygame.image.load("karakter/karakter.png").convert_alpha()
columns, rows = 9, 3
frame_width  = sprite_sheet.get_width()  // columns
frame_height = sprite_sheet.get_height() // rows

def get_frame(row, col):
    x, y = (col-1)*frame_width, (row-1)*frame_height
    return sprite_sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))

def get_frames(sheet, frame_width, frame_height):
    frames = []
    cols = sheet.get_width() // frame_width
    for i in range(cols):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        frames.append(sheet.subsurface(rect))
    return frames

# Kullanacağım karakter frameleri
yuru_animasyon  = [
    get_frame(1, 1),
    get_frame(2, 2),
    get_frame(2, 1)
]

#Animasyon 
frame_indeksi   = 0
frame_suresi    = 150                    
son_guncelleme  = pygame.time.get_ticks()

# Karakter dikdörtgeni
karakter        = yuru_animasyon[0]
karakter_rect   = karakter.get_rect()
karakter_rect.midbottom = (WIDTH//2, HEIGHT-10)

# Hız ve hareket için değişkenler 
hiz             = 5      # Piksel/frame hızı
velocity_x      = 0      # Anlık x-yönlü hız
direction       = 'right'

# Yürüyüş animasyonları iki yönlü
yuru_animasyon_sag = yuru_animasyon
yuru_animasyon_sol = [pygame.transform.flip(frm, True, False) for frm in yuru_animasyon]

# Karakter gölgesi yüzeyi
shadow_width  = frame_width
shadow_height = frame_height // 4
shadow_surf   = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect())

# Uçak animasyonu ve hareket ayarları 
ucak_animasyon = [
    pygame.image.load("ucak/ucak1.png").convert_alpha(),
    pygame.image.load("ucak/ucak2.png").convert_alpha()
]

scale_factor = 0.35 # Uçak boyutu ayarlama

for i, surf in enumerate(ucak_animasyon):
    w, h = surf.get_size()
    ucak_animasyon[i] = pygame.transform.scale(
        surf,
        (int(w * scale_factor), int(h * scale_factor))
    )

ucak_frame_index    = 0
ucak_frame_interval = 150 
ucak_last_update    = pygame.time.get_ticks()

ucak_rect       = ucak_animasyon[0].get_rect(topleft=(0, 40)) 
ucak_hiz        = 3
ucak_direction  = 'right'          

# Bomba sprite-sheet yükleme ve frameleri ayarlanma
bomb_sheet = pygame.image.load("objeler/bomba.png").convert_alpha()

bfw = bomb_sheet.get_height()
bfh = bomb_sheet.get_height()
bomb_frames = get_frames(bomb_sheet, bfw, bfh)

bomb_normal    = bomb_frames[:-4]   
bomb_explosion = bomb_frames[-4:] 

BOMB_SCALE = 1.0   # bomba boyutu ayarlama
HEART_SCALE = 0.7  # kalp boyutu ayarlama

# Bombanın düşme framelerini ölçekleme
bomb_normal = [
    pygame.transform.scale(f, (
        int(f.get_width() * BOMB_SCALE),
        int(f.get_height() * BOMB_SCALE)
    ))
    for f in bomb_normal
]
# Bombanın patlama framelerini ölçekleme
bomb_explosion = [
    pygame.transform.scale(f, (
        int(f.get_width() * BOMB_SCALE),
        int(f.get_height() * BOMB_SCALE)
    ))
    for f in bomb_explosion
]

# Kalp resmi yükeleme
heart_image = pygame.image.load("objeler/kalp.png").convert_alpha()
heart_original = heart_image  # ölçekleme veya pulse için saklayabilirsin

# Kalbi ölçekleme
heart_image = pygame.transform.scale(
    heart_original,
    (
        int(heart_original.get_width() * HEART_SCALE),
        int(heart_original.get_height() * HEART_SCALE)
    )
)

class Drop:
    def __init__(self, frames, x, y, speed, anim_interval=100):
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.anim_interval = anim_interval
        self.last_update = pygame.time.get_ticks()
        self.exploding = False

    def update(self):
        # Aşağı doğru hareket
        self.rect.y += self.speed
        
        # Animasyon
        now = pygame.time.get_ticks()
        if now - self.last_update > self.anim_interval:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Bomb(Drop): #Bomba sınıfı
     def __init__(self, x, y, speed):
         super().__init__(bomb_normal, x, y, speed)

     def explode(self):
        self.frames = bomb_explosion
        self.frame_index = 0
        self.exploding = True
        EXPLOSION_OFFSET = 60
        self.rect.bottom = HEIGHT - EXPLOSION_OFFSET



class Heart(Drop): #Kalp sınıfı
    def __init__(self, x, y, speed):
        super().__init__([heart_image], x, y, speed)
    def update(self):
        self.rect.y += self.speed

                            
# Oyun döngüsü
running = True

#Bomba ve kalp spwanlama
drops = []
drop_timer = pygame.time.get_ticks()
drop_interval = 1000  # ilk spawn aralığı (ms)

# Oyun skoru ve HUD fontu
score = 0
font  = pygame.font.Font(None, 36)
heart_count = 0


while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Tuşa basıldığında karakter yönünü ayarlama
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                velocity_x = hiz
                direction  = 'right'
            elif event.key == pygame.K_LEFT:
                velocity_x = -hiz
                direction  = 'left'

        # Tuş bırakıldığında durma
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                velocity_x = 0

    # Karakteri hareket ettirme
    karakter_rect.x += velocity_x
    
    # Yatay pencere sınırı kontrolü
    karakter_rect.x = max(0, min(WIDTH - frame_width, karakter_rect.x))
    
    #Uçak hareketi 
    if ucak_direction == 'right':
        ucak_rect.x += ucak_hiz
        if ucak_rect.right >= WIDTH:
            ucak_direction = 'left'
    else:
        ucak_rect.x -= ucak_hiz
        if ucak_rect.left <= 0:
            ucak_direction = 'right'

    #Uçak animasyon güncelleme
    suanki_zaman = pygame.time.get_ticks()
    if suanki_zaman - ucak_last_update > ucak_frame_interval:
        ucak_last_update = suanki_zaman
        ucak_frame_index = (ucak_frame_index + 1) % len(ucak_animasyon)
        
    now = pygame.time.get_ticks()
    if now - drop_timer > drop_interval:
        drop_timer = now
        drop_interval = random.randint(800, 1500)
        x = ucak_rect.centerx
        if random.random() < 0.7:
            drops.append(Heart(x, ucak_rect.bottom, speed=5))
        else:
            bomb_drop_sound.play()
            drops.append(Bomb(x, ucak_rect.bottom, speed=5))

    #Ekran çizimi
    screen.blit(background, (0, 0))
    
    #Uçak çizimi
    base_frame = ucak_animasyon[ucak_frame_index]
    if ucak_direction == 'left':
        frame = pygame.transform.flip(base_frame, True, False)
    else:
        frame = base_frame
    screen.blit(frame, ucak_rect)
    
    # Drop nesnelerini güncelleme, çizme ve patlama kontrolü yapma
    for drop in drops[:]:
        drop.update() 
        
        # Çarpışma algılama
        if drop.rect.colliderect(karakter_rect):
            if isinstance(drop, Heart):
                score += 5
                heart_count += 1
                heart_collect_sound.play()
                drops.remove(drop)
            elif isinstance(drop, Bomb):
                game_over_sound.play()
                running = False
                break
        
        drop.draw(screen)

        if isinstance(drop, Bomb):
            
            if not drop.exploding and drop.rect.bottom >= HEIGHT:
                bomb_explosion_sound.play()
                drop.explode()
                drop.frame_index = 0
                drop.last_update = pygame.time.get_ticks()
        
        # Patlama animasyonu bitince bombayı silme
            elif drop.exploding and drop.frame_index == len(drop.frames) - 1:
                drops.remove(drop)
        else:
            #Kalp yere düşünce silme
            if drop.rect.top > HEIGHT:
                drops.remove(drop)


    #Gölge çizme
    shadow_x = karakter_rect.centerx - shadow_width // 2
    shadow_y = karakter_rect.bottom - shadow_height // 2
    screen.blit(shadow_surf, (shadow_x, shadow_y))

    #Karakter animasyonunu zamanla ilerletme
    if velocity_x != 0:
        suanki_zaman = pygame.time.get_ticks()
        if suanki_zaman - son_guncelleme > frame_suresi:
            son_guncelleme = suanki_zaman
            frame_indeksi = (frame_indeksi + 1) % len(yuru_animasyon)
    else:
        frame_indeksi = 0 

    #Doğru listeden kareyi alma
    anim_list = yuru_animasyon_sag if direction == 'right' else yuru_animasyon_sol
    aktif_frame = anim_list[frame_indeksi]

    #Yöne göre doğru frameleri seçme
    if direction == 'right':
        aktif_frame = yuru_animasyon_sag[frame_indeksi]
    else:
        aktif_frame = yuru_animasyon_sol[frame_indeksi]

    hud_text = f"Puan: {score}   Kalpler: {heart_count}"
    hud_surf = font.render(hud_text, True, (255, 0, 0))
    screen.blit(hud_surf, (10, 10))

    #Karakteri çizme ve ekranı güncelleme
    screen.blit(aktif_frame, karakter_rect)
    pygame.display.flip()
    

# Game Over ekranı
bg = screen.copy()
small = pygame.transform.smoothscale(bg, (WIDTH//10, HEIGHT//10))
blurred = pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
screen.blit(blurred, (0, 0))

#Skor paneli
panel_w, panel_h = 400, 200
panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
panel.fill((30, 30, 30, 200)) 

#Son skor metnini oluşturma ve panelin ortasına yerleştirme
line1 = font.render("Oyun Bitti!", True, (255, 255, 255))
line2 = font.render(f"Skorunuz: {score}", True, (255, 255, 255))
line3 = font.render(f"Toplanan Kalp: {heart_count}", True, (255, 255, 255))

line1_rect = line1.get_rect(center=(panel_w//2, panel_h//2 - 30))
line2_rect = line2.get_rect(center=(panel_w//2, panel_h//2))
line3_rect = line3.get_rect(center=(panel_w//2, panel_h//2 + 30))

panel.blit(line1, line1_rect)
panel.blit(line2, line2_rect)
panel.blit(line3, line3_rect)

# Paneli ekranın tam ortasına yerleştirme
panel_rect = panel.get_rect(center=(WIDTH//2, HEIGHT//2))
screen.blit(panel, panel_rect)

pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                waiting = False 

    # FPS ayarlamak için
    clock.tick(60)
    
pygame.quit()


