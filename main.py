import pygame
import sys
import random

pygame.init()

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

# Gölge yüzeyi
shadow_width  = frame_width
shadow_height = frame_height // 4
shadow_surf   = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect())

# Uçak animasyonu ve hareket ayarları 
ucak_animasyon = [
    pygame.image.load("ucak/ucak1.png").convert_alpha(),
    pygame.image.load("ucak/ucak2.png").convert_alpha()
]

scale_factor = 0.35 # Uçak boyutu

for i, surf in enumerate(ucak_animasyon):
    w, h = surf.get_size()
    ucak_animasyon[i] = pygame.transform.scale(
        surf,
        (int(w * scale_factor), int(h * scale_factor))
    )

ucak_frame_index    = 0
ucak_frame_interval = 150 
ucak_last_update    = pygame.time.get_ticks()

ucak_rect       = ucak_animasyon[0].get_rect(topleft=(0, 20)) 
ucak_hiz        = 3
ucak_direction  = 'right'                                      

# Oyun döngüsü
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Tuşa basıldığında hızı ve yönü ayarlama
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

    #  Karakteri hareket ettirme
    karakter_rect.x += velocity_x
    
    # Yatay pencere sınırı kontrolü
    karakter_rect.x = max(0, min(WIDTH - frame_width, karakter_rect.x))
    
    #Uçak hareketi (sağa–sola gidip gelecek)
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

    #Ekran çizimi
    screen.blit(background, (0, 0))
    
    #Uçak çizimi
    base_frame = ucak_animasyon[ucak_frame_index]
    if ucak_direction == 'left':
        frame = pygame.transform.flip(base_frame, True, False)
    else:
        frame = base_frame
    screen.blit(frame, ucak_rect)

    #Gölge çizme
    shadow_x = karakter_rect.centerx - shadow_width // 2
    shadow_y = karakter_rect.bottom - shadow_height // 2
    screen.blit(shadow_surf, (shadow_x, shadow_y))

    #Karakter animasyonunu zamanla ilerletme (sadece hareketliyken)
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

    #Karakteri çizme ve ekranı güncelleme
    screen.blit(aktif_frame, karakter_rect)
    pygame.display.flip()

pygame.quit()
sys.exit()
