/**
 * Copyright (c) 2012 Desire2Learn Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the license at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */

/******************************************************************************
 * Javascript functions for the sample HTML file                              *
 ******************************************************************************/

// Button Handling Methods
function getProfile() {

    $.ajax({
               url: "/getProfile",
               data: { },
               success: function(data) {
                   $('#result').html(data);
               },
               error: function(jqXHR, textStatus, errorThrown) {
                   $('#resultHeading').html("Error:");
                   $('#result').html(textStatus);
               }
           });
}

function updateProfile() {

    var nickname = $('#nicknameField').val();
    var email = $('#emailField').val();

    $.ajax({
               url: "/updateProfile",
               data: {
                   nickname: nickname,
                   email: email
               },
               success: function(data){
                   $('#result').html(data);
               },
               error: function(jqXHR, textStatus, errorThrown) {
                   $('#resultHeading').html("Error:");
                   $('#result').html(textStatus);
               }
           });
}

function clearTextArea() {
    $("#resultHeading").html("&nbsp;");
    $("#result").html("&nbsp;");
}
