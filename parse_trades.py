from bs4 import BeautifulSoup
import requests
import re

def download_html(url, filename='torgi_page.html'):
    """Скачивает HTML-страницу и сохраняет локально"""
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Страница сохранена в {filename}")
        return response.text
    except Exception as e:
        print(f"Ошибка при скачивании: {e}")
        return None

def parse_price(price_str):
    """Преобразует строку цены в число"""
    if not price_str:
        return 0
    # Удаляем все, кроме цифр и точки
    clean_price = re.sub(r'[^0-9.]', '', price_str)
    try:
        return float(clean_price)
    except:
        return 0

def parse_trades(html_content):
    """Парсит HTML и извлекает данные о лотах"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    lots = []
    table = soup.find('table', {'id': 'auction-table'})
    
    if not table:
        print("Таблица с лотами не найдена")
        return lots
    
    rows = table.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 7:  # Пропускаем строки без данных
            continue
            
        # Извлекаем данные
        name_cell = cells[1]
        price_cell = cells[5]
        
        link_tag = name_cell.find('a')
        if link_tag:
            name = link_tag.get_text(strip=True)
            link = 'https://torgi.org' + link_tag.get('href', '')
        else:
            continue
            
        price_text = price_cell.get_text(strip=True)
        price = parse_price(price_text)
        
        lots.append({
            'name': name,
            'price': price,
            'link': link
        })
    
    return lots

def filter_by_price(lots, min_price, max_price):
    """Фильтрует лоты по диапазону цен"""
    return [lot for lot in lots if min_price <= lot['price'] <= max_price]

def main():
    # URL сайта торгов
    url = 'https://torgi.org/index.php?class=Auction&action=List&mod=Open&AuctionType=All'
    
    # Скачиваем HTML
    print("Скачивание HTML-страницы...")
    html_content = download_html(url)
    
    if not html_content:
        print("Не удалось скачать страницу")
        return
    
    # Парсим данные
    print("Парсинг данных...")
    lots = parse_trades(html_content)
    
    if not lots:
        print("Лоты не найдены")
        return
    
    # Сортируем по убыванию цены
    lots_sorted = sorted(lots, key=lambda x: x['price'], reverse=True)
    
    print(f"\nНайдено лотов: {len(lots_sorted)}\n")
    
    # Запрашиваем диапазон цен
    try:
        min_price = float(input("Введите минимальную цену (руб.): "))
        max_price = float(input("Введите максимальную цену (руб.): "))
        
        # Фильтруем
        filtered_lots = filter_by_price(lots_sorted, min_price, max_price)
        
        print(f"\nЛоты в диапазоне от {min_price:,.2f} до {max_price:,.2f} руб.:\n")
        print("=" * 80)
        
        for i, lot in enumerate(filtered_lots, 1):
            print(f"{i}. {lot['name'][:70]}...")
            print(f"   Цена: {lot['price']:,.2f} руб.")
            print(f"   Ссылка: {lot['link']}")
            print("-" * 80)
        
        if not filtered_lots:
            print("Нет лотов в указанном диапазоне цен")
    
    except ValueError:
        print("Ошибка: введите корректные числа")
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")

if __name__ == '__main__':
    main()
