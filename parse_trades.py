from bs4 import BeautifulSoup
import requests


def parse_price(price_str):
    if not price_str:
        return 0
    clean = ''.join(c for c in price_str if c.isdigit() or c == '.')
    return float(clean) if clean else 0


def parse_trades(html):
    soup = BeautifulSoup(html, 'html.parser')
    lots = []
    table = soup.find('table', {'id': 'auction-table'})
    
    if not table:
        return lots
    
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
        
        link = cells[1].find('a')
        if not link:
            continue
        
        lots.append({
            'name': link.text.strip(),
            'price': parse_price(cells[5].text.strip()),
            'link': 'https://torgi.org' + link.get('href', '')
        })
    
    return lots


def main():
    url = 'https://torgi.org/index.php?class=Auction&action=List&mod=Open&AuctionType=All'
    
    print("Скачивание...")
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        with open('torgi_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Сохранено в torgi_page.html")
    except Exception as e:
        print(f"Ошибка: {e}")
        return
    
    lots = sorted(parse_trades(response.text), key=lambda x: x['price'], reverse=True)
    print(f"\nНайдено: {len(lots)} лотов\n")
    
    try:
        min_price = float(input("Мин. цена: "))
        max_price = float(input("Макс. цена: "))
        filtered = [lot for lot in lots if min_price <= lot['price'] <= max_price]
        
        print(f"\n{'='*80}")
        for i, lot in enumerate(filtered, 1):
            print(f"{i}. {lot['name'][:70]}")
            print(f"   {lot['price']:,.0f} руб. | {lot['link']}")
            print(f"{'-'*80}")
        
        if not filtered:
            print("Нет лотов в диапазоне")
    except:
        print("Ошибка ввода")


if __name__ == '__main__':
    main()
