'''
Created on 6.11.2014

@author: mvi
'''

import logging

import json
import requests
import urllib
import urllib2
import pylons.config as config

# doc https://team.eea.sk/wiki/pages/viewpage.action?pageId=108660564
# TODO /pipelines/<pipeline_id>/schedules/
# TODO /pipelines/<pipeline_id>/schedules/<id>
# TODO /pipelines/<pipeline_id>/schedules/<schedule_id>
# TODO GET /pipelines/<pipeline_id>/executions
# TODO /pipelines/<pipeline_id>/executions/<execution_id>
# TODO /pipelines/<pipeline_id>/executions
# TODO /pipelines/<pipeline_id>/executions/<execution_id>/events

# TODO this class to ckancommons

TIMEOUT =  int(config.get('odn.uv.timeout', 5))

log = logging.getLogger('ckanext')

class UVRestAPIWrapper():
    
    def __init__(self, uv_url):
        assert uv_url
        self.url = uv_url
        

    def _send_request(self, uv_url):
        """Sends GET request
        """
        assert uv_url
        log.debug("uv_helper sending request to: {0}".format(uv_url))
        request = urllib2.Request(uv_url)
        # Make the HTTP request.
        response = urllib2.urlopen(request, timeout=TIMEOUT)
        assert response.code == 200
        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        return response_dict


    def _send_request_with_data(self, uv_url, data_string):
        """Sends POST request with JSON data
        """
        print data_string
        assert uv_url
        headers = {'content-type': 'application/json'}
        response = requests.post(uv_url, data=data_string, headers=headers)
        if response.status_code != 200:
            raise Exception("Error sending request to {0}: {1}".format(uv_url, response.text))
        response_dict = response.json()
        return response_dict
    
    
    def get_pipelines(self):
        uv_url = '{0}/pipelines'.format(self.url)
        return self._send_request(uv_url)
    
    
    def get_pipeline_by_id(self, pipe_id):
        assert pipe_id
        uv_url = '{0}/pipelines/{1}'.format(self.url, pipe_id)
        return self._send_request(uv_url)


    def create_pipeline(self, name, description):
        uv_url = '{0}/pipelines'.format(self.url)
        data = {'name':name, 'description': description}
        return self._send_request_with_data(uv_url, json.dumps(data))
    
    
    def create_copy_pipeline(self, pipe_to_copy, name, description):
        assert pipe_to_copy
        uv_url = '{0}/pipelines/{1}/clones'.format(self.url, pipe_to_copy)
        data = {'name':name, 'description': description}
        return self._send_request_with_data(uv_url, json.dumps(data))


    def get_last_finished_execution(self, pipe_id):
        assert pipe_id
        uv_url = '{0}/pipelines/{1}/executions/last'.format(self.url, pipe_id)
        try:
            execution = self._send_request(uv_url)
            return execution
        except urllib2.HTTPError, err:
            if err.code == 404:
                return None
            else:
                raise err


    def get_next_execution_info(self, pipe_id):
        """ Return information about next execution
        (schedule_id, next_execution_time, execution_status)
        """
        assert pipe_id
        # find pending execution
        uv_url = '{0}/pipelines/{1}/executions/pending'.format(self.url, pipe_id)
        executions = self._send_request(uv_url)
        if executions and len(executions) > 0:
            execution = executions.pop(0)
            return execution['schedule'], execution['lastChange'], execution['status']
        
        # if there is no pending execution, get next execution from schedules
        uv_url = "{0}/pipelines/{1}/schedules/~all/scheduledexecutions".format(self.url, pipe_id)
        schedules = self._send_request(uv_url)
        if schedules and len(schedules) > 0:
            schedule = schedules.pop(0)
            return schedule['schedule'], schedule['start'], None
        
        return None, None, None 
    

    def execute_now(self, pipe_id, is_debugging=False):
        assert pipe_id
        uv_url = '{0}/pipelines/{1}/executions/'.format(self.url, pipe_id)
        data = {'debugging':is_debugging}
        return self._send_request_with_data(uv_url, json.dumps(data))

