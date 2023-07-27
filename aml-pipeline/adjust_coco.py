import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser('Adjust coco_url information in coco_info.json')
    parser.add_argument('--blob_storage', '-s', type=str, default=None, help='Name of storage for AML dataset', required=True)
    return parser.parse_args()

def adjust_coco_url(blob_storage):
    data = json.load(open("./data/cats_dogs/coco_info.json"))
    for i in data['images']:
        i['coco_url'] = i['coco_url'].replace('playground7463417589', blob_storage)  
    with open("./data/cats_dogs/coco_info.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=2, separators=(',', ':'), default=str)

def main():
    args = parse_args()
    blob_storage = args.blob_storage
    adjust_coco_url(blob_storage)

if __name__ == '__main__':
    main()
