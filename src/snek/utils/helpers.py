import os

def dump_dict(items):
  for key,value in items.items():
    print(f"  {key} -> {value}")
        


def file_in_dirs(file,search_list):
  exists = os.path.exists
  if exists(file):
    return file
  else:
    for path in search_list:
      abs_file = f'{path}/{file}'
      if exists(abs_file):
        return abs_file
  return None

# dict{ a,b,c,d } -> dict{ a,d }
def reduce_dict(dict, exclude_keys):
  return {key: dict[key] for key in dict if key not in exclude_keys}

# flat file splitting of values with k:v,k:v,k:v 
def unzip_pairs(pairs_list):
  ref = pairs_list.split(",")
  this = {k: v for k, v in (pair.split(":") for pair in ref)}
  return this