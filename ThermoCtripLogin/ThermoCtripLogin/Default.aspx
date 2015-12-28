<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="ThermoCtripLogin.Default" EnableViewState="true" Trace="false" %>

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title></title>
    <script type="text/javascript" src="jquery-1.10.2.min.js"></script>
</head>
<body>
    <form id="mainform" name="mainform" action="<%=encodeString%>">
        <%if (isdebug == true)
          {
        %>
        <input name="UserID" value="obk_Thermo" type="text" />
        <input name="Password" value="obk_Thermo" type="text" />
        <input name="EmployeeID" value="T100135" type="text" />
        <input name="OrderType" value="corp" type="text" />
        <div style="display: block">
            <input type="submit" formmethod="post" value="Ctrip Login" />
        </div>
        <%} %>
        <%else
          { %>
        <div style="display: none">
            <input name="Token" value="<%=encryptdata %>" type="hidden" />
            <input type="submit" formmethod="post" value="Ctrip Login" />
        </div>
        <%} %>
    </form>
    <script type="text/javascript">
        $(document).ready(function(){
            $("form").submit();  
        });
    </script>
</body>
</html>
