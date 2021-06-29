import json
from sweeper import DCSweeper

if __name__ == '__main__':
    with open('const.json', encoding='utf8') as const_file:
        const = json.load(const_file)
        target_galleries = const['target_galleries']
        galleries = const['galleries']

    for target_gallery in target_galleries:
        DCSweeper(target_gallery, galleries[target_gallery]).start_sweeping()