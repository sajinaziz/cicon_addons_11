<html>
<head>
    <style type="text/css">
        ${css}

       body
       {
           font-family: Tahoma;
           font-size: 12;
           margin:2;
           padding:5px;
       }
       table, tr, td, th
       {
           border: 1px solid darkgray;
           border-collapse: collapse ;
       }
       td ,tr
       {
           margin: 3px;
           padding: 4px;
       }

    </style>
</head>
<body>


    <%
        from datetime import datetime
        from datetime import timedelta
        _fromDate = datetime.strptime(context.get('start_date',False),'%Y-%m-%d')
        _toDate = datetime.strptime(context.get('end_date',False),'%Y-%m-%d')
    %>

  <%
    _employees = [(e.employee_id.id ,e.employee_id.name ,e.employee_id.cicon_employee_id) for e in objects]
    _temp_date = _fromDate
  %>

    %for employee in set(_employees):
        <% _count = 0 %>
        <p> ${employee} </p>
        <table>
            <thead>
                <th> Sno </th>
                <th> Date </th>
                <th> IN </th>
                <th> IN </th>
                <th> Work Hour</th>
                <th> Leave </th>
            </thead>
            <tbody>
        %while _temp_date <= _toDate :
            <tr>
            <%
            _count += 1
            _attendance = [a for a in objects if a.employee_id.id == employee[0] and a.date == _temp_date.strftime('%Y-%m-%d')]
            _leave_type = ''
            %>
            <td style="width:5%"> ${_count} </td>
            <td style="width:25%" > ${_temp_date.strftime('%A, %d-%m-%Y')} </td>
            <td style="width:20%">
                %if _attendance and _attendance[0].sign_in:
                    ${_attendance[0].sign_in.log_datetime}
                %endif
            </td>
            <td style="width:20%">
                %if _attendance and _attendance[0].sign_out:
                    ${_attendance[0].sign_out.log_datetime}
                %endif
            </td>
            <td style="width:10%">
                %if _attendance and _attendance[0].work_hour > 0:
                    <%
                        _wh = str( _attendance[0].work_hour).split('.')
                    %>
                    ${_wh[0]+':'+_wh[1]}
                %endif
            </td>
               %if _attendance and _attendance[0].leave_id:
                <%
                      _leave_type = getSelectionValue('cicon.hr.employee.leave','leave_type',  _attendance[0].leave_id.leave_type)
                %>
                %endif

            <td style="width:15%">
                  ${_leave_type}
            </td>
            <%
                _temp_date += timedelta(days=1)
            %>
            </tr>
        %endwhile
            </tbody>
        </table>
    %endfor

</body>
</html>