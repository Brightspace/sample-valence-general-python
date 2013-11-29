<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Final Grade Demo App</title>
	<style type = "text/css">
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
    function getGradeList() {

       $.ajax({
          url:"/getGradeList",
          data: {},
          success: function(data) {
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
        </table>
	</form><br /><br />
    <hr />

    <table style="float:left;" class = "plain">
        <tr class = "plain">
            <td class = "plain">
                Click to retrieve all the final grades for the <b>{{name}}</b>.
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
