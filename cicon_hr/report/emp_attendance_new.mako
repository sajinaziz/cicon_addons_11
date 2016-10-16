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

       table
       {
         width: 100%;
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


    %for employee in objects:
        <table>
            <caption> employee.employee_id.name </caption>
            <thead>
                <th> Sno </th>
                <th> Date </th>
                <th> IN </th>
                <th> OUT </th>
                <th> Work Hour</th>
                <th> Leave </th>
            </thead>
            <tbody>
             %for k, v in  employee.get_employee_attendance().iteritems()|sort:
            <tr>
                <td> ${loop.index} </td>
                <td> ${k} </td>
                <td>
                    %if v and v.attendance.sign_in:
                       ${v.attendance.sign_in.log_datetime}
                    %endif
                </td>
                <td>
                    %if v and v.attendance.sign_out:
                       ${v.attendance.sign_out.log_datetime}
                    %endif
                </td>
                <td>
                    %if v :
                       ${employee.get_work_hour(v.attendance.work_hour)}
                    %endif
                </td>
                <td>
                    %if v and v.attendance.leave_id:
                       ${v.attendance.work_hour.leave_id.leave_type}
                    %endif
                </td>

            </tr>
             %endfor
            </tbody>
        </table>
    %endfor

</body>
</html>