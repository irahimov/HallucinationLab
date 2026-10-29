# holdout2: 14 uyğunsuzluğun yoxlanması

Bu fayl hakimin cavabına baxıldıqdan SONRA yazılıb. Ona görə bu, müstəqil yoxlama deyil, müəllifin ilkin oxunuşudur.
Etiketlər (`tests/data/holdout2.jsonl`) hələ dəyişdirilməyib.

| id | müəllif etiketi | hakim | kontekst dəlili | ilkin qənaət |
|---|---|---|---|---|
| m01 | SUPPORTED | CONTRADICTED | ilk 24 saat məbləğ çıxarmaq olmur | hakim düzgün |
| m05 | SUPPORTED | CONTRADICTED | premium yalnız illik ödənişlə | hakim düzgün |
| m07 | CONTRADICTED | SUPPORTED | 1.5% konversiya haqqı tutulur | hakim düzgün |
| m08 | SUPPORTED | CONTRADICTED | konversiya yalnız onlayn ödənişlərdən | hakim düzgün |
| m09 | UNSUPPORTED | SUPPORTED | məzənnə rəsmi kursla hesablanır | hakim düzgün |
| m10 | UNSUPPORTED | SUPPORTED | 60 gün ərzində təqdim etməlidir | hakim düzgün |
| m11 | SUPPORTED | CONTRADICTED | onlayn və ya yazılı ərizə ilə | hakim düzgün |
| m12 | CONTRADICTED | SUPPORTED | 30 günə qədər uzana bilər | hakim düzgün |
| m13 | UNSUPPORTED | SUPPORTED | hər 1000 AZN-ə 1 bonus xal | hakim düzgün |
| m14 | SUPPORTED | CONTRADICTED | nağd pula çevrilə bilməz | hakim düzgün |
| m15 | CONTRADICTED | SUPPORTED | bir il ərzində yığılır | hakim düzgün |
| m16 | UNSUPPORTED | SUPPORTED | 5 il saxlayır | hakim düzgün |
| m18 | UNSUPPORTED | SUPPORTED | tələblərinə uyğun müəyyən edilib | hakim düzgün |
| m20 | UNSUPPORTED | CONTRADICTED | heç bir komissiya tutulmur | hakim düzgün |

Ümumi nəticə: 14 uyğunsuzluğun hamısında ilkin oxunuş hakimin tərəfindədir. Bu, müəllifin etiketlərinin səhv ola biləcəyini göstərir.

Açıq məsələlər:
- Bu oxunuş müəllifindir. Ölçünün etibarı üçün kor (blind) ikinci etiketləyici lazımdır: o, hakimin cavabını görmədən etiketləsin.
- Düzəldilmiş etiketlərlə nəticə (v2) yalnız ikinci etiketləyici ilə razılaşdıqdan sonra əsas nəticə kimi göstərilə bilər.
- Əsas nəticə 0.30 olaraq qalır. Qeyd: bu rəqəm dəqiq ölçüdür, amma etiketlərin keyfiyyətindən asılıdır.
