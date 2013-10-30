#!/usr/local/bin/python3

# -*- coding: utf-8 -*-
# Profile change sample to use with the D2LValence package to demo a simple
# data update posted back to the server.
#
# Copyright (c) 2012 Desire2Learn Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the license at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

## standard library imports
import os
import urllib.parse
import json

## third-party package imports: You need these packages, and you can get them from PyPi
import bottle
import requests

## D2L package imports: these obviously need to be in your package path, either
## installed with pip, or using this code:
# import sys
# sys.path.append('/path/to/where/you/unzipped/D2LValence')
import d2lvalence.auth as d2lauth
import d2lvalence.data as d2ldata
import d2lvalence.service as d2lservice

##
## Some useful state to maintain as default configuration data
##

# Execution dir to find script file
_dir = os.getcwd()
with open(os.path.join(os.getcwd(),'sample.js'),'r') as _f:
    _script = _f.read()

# Default App's D2L-provided credentials
#   app_id -- default App ID as provided by D2L
#   app_key -- default App Key as provided by D2L
#   host   -- default host for the web-app
#   port   -- default port number for the web-app
#   scheme -- the default protocol to use for user <--> web-app interaction
#   lms_host -- hostname for the back-end LMS
#   lms_port -- port number for the back-end LMS
#   encrypt_requests -- use HTTPs by preference when making API calls to the LMS
#   lms_ver -- product component API versions to call
_default_app_valence = { 'app_id': 'G9nUpvbZQyiPrk3um2YAkQ',
                         'app_key': 'ybZu7fm_JKJTFwKEHfoZ7Q',
                         'host': 'localhost',
                         'port': '8080',
                         'scheme': 'HTTP',
                         'lms_host': 'valence.desire2learn.com',
                         'lms_port': '443',
                         'encrypt_requests': True,
                         'lms_ver': {'lp':'1.0','le':'1.0','ep':'2.0'}
                         }

# set _default_app to the environment to test against
_default_app = _default_app_valence

# Default LMS ID values for enrollment roles, and org structure roles needed
# by this example -- these may or may not be different for the particular back-end
# LMS, and they might not be values that are visible to the calling user-context.
# valence
# _d2l_ids = { 'student_role': 78,
#             'course_offering': 3 }
# valence fusion instance
_d2l_ids = { 'student_role': 106,
             'course_offering': 3 }


# Global state for the application and current user contexts. These starts out
# as empty. In them, the active state for the app and user contexts, including
# the app and user context objects themselves.
_app_context = {}
_user_context = {}

##
## Course grade-list structure we can use to house the processed data
##
class CourseGradeList():
    def __init__(self,d2lid,course_name='',course_code=''):
        self.props = { 'd2lId': d2lid,
                       'CourseName': course_name,
                       'CourseCode': course_code,
                       'Students': {} }

    def __repr__(self):
        return str(self.props)

    def as_json(self):
        return json.dumps(self.props)

    def addupdate_student(self,d2lid, name='', id='', grade=''):
        self.props['Students'][d2lid]={'Name': name,
                                       'StudentID': id,
                                       'Grade': grade }
##
## Bottle app instance used to handle user-->web-app interaction; check Bottle's
## docs for an explanation of how the handler code below works.
##
app = bottle.Bottle()

##
## HTML page boilerplate for building the app's UI
##
_page_header = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Desire2Learn Auth SDK Sample</title>
	<style type = "text/css">
		table.plain
		{{
		  border-color: transparent;
		  border-collapse: collapse;
		}}

		table td.plain
		{{
		  padding: 5px;
		  border-color: transparent;
		}}

		table th.plain
		{{
		  padding: 6px 5px;
		  text-align: left;
		  border-color: transparent;
		}}

		tr:hover
		{{
			background-color: transparent !important;
		}}
	</style>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript">{script}</script></head><body>'''.format(script=_script)

_page_body = '''
	<form id="configForm" method="post">
        <table>
            <tr>
                <td><h4>Host: </h4></td>
                <td><input id="hostField" name="hostField" type="text" size=30 value="{host}" /></td>
                <td><h4>Port:</h4></td>
                <td><input id="portField" name="portField" type="text" size=3 value="{port}" /></td>
            </tr>
            <tr>
                <td><h4>App ID:</h4></td>
                <td><input id="appIDField" name="appIDField" type="text" size=30 value="{app_id}" /></td>
                <td><h4>App Key:</h4></td>
                <td><input id="appKeyField" name="appKeyField" type="text" size=30 value = "{app_key}" /></td>
            </tr>
    		<tr>
                <td><h4>User ID:</h4></td>
                <td><input id="userIDField" type="text" size=30  value="{user_id}" /></td>
                <td><h4>User Key:</h4></td>
                <td><input id="userKeyField" type="text" size=30 value="{user_key}" /></td>
            </tr>
        </table>
        <input type="submit" value="Authenticate" /> Note: to authenticate against the test server, you can user username "sampleapiuser" and password "Tisabiiif".
	</form><br /><br />
    <hr />

    <table style="float:left;" class = "plain">
        <tr class = "plain">
            <td class = "plain">
                <input id="getGradeList" type="button" value="Get Final Grades" style="float:right" onclick="getGradeList()" /><br /><br />
                <input id="clearButton" type="button" value="Clear" style = "float:right" onclick = "clearTextArea()" />
            </td>
            <td class = "plain">
                <span id = "resultHeading" style = "clear:both;float:left;color: black;" ></span>
                <span id = "result" style = "clear:both;float:left;color: black;text-align:left" ></span>
            </td>
        </tr>
    </table>

</body>
</html>
'''
_page_footer = ''' </body></html>'''

##
## Main form for web-app's UI, divided into a GET handler and a POST handler
##
@app.get('/start')
def start_form():
    global _app_context, _user_context

    user_id = ''
    user_key = ''
    app_id = _default_app['app_id']
    app_key = _default_app['app_key']
    lms_host = _default_app['lms_host']
    lms_port = _default_app['lms_port']
    
    if 'ac' in _app_context:
        app_id = _app_context['ac'].app_id
        app_key = _app_context['ac'].app_key
        lms_host = _app_context['lms_host']
        lms_port = _app_context['lms_port']

    if 'uc' in _user_context:
        user_id = _user_context['user_id']
        user_key = _user_context['user_key']
    elif 'ac' in _app_context:
        uc = _app_context['ac'].create_user_context( result_uri=bottle.request.url,
                                                     host=_app_context['lms_host'],
                                                     encrypt_requests=_app_context['encrypt_requests'])
        _user_context.update(uc.get_context_properties())
        _user_context['uc']=uc
        user_id = _user_context['user_id']
        user_key = _user_context['user_key']
        bottle.redirect('/start')
        
    body = _page_body.format(host=lms_host,
                             port=lms_port,
                             app_id=app_id,
                             app_key=app_key,
                             user_id=user_id,
                             user_key=user_key)
    
    page = _page_header + body + _page_footer
    return page

@app.post('/start')
def start_submit():
    global _app_context, _user_context

    _app_context.update(_default_app)
    _app_context['lms_host'] = bottle.request.forms.get('hostField')
    _app_context['lms_port'] = bottle.request.forms.get('portField')
    _app_context['ac'] = d2lauth.fashion_app_context(app_id=bottle.request.forms.get('appIDField'),
                                                     app_key=bottle.request.forms.get('appKeyField'))

    target_url = urllib.parse.urlunsplit((_app_context['scheme'],
                                          _app_context['host']+':'+_app_context['port'],
                                          '/start','',''))
    lms_netloc = _app_context['lms_host']+':'+_app_context['lms_port']
    auth_url = _app_context['ac'].create_url_for_authentication(lms_netloc, target_url)
    bottle.redirect(auth_url)
    return


##
## API call handlers
##
# assemble grade-list data
@app.get('/getGradeList')
def getgradelist_pg():
    global _user_context
    vlp = _default_app['lms_ver']['lp']
    vle = _default_app['lms_ver']['le']

    result = []

    if not 'uc' in _user_context:
        bottle.abort(403, 'No user context: must authenticate first.')
    else:
        # first, we assemble an array of all the calling user's courses; since
        # the myenrollments call fetches a paged result set, we need to make
        # sure we get all the available data pages
        courses = []
        mark = None
        while True: # pg.HasMoreItems
            pg = d2lservice.get_my_enrollments(_user_context['uc'],
                                               orgUnitTypeId=_d2l_ids['course_offering'],
                                               bookmark=mark,
                                               ver=vlp)
            courses += pg.Items
            if not pg.HasMoreItems:
                break
            mark = pg.Bookmark

        # for each course, gather the grade information
        for course in courses:
            # create the skeleton of a course grade-list for current course
            the_course = CourseGradeList(course['OrgUnit']['Id'],
                                         course_name=course['OrgUnit']['Name'],
                                         course_code=course['OrgUnit']['Code'])
            # grab the list of students for the course
            students = []
            mark = None
            while True: # pg.HasMoreItems
                pg = d2lservice.get_enrolled_users_for_orgunit(_user_context['uc'],
                                            course['OrgUnit']['Id'],
                                            roleId=_d2l_ids['student_role'],
                                            bookmark=mark,
                                            ver=vlp)
                students += pg.Items
                if not pg.HasMoreItems:
                    break
                mark = pg.Bookmark
            
            # for every student, fetch the final grade if we can, and build a
            # student entry
            for student in students:
                try:
                    g = d2lservice.get_final_grade_value_for_user_in_org(_user_context['uc'],
                                            course['OrgUnit']['Id'],
                                            student['User']['Identifier'],
                                            ver=vle).DisplayedGrade
                except requests.exceptions.HTTPError:
                    g = 'No Grade Available'

                the_course.addupdate_student(student['User']['Identifier'],
                                             name=student['User']['DisplayName'],
                                             id=student['User']['OrgDefinedId'],
                                             grade=g)

            # add the json form of the CourseGradeList as the next element in
            # the result array
            result.append(the_course.as_json())

        return repr(result)



##
## Handle /reset route, regardless of method
##
@app.route('/reset')
def reset_pg():
    global _app_context, _user_context
    
    # first, flush all state for the user context
    _user_context.clear()
    # next, flush the app context
    _app_context.clear()
    page = '''{0}
              <table style="float:left; class="plain">
                <tr class="plain"><td class="plain">
                  The sample application has reset; you must <a href="/start">re-authenticate</a> the user.
              </table>
              {1}'''.format(_page_header, _page_footer)
    return page

# redirect the root folder to the start page
@app.route('/')
def redirect_to_start_pg():
    bottle.redirect('/start')

##
## Main processing loop
##
# Run the bottle app instance to run on the web-apps's host, listening on the right port
bottle.run(app, host=_default_app['host'], port=_default_app['port'])



