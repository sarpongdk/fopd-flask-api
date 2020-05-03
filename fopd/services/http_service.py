import requests, datetime, json, time, os

TIMEOUT = 600213
TOOMANYREDIRECTS = 31321


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

   def _get_credentials(self):
      """return default login credentials"""
      return "{\n\t\"username\": \"sludev\",\n\t\"password\": \"football76fire\"\n}"

   def login(self, url = LOGIN_URL, credentials = None):
      #self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
      if not credentials:
         credentials = self._get_credentials()

      header = {
         "Content-Type": "application/x-www-form-urlencoded"
      }

      try:
         response = self.session.post(url, data = credentials, headers = header)
         self.cookieJar = self.session.cookies
         # print(self.cookieJar.get_dict())
         return {
            'session': self.cookieJar.get_dict().get('session'),
            'logged_in': response.json()['logged_in'],
            'organizations': response.json()['organizations']
         }
      except requests.exceptions.Timeout as e:
         print(e)
         return TIMEOUT
      except requests.exceptions.TooManyRedirects as ex:
         print(ex)
         return TOOMANYREDIRECTS
      except requests.exceptions.RequestException as exy:
         print(exy)
         return None
      

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
      return response.json(), response.status_code, response.reason

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
   res, status_code, reason = http.getObservations("8a0118e3-a6bf-4ace-85c4-a7c824da3f0c", "2020-01-23", "2020-01-24")
   print(res[0], status_code, reason)
   #http.getImage(deviceId = "8a0118e3-a6bf-4ace-85c4-a7c824da3f0c", ts = 1583192407261)
   #print('Session cookie =', http.login())
