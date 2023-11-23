
##----------------------------------------------##
## QUERY / MATCH

def parse_and_execute(self, command):
  parts = command.split(maxsplit=2)
  action = parts[0]
  if action == "find":
      # Assuming format "find key in path"
      key, path = parts[1], parts[3]
      return self.find_key_in_path(key, path)
  elif action == "read":
      # Assuming format "read at path"
      path = parts[2]
      return self.read_at_path(path)
  elif action == "match":
      # Assuming format "match key in path"
      key, path = parts[1], parts[3]
      return self.match_key_in_list(key, path)
  elif action == "path_resolve":
      # Assuming format "path_resolve path"
      path = parts[1]
      return self.path_exists(path)
  else:
      raise ValueError("Invalid command action.")


##----------------------------------------------##


def path_exists(self, path):
  ssid_path = f"data.{self.active}.{path}"
  try:
      # Check if path exists
      resolved_value = self.data.get(ssid_path)
      return resolved_value is not None
  except Exception as e:
      warn(f"Error resolving path '{ssid_path}': {e}")
      return False


##----------------------------------------------##


def find_key_in_path(self, key, path):
  ssid_path = f"data.{self.active}.{path}"
  try:
      values_at_path = self.data.get(ssid_path)
      if key in values_at_path:
          return values_at_path[key]
      else:
          return None  # Or an appropriate message/value
  except Exception as e:
      warn(f"Failed to find key '{key}' at path '{ssid_path}': {e}")
      return None


##----------------------------------------------##

def read_at_path(self, path):
  ssid_path = f"data.{self.active}.{path}"
  try:
      return self.data.get(ssid_path)
  except Exception as e:
      warn(f"Failed to read data at path '{ssid_path}': {e}")
      return None


##----------------------------------------------##

def match_key_in_list(self, key, path):
  ssid_path = f"data.{self.active}.{path}"
  try:
      values_at_path = self.data.get(ssid_path)
      if not isinstance(values_at_path, list):
          raise TypeError("Data at specified path is not a list.")
      
      # Filter the list for objects containing the key
      matched_objects = [obj for obj in values_at_path if isinstance(obj, dict) and key in obj]
      return matched_objects
  except Exception as e:
      warn(f"Failed to match key '{key}' in list at path '{ssid_path}': {e}")
      return None



