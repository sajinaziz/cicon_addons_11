<html xmlns="http://www.w3.org/1999/html">
<head>
    <style type="text/css">
            ${css}
        body{
            font-family: serif, arial;
        }
        table {
            border-spacing: 0;
        }
        td{
            vertical-align: middle;
            padding: 5;
        }
        .big_heading
        {
            font-size: 20px;
            font-weight: bold;
        }
        .heading{
            font-weight: bold;
            background-color: #dfdfdf;
        }
        .table_full
        {
            width: 100%;
            border-spacing: 2px;
        }
        .table_border{
            border-width: 1px;
            border-style: solid;
            border-color: #000000;
            width: 100%;
            padding: 5px;
        }
        .cell_border{
            border-width: 1px;
            border-style: solid;
            border-color: #000000;
        }
        .remarks
        {
            vertical-align: top;
        }
        .amount
        {
            text-align: right;
        }
        .table_heading{
            text-align: center;
        }
        .footer_table
        {
            widows: 50%;
        }
        .main_table
        {
            border-spacing: 2px;
        }
        .amount_column
        {
            width: 100px;
        }
    </style>
</head>
<body>
    <%! from dateutil import parser%>
    %for credit_check in objects:
        <table align="center">
            <tr>
                <td>
                    <h1>CREDIT CHECK</h1>
                </td>
            </tr>
        </table>
        <hr>
        <table class="table_full">
            <tr>
                <td class="big_heading heading">Customer Name</td>
                <td>:</td>
                <td colspan="5">${credit_check.partner_id.name}</td>
            </tr>
            <tr>
                <td colspan="7">&nbsp;</td>
            </tr>
            <tr>
                <td class="heading">Customer Status</td>
                <td>:</td>
                <td colspan="5">${'Unknown' if credit_check.status == False else credit_check.status}</td>
            </tr>
            <tr>
                <td class="heading">Cases of Holding of Cheque</td>
                <td>:</td>
                <td>${credit_check.cheque_hold}</td>
                <td>&nbsp; </td>
                <td class="heading">Payment Term</td>
                <td>:</td>
                <td>${credit_check.payment_terms.name}</td>
            </tr>
            <tr>
                <td class="heading">Cases of Check Bounce</td>
                <td>:</td>
                <td>${credit_check.cheque_bounce}</td>
                <td>&nbsp;</td>
                <td class="heading">Sales Person</td>
                <td>:</td>
                <td>${credit_check.partner_id.user_id.name or ''}</td>
            </tr>
            <tr>
                <td colspan="7">&nbsp;</td>
            </tr>
            %if credit_check.sun_credit_details_ids:
                <tr>
                    <td colspan="7">
                        <table class="table_border">
                            <tr>
                                <td class="cell_border table_heading heading">Account Name</td>
                                <td class="cell_border table_heading heading amount_column">Account Balance</td>
                                <td class="cell_border table_heading heading amount_column">Account Due</td>
                            </tr>
                            %for line in credit_check.sun_credit_details_ids:
                                <tr>
                                    <td class="cell_border">${line.project_id.name or ''}</td>
                                    <td class="cell_border amount amount_column">${line.proj_account_balance}</td>
                                    <td class="cell_border amount amount_column">${line.proj_account_due}</td>
                                </tr>
                            %endfor
                            <tr>
                                <td class="cell_border heading amount">Total</td>
                                <%
                                    proj_account_balance = 0
                                    proj_account_due = 0
                                %>
                                %for line in credit_check.sun_credit_details_ids:
                                    <%
                                        proj_account_balance += line.proj_account_balance
                                        proj_account_due += line.proj_account_due
                                    %>
                                %endfor
                                <td class="cell_border amount heading">${formatLang(proj_account_balance, digits=2)}</td>
                                <td class="cell_border amount heading">${formatLang(proj_account_due, digits=2)}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            %endif
            <tr>
                <td class="heading" colspan="7">Remarks :</td>
            </tr>
            <tr>
                <td colspan="7" class="remarks">${' ' if credit_check.remarks == False else credit_check.remarks}</td>
            </tr>
             <tr>
                <td class="heading" colspan="7">Verification Remarks :</td>
            </tr>
             <tr>
                <td colspan="7" class="remarks">${' ' if credit_check.verification_remarks == False else credit_check.verification_remarks}</td>
            </tr>
             <tr>
                <td class="heading" colspan="7">Management Note :</td>
            </tr>
             <tr>
                <td colspan="7" >${' ' if credit_check.management_note == False else credit_check.management_note}</td>
            </tr>
            <tr>
                <td colspan="7">&nbsp;</td>
            </tr>
        </table>
        <table class="table_border">
            <tr>
                <td colspan="2">
                    <b>Date</b> : ${parser.parse(credit_check.date_create).strftime('%d %B %Y')}
                </td>
            </tr>
            <tr>
                <td class="footer_table"><b>Credit check conducted by</b>:<br/><br/>
                    ${credit_check.user_id.name}<br/>
                </td>
                <td class="footer_table"><b>Approved by</b>:<br/><br/><br/>
                   SAMEER BALOCH
                </td>
            </tr>
        </table>
        <p style="page-break-after: always"/>
    %endfor
</body>
</html>