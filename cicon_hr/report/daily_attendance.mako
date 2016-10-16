{% extends "base.html" %}
{% block body %}
    % for r in objects:
    <div class="container">

    <p style="font-weight: bold" > Attendance Date:  ${time.strftime('%d-%m-%Y, %A',time.strptime(r.attendance_date,'%Y-%m-%d'))} </p>

    <table class="table table-bordered">
        <thead>
            <th> SNo </th>
            <th> ID </th>
            <th> Name </th>
            <th> Sign In </th>
            <th> Sign Out </th>
            <th> Work Hour </th>
            <th> Leave </th>
        </thead>
        <tbody>
             %for a in r.attendance_ids:
            <tr>
                <td style="width:5%"> ${loop.index} </td>
                <td style="width:10%"> ${a.employee_id.cicon_employee_id} </td>
                <td style="width:25%"> ${a.employee_id.name} </td>
                <td style="width:20%">
                    %if a.sign_in:
                        ${a.sign_in.log_datetime}
                    %endif
                </td>
                <td style="width:20%">
                    %if a.sign_out:
                        ${a.sign_out.log_datetime} </td>
                    %endif
                <td style="width:10%">
                %if a.work_hour > 0:
                    ${r.get_work_hour(a.work_hour)}
                %endif
                </td>
               <td style="width:10%">
                    %if a.leave_id:
                        ${r.getSelectionValue('cicon.hr.employee.leave','leave_type', a.leave_id.leave_type)}
                    %endif
                </td>

            </tr>
            %endfor
        </tbody>
    </table>

    </div>

    %endfor
{% endblock %}
