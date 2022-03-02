from operator import le
import json

file = open('MitreData.json')
obj_list = []
dict = {}

for line in file:
    obj_list.append(eval(line))

new_list = []
for item in obj_list:
    if(len(item['tactics'])>1):
        print(item['tactics'])
        print(type(item['tactics']))
        for tactic in item['tactics']:
            print(tactic)
            dict = item
            dict['tactics'] = tactic
            print(dict['tactics'])
            new_list.append(dict)
            # print(tactic)
    else:
        print(item['tactics'])
        dict = item
        dict['tactics'] = item['tactics'][0]
        new_list.append(dict)
    
for item in new_list:
     print(item['tactics'])

# with open("MITREjsonAll.json", "w") as outfile:
#     json.dump(obj_list, outfile)

# df = pd.DataFrame(obj_list)
# df.head()
# df.keys()
