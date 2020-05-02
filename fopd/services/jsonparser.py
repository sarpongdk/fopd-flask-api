import json

from fopd.services.http_service import HttpService

class JsonParser(object):
   def __init__(self):
      pass

   @staticmethod
   def parse(resJson):
      observations = []
      # data = json.load(fileObj)
      for parsed in resJson:
         deviceId = parsed['device_id']
         deviceName = parsed['device_name']
         timestamp = parsed['ts']
         subject = parsed['subject']
         subjectId = parsed['subject_location_id']
         attribute = parsed['attribute']
         value = parsed['value']
         units = parsed['units']
      #    observation = Observation(deviceId, timestamp, subject, attribute, value, units, deviceName, subjectId)
      #    observations.append(observation)
      #    #print(observation)
      # return observations

      
if __name__ == "__main__":
   http = HttpService()
   deviceId = "8a0118e3-a6bf-4ace-85c4-a7c824da3f0c" 
   startDate = "2020-01-23"
   endDate = "2020-01-24"
   res = http.getObservations(deviceId, startDate, endDate) 
   JsonParser.parse(res)

