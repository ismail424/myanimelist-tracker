import requests, os, time, json, re, datetime
from deepdiff import DeepDiff

regex = re.compile(r"\['([^']+)'\]")

class User:
    def __init__(self, username):
        self.username = username
        self.url = f"https://myanimelist.net/animelist/{username}/load.json"
        
        # Path to the folder where the data will be saved
        full_path = os.path.realpath(__file__)
        app_dir = os.path.dirname(full_path)
        self.user_folder = os.path.join(app_dir, f"previous_data/{self.username}")
        self.create_folder()
    
    def check_if_user_exists(username: str):
        url = f"https://myanimelist.net/animelist/{username}/load.json"
        r = requests.get(url)
        if r.status_code == 200:
            return True
        return False     
    
    def create_folder(self):
        if os.path.exists(self.user_folder) != True:
            os.mkdir(self.user_folder)
 
    def get_data(self):
        r = requests.get(self.url)
        return r.json()
    
    def get_relevante_data(self):
        all_data = self.get_data()
        output = {}
        for anime in all_data:
            output[anime["anime_title"]] ={
                "anime_image_path": anime["anime_image_path"],
                "status": anime["status"],
                "num_watched_episodes": anime["num_watched_episodes"],
                "score": anime["score"]
            }
        return output
    
    def save_data(self):
        file_path = os.path.join(self.user_folder, f"old_data.json")
        current_time = time.time()
        now = datetime.datetime.now()
        readable_time = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "w") as f:
            f.write(json.dumps
                    (
                        {
                            "time": current_time,
                            "readable_time":readable_time, 
                            "data": self.get_relevante_data()
                        }
                    ))

    def load_data(self):
        file_path = os.path.join(self.user_folder, "old_data.json")
        with open(file_path, "r") as f:
            data = json.loads(f.read())
        return data["data"]

    def compare_data(self):
        new_data = self.get_relevante_data()
        old_data = self.load_data()

        output_obj = []
        ddiff = DeepDiff(old_data, new_data, ignore_order=True)
        if ddiff != {}:
            for key in list(ddiff.keys()):
                if key == "values_changed":
                    values_changed = ddiff['values_changed']  
                    for item in list(values_changed):
                        groups = regex.findall(item)

                        output_obj.append(
                            {
                                "anime_title" : groups[0],
                                "anime_img": new_data[groups[0]]["anime_image_path"],
                                "subject" : groups[-1],
                                **values_changed[item]
                            }
                        )

        return output_obj
                
        
    def get_anime_list_names(self):
        data = self.get_data()
        return [anime["anime_title"] for anime in data]



class DiscordUser:

    def __init__(self, username: str, discord_id: int):
        self.username = username
        self.discord_id = discord_id
        self.schema = {
                "username": self.username,
                "discord_id": self.discord_id
            }
        if self.check_if_exist() == False:
            self.add_user()
        
    def check_if_exist(self):
        for user in self.load_data():
            if user['username'] == self.username:
                return True
            
        return False
            
    def remove_user(self, username: str):
        data = self.load_data()
        for item in data:
            if self.username == username:
                data.remove(item)
        self.save_data(data)

    
    def load_data(self):
        with open("users.json", "r") as f:
            data = json.loads(f.read())
        return data
    
    def load():
        with open("users.json", "r") as f:
            data = json.loads(f.read())
        return data
    
    def add_user(self):
        data = self.load_data()
        data.append(self.schema)
        self.save_data(data)
        
    def save_data(self, data):
        with open("users.json", "w") as f:
            f.write(json.dumps(data))
        



