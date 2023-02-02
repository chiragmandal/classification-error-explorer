import json

# json_path = '/data/imagenet/imagenet_class_index.json'
json_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/index_mappings.json'
with open(json_path) as f:
    data = json.load(f)
    # print(type(data))

print(data)
print(data.get('n01440764'))