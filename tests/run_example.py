import main
from src.dependencies import wiki_loader

article = wiki_loader.get("ispolzuet-po-naznacheniyu-dekorator-property-v-svoem-kode")
print(article)

article = wiki_loader.find("skill", "Пишет запросы с арифметическими действиями")
print(article)
