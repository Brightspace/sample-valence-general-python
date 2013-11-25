#!/usr/local/bin/python3

# -*- coding: utf-8 -*-
# Getting Started sample to use with the D2LValence package to demo the auth
# library.
#
# Copyright (c) 2012-2013 Desire2Learn Inc.
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

## Imports
# Python stdlib imports
import urllib.parse

# Python third-party (non-D2L) lib imports
import beaker.middleware
import bottle
from bottle import request, route, hook, template, redirect, abort

# D2L SDK library imports
# - the SDK also depends on the 'requests' third-party lib
import d2lvalence.auth as d2lauth
import d2lvalence_util.data as d2ldata
import d2lvalence_util.service as d2lservice


## ----------------------------------------------------------------------------
## Service configuration
##
# Import the application configuration state from a separate file that can be
# placed under stricter control than this web-app code. app_config is a
# dictionary of name-value pairs:
#
#   app_id --  App ID as provided by D2L -- DON'T HARDCODE INTO YOUR APP
#   app_key -- App Key as provided by D2L -- DON'T HARDCODE INTO YOUR APP
#   host   --  host for the web-app
#   port   --  port number for the web-app
#   scheme --  protocol to use for user <--> web-app interaction
#   lms_host -- hostname for the back-end LMS
#   lms_port -- port number for the back-end LMS
#   encrypt_requests -- True: use HTTPS when making API calls to the LMS
#   lms_ver -- product component API versions to call
#   verify -- cert verification flag
#   debug -- debug flag

from conf_basic import app_config as _CFG

# Callback URL for receiving user auth tokens for Valence LF API calls
_AUTH_ROUTE = '/token'
_AUTH_CB = '{0}://{1}:{2}{3}'.format(_CFG['scheme'],
                                     _CFG['host'],
                                     _CFG['port'],
                                     _AUTH_ROUTE)
## ----------------------------------------------------------------------------


## Service global singleton objects for all threads in this web service
_ac = d2lauth.fashion_app_context(app_id=_CFG['app_id'],
                                  app_key=_CFG['app_key'])


## Beaker middleware
# set up beaker session state middleware
_session_opts = {'session.type': 'memory',
                 'session.auto': True}

# wrap the bottle app in a beaker
_app = beaker.middleware.SessionMiddleware(bottle.app(), _session_opts)


# hook request to make the beaker session easier to get to
@hook('before_request')
def _setup_request():
    request.session = request.environ['beaker.session']


## ----------------------------------------------------------------------------
## Web service code
## ----------------------------------------------------------------------------

## Route handlers
# Ping handler for really simple web-server testing: does it ping back?
@route('/ping')
@route('/ping/')
@route('/ping/<name:re:[a-zA-Z0-9]+>')
def ping_handler(name='World'):
    assert name.isalnum()
    return template('<b>Ping! Hello {{name}}!</b>', name=name)


# Default endpoint to start from
@route('/')
@route('/start')
def start_handler():

    if 'user_context' not in request.session:
        # valence user not yet auth'd -- start the process from scratch
        aurl = _ac.create_url_for_authentication(
            host=_CFG['lms_host'],
            client_app_url=_AUTH_CB,
            encrypt_request=_CFG['encrypt_requests'])

        # redirect to the valence auth entry point on the LMS
        return template('needsAuth', aurl=aurl)

    else:
        # we do have a user context so render the profile form page
        uc = _ac.create_user_context(
            d2l_user_context_props_dict=request.session['user_context'])
        user_profile = d2lservice.get_my_profile(
            uc,
            ver=_CFG['lms_ver']['lp'],
            verify=_CFG['verify'])
        return template(
            'profileChange',
            host=_CFG['lms_host'],
            port=_CFG['lms_port'],
            nickname=user_profile.Nickname,
            email=user_profile.Email)


# Endpoint for authentication callback: the LMS will send user tokens back
# to this route once they're generated; note that this route does not display
# anything itself -- it caches the user context properties in the session and
# then redirects to the "whoami" page.
@route(_AUTH_ROUTE, method='GET')
def auth_token_handler():
    # we've got back a set of user tokens from the LMS, so use them to build a
    # valence user context
    uc = _ac.create_user_context(
        result_uri=request.url,
        host=_CFG['lms_host'],
        encrypt_requests=_CFG['encrypt_requests'])

    # store the context's props, so we can rebuild it from these props later
    request.session['user_context'] = uc.get_context_properties()

    # redirect to the whoami handler
    redirect('/', 302)


##
## Valence-client-facting API call handlers
##
# fetch current profile data from server
@route('/getProfile', method='GET')
def getProfile_handler():

    if 'user_context' not in request.session:
        abort(403, "No user context: must authenticate first.")
    else:
        # we have a user context, so let's revive it
        uc = _ac.create_user_context(
            d2l_user_context_props_dict=request.session['user_context'])

        # retrieve the User.UserProfile structure for the user context
        user_profile = d2lservice.get_my_profile(
            uc,
            ver=_CFG['lms_ver']['lp'],
            verify=_CFG['verify'])
        return repr(user_profile)


@route('/updateProfile', method='GET')
def updateProfile_handler():

    nickname = request.query.nickname
    email = request.query.email

    if 'user_context' not in request.session:
        abort(403, "No user context: must authenticate first.")
    else:
        uc = _ac.create_user_context(
            d2l_user_context_props_dict=request.session['user_context'])
        user_profile = d2lservice.get_my_profile(
            uc,
            ver=_CFG['lms_ver']['lp'],
            verify=_CFG['verify'])
        user_profile.Nickname = str(nickname)
        user_profile.Email = str(email)
        new_user_profile = d2lservice.update_my_profile(
            uc,
            user_profile,
            ver=_CFG['lms_ver']['lp'],
            verify=_CFG['verify'])
        return repr(new_user_profile)


## Get bottle to run the web service app.
bottle.run(
    app=_app,
    host=_CFG['host'],
    port=_CFG['port'],
    debug=_CFG['debug'])
