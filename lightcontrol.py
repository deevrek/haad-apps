import appdaemon.appapi as appapi
import re
from fuzzywuzzy import fuzz

LIGHT_KEY={'minimum': 10,'maximum' : 100,'increase': 80, 'decrease': 20}

class LightControl(appapi.AppDaemon):

   
    def initialize(self):
        self.register_endpoint(self.api_call, "lights")
        
    def find_entity(self, entity, types,filter=''):
        entities={}
        for type in types:
            entities.update(self.get_state(type))
            
        best_score = 0
        best_entity = None
        for state in entities:
            try:
#                self.log(state)
                if state.split(".")[0] in types and re.search(filter,state):

                    score = fuzz.ratio(entity, entities[state]['attributes']['friendly_name'].lower())
                    if score > best_score:
                        best_score = score
                        best_entity = state
            except KeyError:
                pass
        return best_entity

    def api_call(self, data):
        intent = self.get_apiai_intent(data)
        parameters=data['result']['parameters']
        req_entity=parameters['Room']
        self.log("Requested entity: %s" % req_entity)
        entity=self.find_entity(req_entity,['light','group'])
        if parameters['OnOff'] == 'off':
            self.turn_off(entity)
            response=self.format_apiai_response(
                speech = "Turned off %s." % parameters['Room'])
            return response, 200
        else: #On or null
            ha_param={}
            if not parameters['color'] == '':
                ha_param.update({'color_name' : parameters['color']} )
            if not parameters['percentage'] == '':
                ha_param.update({'brightness_pct' : parameters['percentage'][:-1]} )
            if not parameters['DimAction'] == '':
                ha_param.update({'brightness_pct' : 
                                 LIGHT_KEY[parameters['DimAction']]} )
        response=self.format_apiai_response(
                speech = "In progress")
        print("entity: %s" % entity)
        print("ha_param: %s"% ha_param)
        self.turn_on(entity,**ha_param)
        return response, 200                    
