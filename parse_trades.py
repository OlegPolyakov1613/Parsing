from bs4 import BeautifulSoup
import requests


def download_html(url, filename='torgi_page.html'):
    """Скачивает HTML-страницу"""
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Страница сохранена в {filename}")
        return response.text
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def parse_price(price_str):
    """Преобразует строку цены в число"""
    if not price_str:
        return 0
    # Оставляем только цифры
    clean_price = ''.join(c for c in price_str if c.isdigit() or c == '.')
    return float(clean_price) if clean_price else 0


def parse_trades(html_content):
    """Парсит HTML и извлекает данные о лотах"""
    soup = BeautifulSoup(html_content, 'html.parser')
    lots = []
    
    table = soup.find('table', {'id': 'auction-table'})
    if not table:
        print("Таблица не найдена")
        return lots
    
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
        
        link_tag = cells[1].find('a')
        if not link_tag:
            continue
        
        name = link_tag.get_text(strip=True)
        link = 'https://torgi.org' + link_tag.get('href', '')
        price = parse_price(cells[5].get_text(strip=True))
        
        lots.append({'name': name, 'price': price, 'link': link})
    
    return lots


def filter_by_price(lots, min_price, max_price):
    """Фильтрует лоты по цене"""
    return [lot for lot in lots if min_price <= lot['price'] <= max_price]


def main():
    url = 'https://torgi.org/index.php?class=Auction&action=List&mod=Open&AuctionType=All'
    
    # Скачиваем HTML
    print("Скачивание страницы...")
    html = download_html(url)
    if not html:
        return
    
    # Парсим
    print("Парсинг данных...")
    lots = parse_trades(html)
    if not lots:
        print("Лоты не найдены")
        return
    
    # Сортируем по убыванию цены
    lots = sorted(lots, key=lambda x: x['price'], reverse=True)
    print(f"\nНайдено лотов: {len(lots)}\n")
    
    # Фильтруем
    try:
        min_price = float(input("Минимальная цена: "))
        max_price = float(input("Максимальная цена: "))
        
        filtered = filter_by_price(lots, min_price, max_price)
        
        print(f"\nЛоты от {min_price:,.0f} до {max_price:,.0f} руб.:\n")
        print("=" * 80)
        
        for i, lot in enumerate(filtered, 1):
            print(f"{i}. {lot['name'][:70]}")
            print(f"   Цена: {lot['price']:,.0f} руб.")
            print(f"   Ссылка: {lot['link']}")
            print("-" * 80)
        
        if not filtered:
            print("Нет лотов в диапазоне")
    
    except ValueError:
        print("Ошибка: введите числа")
    except KeyboardInterrupt:
        print("\nПрервано")


if __name__ == '__main__':
    main()
