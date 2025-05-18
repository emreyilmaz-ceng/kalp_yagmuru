**Kalp Yağmuru**
Ekrandan düşen kalpleri toplayıp puan kazandığın, bombalardan kaçtığın refleks tabanlı bir Python/Pygame oyunudur.

Oyun Mekanikleri
Uçak ekranda sağa-sola hareket ederek rastgele kalp veya bomba bırakır.

Kalp topladıkça +5 puan kazanırsınız, topladığınız kalp sayısı artar.

Bomba ile temas ederseniz patlama efekti çalar ve oyun biter.

Puan ve toplanan kalp sayısı ekranın sol üstünde gösterilir.

Kontroller
Tuş	İşlev
→ / ←	Karakteri sağa/sola hareket ettir
R	Oyun bittiğinde yeniden başlat
Esc	Oyunu kapat

Kod Mimarisi
resource_path()
PyInstaller ile derlenmiş exe içinden kaynaklara erişimi sağlar.

Sınıflar

Drop — Ortak düşen nesne mantığı

Heart — Tek frame’li kalp

Bomb — Normal ve patlama animasyonlu bomba

Oyun Döngüsü (while running:)

Olay yönetimi (klavye, pencere kapatma)

Karakter ve uçak hareketleri

Drop’ların spawn, güncelleme ve çarpışma kontrolü

Çizim sırası: arka plan → uçak → drop nesneleri → karakter → HUD → flip
