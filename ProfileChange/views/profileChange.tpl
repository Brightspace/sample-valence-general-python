<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Profile Change Demo App</title>
    <style type="text/css">
    table.plain
    {
        border-color: transparent;
        border-collapse: collapse;
    }

    table td.plain
    {
        paddding: 5px;
        border-color: transparent;
    }

    table th.plain
    {
        padding: 6px 5px;
        text-align: left;
        border-color: transparent;
    }

    tr:hover
    {
        background-color: transparent !important;
    }
    </style>
    <script src="https://code.jquery.com/jquery-latest.min.js" type="text/javascript"></script>
    <script type="text/javascript">
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

    </script>
</head>
<body>
    <form id="configForm" method="post">
        <table>
            <tr>
                <td><h4>Host: </h4></td>
                <td><input id="hostField" name="hostField" type="text" size=30 value="{{host}}" /></td>
                <td><h4>Port:</h4></td>
                <td><input id="portField" name="portField" type="text" size=3 value="{{port}}" /></td>
            </tr>
            <tr>
                <td><h4>Nickname:</h4></td>
                <td><input id="nicknameField" type="text" size=30 value="{{nickname}}" /></td>
                <td><h4>Email:</h4></td>
                <td><input id="emailField" type="text" size=30 value="{{email}}" /></td>
            </tr>
        </table>
    </form><br /><br />
    You can change your Nickname and Email shown, then click here.    
    <input id="updateProfile" type="button" value="Update Nickname and Email" onclick="updateProfile()" /><br /><br /> 
    <hr />

    <table style="float:left;" class = "plain">
        <tr class = "plain">
            <td class = "plain">
                Click to show the current state of your profile on the LMS.
                <input id="getProfile" type="button" value="Show Profile on Server" style="float:right" onclick="getProfile()" /><br /><br />
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
