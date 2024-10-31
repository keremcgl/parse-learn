import requests
from urllib.parse import urljoin
import sys


# Bazı sitelerdeki mailto kısımları da link olarak geçiyor fakat onları https olarak algılamıyor. (http kontrolü eklendi)
# help linklerinde 403 yani forbidden alıyoruz. Bunu dead olarak yazdırıyoruz fakat forbidden şeklinde güncellenebilir.


# 2 argümandan az veya fazla alınıp alınmadığının kontrolü.
if len(sys.argv) != 2:
    sys.exit("python3 script.py <url>")

url = sys.argv[1]
response = requests.get(url)

links = set()
startpos = 0

while True:
    # Anchor etiketini buluyoruz.
    startpos = response.text.find("<a", startpos)
    if startpos == -1:
        break
    endpos = response.text.find(">", startpos)
    if endpos == -1:
        break

    # Anchor etiketi içinde href buluyoruz.
    href_start = response.text.find("href", startpos, endpos)
    if href_start == -1:
        startpos = endpos
        continue

    # href'ten sonraki eşittir işaretini kontrol ediyoruz. hreften sonra eşittir için boşluk bırakılıp bırakılmama durumunu kontrol için.
    equals_sign_pos = response.text.find("=", href_start, endpos)
    if equals_sign_pos == -1:
        startpos = endpos
        continue

    # Bağlantının başlangıç pozisyonunu belirlemek için eşittirin bir sağına gidiyoruz.
    link_start = equals_sign_pos + 1
    
    # Bağlantının yanındaki tırnak işaretlerinin konumunu buluyoruz. strip sayesinde tırnak öncesi boşlukları atlayıp bir sonraki karaktere bakabiliyoruz.
    quote_char = response.text[link_start].strip()
    if quote_char not in ('"', "'"):
        startpos = endpos
        continue
    # Tırnaktan sonraya geçip bağlantının sonunu bulmak için.
    link_start += 1
    link_end = response.text.find(quote_char, link_start)
    if link_end == -1:
        startpos = endpos
        continue

    # Bağlantı listeye ekleniyor.
    link = response.text[link_start:link_end].strip()
    if link:
        links.add(link)
    startpos = endpos



link_count = 0
for link in links:
    link_count += 1
    full_url = urljoin(url, link)
    
    # Başlangıcında http olmayan linkler alınmıyor. mailto kısımları da href kısmında bağlantı olarak yazıldığı için onları incelemiyoruz.
    
    if full_url[0:4] != "http":
    	continue
    	
    try:
        # Bağlantının durumunu kontrol etmek için requests.head kullanıyoruz.
        # allow_redirects eklenince redirect ile gidilen linkleri daha iyi kontrol edebiliyoruz.
        link_response = requests.head(full_url, allow_redirects=True)
        if link_response.status_code == 200:
            print(f"{link_count} - {full_url}  Active")	     
        else:
            print(f"{link_count} - {full_url}  Dead (Status: {link_response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"{link_count} - {full_url}  Error: {e}")


