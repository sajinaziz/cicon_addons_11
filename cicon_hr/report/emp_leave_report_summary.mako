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
           min-height: 25px ;
           padding: 4px;
       }
        th
        {
            min-height: 50px;
        }

    </style>
</head>
<body>


    <table>
        <thead>
            <th> Sno </th>
            <th> ID </th>
            <th> Name </th>
            <th> Leave Type </th>
        <th> JAN </th>
        <th> FEB </th>
        <th> MAR </th>
        <th> APR </th>
        <th> MAY </th>
        <th> JUN </th>
        <th> JUL </th>
        <th> AUG </th>
        <th> SEP </th>
        <th> OCT </th>
        <th> NOV </th>
        <th> DEC </th>
        <th> TOTAL </th>
        </thead>
        <tbody>
            <% _count = 0  %>
            %for emp in objects:
            <%
                _emp_leaves = []
                _emp_leaves = getEmployeeLeave(emp.id)
                i =1
                _count += 1
            %>
            %for _emp_l in _emp_leaves:
                <%
                    m = 1
                    _total = 0
                    _rowspan = len(_emp_leaves)

                %>
            <tr>
                %if i < 2:
                    <td rowspan=${_rowspan} style="width:5%"> ${_count} </td>
                    <td rowspan=${_rowspan} style="width:10%"> ${emp.cicon_employee_id} </td>
                    <td rowspan=${_rowspan} style="width:20%"> ${emp.name} </td>
                %endif
                 <td style="width:10%"> ${_emp_l} </td>
                %while m <= 12:
                    <td style="width:4%"> ${_emp_leaves[_emp_l][str(m)]}  </td>
                <%
                 _total += _emp_leaves[_emp_l][str(m)]
                 m += 1
                %>
                %endwhile
                <td style="width:4%;font-weight:bold"> ${_total}</td>

                <%
                    i += 1
                %>

            </tr>

             %endfor
           %endfor
       </tbody>
    </table>
</body>

</html>