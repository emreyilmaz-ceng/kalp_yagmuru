import pygame
import sys

# Başlat
pygame.init()

# Ekran boyutu ve pencere
WIDTH, HEIGHT = 905, 660
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kalp Yağmuru")

# FPS ayarı
clock = pygame.time.Clock()

# Arka plan yükle
background = pygame.image.load("arkaplan/arkaplan.png")

# Karakter yükleme ve animasyon ayarları
sprite_sheet = pygame.image.load("karakter/karakter.png").convert_alpha()
columns, rows = 9, 3
frame_width  = sprite_sheet.get_width()  // columns
frame_height = sprite_sheet.get_height() // rows

def get_frame(row, col):
    x, y = (col-1)*frame_width, (row-1)*frame_height
    return sprite_sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))

# Kullanacağım frameler
yuru_animasyon  = [
    get_frame(1, 1),
    get_frame(2, 2),
    get_frame(2, 1)
]

# Animasyon 
frame_indeksi   = 0
frame_suresi    = 150                    
son_guncelleme  = pygame.time.get_ticks()

# Karakter dikdörtgeni
karakter        = yuru_animasyon[0]
karakter_rect   = karakter.get_rect()
karakter_rect.midbottom = (WIDTH//2, HEIGHT-10)


# Hız ve hareket için değişkenler 
hiz             = 5      # Piksel/frame hızı (60 FPS için saniyeye≈300 px)
velocity_x      = 0      # Anlık x-yönlü hız
direction       = 'right'# 'right' veya 'left'

# Yürüyüş animasyonları iki yönlü
yuru_animasyon_sag = yuru_animasyon
yuru_animasyon_sol = [pygame.transform.flip(frm, True, False) for frm in yuru_animasyon]
# ────────────────────────────────────────────────

# Gölge yüzeyi
shadow_width  = frame_width
shadow_height = frame_height // 4
shadow_surf   = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect())


# Oyun döngüsü
running = True
while running:
    clock.tick(60)  # 60 FPS

    #  Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Tuşa basıldığında hızı ve yönü ayarla
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                velocity_x = hiz
                direction  = 'right'
            elif event.key == pygame.K_LEFT:
                velocity_x = -hiz
                direction  = 'left'

        # Tuş bırakıldığında dur
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                velocity_x = 0

    #  Karakteri hareket ettirme
    karakter_rect.x += velocity_x
    
    # Yatay sınır kontrolü
    karakter_rect.x = max(0, min(WIDTH - frame_width, karakter_rect.x))
    

    #  Ekran çizimi
    screen.blit(background, (0, 0))
       
    # Gölge çizme
    shadow_x = karakter_rect.centerx - shadow_width // 2
    shadow_y = karakter_rect.bottom - shadow_height // 2
    screen.blit(shadow_surf, (shadow_x, shadow_y))


    #  Animasyonu zamanla ilerlet (sadece hareketliyken)
    if velocity_x != 0:
        suanki_zaman = pygame.time.get_ticks()
        if suanki_zaman - son_guncelleme > frame_suresi:
            son_guncelleme = suanki_zaman
            frame_indeksi = (frame_indeksi + 1) % len(yuru_animasyon)
    else:
        frame_indeksi = 0  # Tuş yoksa 1. karede sabit dur

    #  Doğru listeden kareyi al
    anim_list = yuru_animasyon_sag if direction == 'right' else yuru_animasyon_sol
    aktif_frame = anim_list[frame_indeksi]

    #  Karakteri çiz ve ekranı güncelle
    screen.blit(aktif_frame, karakter_rect)
    pygame.display.flip()


    #  Yöne göre doğru frameleri seçtik
    if direction == 'right':
        aktif_frame = yuru_animasyon_sag[frame_indeksi]
    else:
        aktif_frame = yuru_animasyon_sol[frame_indeksi]

    #  Karakteri çiz ve ekranı güncelle
    screen.blit(aktif_frame, karakter_rect)
    pygame.display.flip()



# Çıkış
pygame.quit()
sys.exit()
