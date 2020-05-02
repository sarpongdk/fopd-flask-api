import requests, datetime, json, time, os

class HttpService(object):
   LOGIN_URL = "https://fop1.urbanspacefarms.com:5000/api/login"
   LOGOUT_URL = "https://fop1.urbanspacefarms.com:5000/api/logout"
   OBSERVATIONS_URL = "https://fop1.urbanspacefarms.com:5000/api/get_data_json/%s/%s/%s"
   IMAGE_URL = "https://fop1.urbanspacefarms.com:5000/api/image/%s?ts=%d"
   ENCODING = "utf-8"
   FILE_PATH = os.path.join(".")

   def __init__(self):
      self.session = requests.Session()
      self.cookieJar = None
      self.login()

   def login(self, url = LOGIN_URL):
      #self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
      credentials = "{\n\t\"username\": \"sludev\",\n\t\"password\": \"football76fire\"\n}"
      header = {
         "Content-Type": "application/x-www-form-urlencoded"
      }
      response = self.session.post(url, data = credentials, headers = header)
      self.cookieJar = self.session.cookies
      #print(self.cookieJar.get_dict())

   def _validateDate(self, startDate, endDate):
      start = startDate.split("-")
      if len(start[0]) != 4:
         return False

      try:
         month = int(start[1])
         day = int(start[2])
      except ValueError:
         return False

      if len(start[1]) != 2 or month > 12 or month < 0: 
         return False
      
      if day < 0 or day > 31:
         return False

      return True

   def getObservations(self, deviceId, startDate = None, endDate = None,  url = OBSERVATIONS_URL):
      if not deviceId: # illegal
         print("No deviceId in getObservations")
         return None
      
      if not self._validateDate(startDate, endDate):
         print("Invalid date")
         return None

      # if no dates provided, choose between yesterday and today
      if not startDate: 
         startDate = datetime.today().strftime('%Y-%m-%d')
         print(startDate)
      if not endDate:
         endDate = datetime.strftime(datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
         print(endDate)

      header = { 
         "Content-Type": "application/json"
          #   "User-Agent": "curl/7.61.0"
      }   

      payload = {}
      url = url % (deviceId, startDate, endDate)
      response = self.session.get(url, data = payload, cookies = self.cookieJar, headers = header)
      #print(response)
      response.encoding = self.ENCODING
      return response.json()

   def getImage(self, deviceId, ts = None, url = IMAGE_URL, filename = 'testfile.png'):
      if not ts:
         ts = int(time.time())
         print(ts)
      
      url = url % (deviceId, ts)
      response = self.session.get(url, cookies = self.cookieJar, stream = True)
      path = os.path.join(self.FILE_PATH, filename)

      with open(path, "wb") as f:
         for chunk in response:
            f.write(chunk)
      return FILE_PATH

if __name__ == "__main__":
   http = HttpService()
   #http.login()
   #res = http.getObservations("8a0118e3-a6bf-4ace-85c4-a7c824da3f0c", "2020-01-23", "2020-01-24")
   http.getImage(deviceId = "8a0118e3-a6bf-4ace-85c4-a7c824da3f0c", ts = 1583192407261)
