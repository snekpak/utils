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



def smart_merge(d1,d2):
  this = {} | d1
  this.update({k: v for k, v in d2.items() if v is not None})
  return this



def reserved(fx):
  def wrapper(self, k, *args, **kwargs):
      if k.startswith('_'):
          raise ValueError("Key is reserved. Public access not allowed.")
      return fx(self, k, *args, **kwargs)
  return wrapper



def unpack_line(line, num_items):
    items = line.split()
    padded_items = items + [None] * (num_items - len(items))
    return padded_items[:num_items]

def find_kbv(ref, term):
    for key, values in ref.items():
      if term in values:
        return key
    return None 

def get_nested_ref(obj, path):
  els = path.replace('[', '.[').split('.')  # Splitting on '.' after adding '.' before '['
  for i, ref in enumerate(els):
      if ref.startswith('['):
          # Handle both string keys and list indices within square brackets
          if ref.startswith("['") and ref.endswith("']"):
              key = ref[2:-2]  # Extracting string key without brackets and quotes
          else:
              key = int(ref[1:-1])  # Extracting integer index without brackets

          if i == len(els) - 1:
              return obj, key
          obj = obj[key] if isinstance(obj, list) else obj[key]
      else:
          if i == len(els) - 1:
              return obj, ref
          obj = obj[ref]

  return None, None
