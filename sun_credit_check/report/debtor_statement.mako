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
                    <h1>DEBTOR STATEMENT</h1>
                </td>
            </tr>

        </table>
        <hr>
        <table class="table_full">
##            <tr>
##                <td colspan="7">${credit_check.user_id.company_id.name}</td>
##            </tr>
##            <tr>
##                <td colspan="7">${credit_check.user_id.company_id.zip or ' '} </td>
##            </tr>
##            <tr>
##                <td colspan="7">${credit_check.user_id.company_id.state_id.name  or ' '}</td>
##            </tr>
##            <tr>
##                <td colspan="7">TEL : ${credit_check.user_id.company_id.phone  or ' '} </td>
##             </tr>
##            <tr>
##                <td colspan="7">FAX : ${credit_check.user_id.company_id.fax  or ' '}</td>
##            </tr>

           <tr>
               <td colspan="7"> CICON BUILDING MATERIALS </td>
           </tr>
               <td colspan="7">  P.O BOX 660 </td>
           <tr>
               <td colspan="7"> ABU DHABI</td>
           </tr>
            <tr>
               <td colspan="7"> TEL : 02-6415444</td>
           </tr>
            <tr>
               <td colspan="7"> FAX : 02-6415511</td>
           </tr>
           <tr>
                <td colspan="2">&nbsp;</td>
                <td colspan="3">${credit_check.partner_id.name}</td>
                <td colspan="2">Statement Date : ${credit_check.date_create}</td>
            </tr>
            <tr>
                <td colspan="2">&nbsp;</td>
                <td colspan="5">PHONE   : ${credit_check.partner_id.phone}</td>
            </tr>
             <tr>
                <td colspan="2">&nbsp;</td>
                <td colspan="5">FAX   :${credit_check.partner_id.fax}</td>
            </tr>
             <tr>
                <td colspan="2">&nbsp;</td>
                <td colspan="5">P.O BOX   :${credit_check.partner_id.zip}</td>
            </tr>
             <tr>
                <td colspan="2">&nbsp;</td>
                <td colspan="5">${credit_check.partner_id.state_id.name}</td>
            </tr>

            <tr>
                <td colspan="7">&nbsp;</td>
            </tr>

            <tr>
                <td colspan="1">Account Code:</td>
                <td colspan="2">${credit_check.proj_credit_id.account_code} / ${credit_check.proj_credit_id.sun_db} </td>
                <td colspan="1">Account Name:</td>
                <td colspan="2">${credit_check.proj_credit_id.account_name}</td>
            </tr>
            %if credit_check.credit_details_ids:
                <tr>
                    <td colspan="7">
                        <table class="table_border">
                            <tr>
                                <td class="cell_border table_heading heading">Date </td>
                                <td class="cell_border table_heading heading">Reference </td>
                                <td class="cell_border table_heading heading">Description </td>
                                <td class="cell_border table_heading heading amount_column">Debit</td>
                                <td class="cell_border table_heading heading amount_column">Credit</td>
                            </tr>
                            %for line in credit_check.credit_details_ids:
                                <tr>
                                    <td class="cell_border">${line.transaction_date}</td>
                                    <td class="cell_border">${line.treference}</td>
                                    <td class="cell_border" style="width:30%">${line.description}</td>
                                    %if line.amount_d_editable > 0:
                                        <td class="cell_border amount amount_column">${line.amount_d_editable}</td>
                                    %else:
                                        <td class="cell_border">&nbsp;</td>
                                    %endif
                                    %if line.amount_c_editable > 0:
                                        <td class="cell_border amount amount_column">${line.amount_c_editable}</td>
                                    %else:
                                        <td class="cell_border">&nbsp;</td>
                                    %endif
                                </tr>
                            %endfor
                            <tr>
                                <td colspan="2"/>
                                <td class="cell_border heading amount">Total</td>
                                <%
                                    proj_account_balance = 0
                                    proj_account_due = 0
                                %>
                                %for line in credit_check.credit_details_ids:
                                    <%
                                        proj_account_balance += line.amount_d_editable
                                        proj_account_due += line.amount_c_editable
                                    %>
                                %endfor

                                %if proj_account_balance > 0:
                                    <td class="cell_border amount heading">${formatLang(proj_account_balance, digits=2)}</td>
                                %else:
                                   <td class="cell_border">&nbsp;</td>
                                %endif
                                % if proj_account_due > 0:
                                    <td class="cell_border amount heading">${formatLang(proj_account_balance, digits=2)}</td>
                                % else:
                                    <td class="cell_border">&nbsp;</td>
                                % endif

                            </tr>
                        </table>
                    </td>
                </tr>
            %endif
            <tr>
                <td colspan="7">&nbsp;</td>
            </tr>
            <tr>
                <td  class="heading" colspan="4">Account Balance</td>
                <td  class="heading amount" colspan="3">${formatLang(proj_account_balance, digits=2)}</td>
            </tr>
            <tr>
                <td   class="heading" colspan="4">Cheque Available</td>
                <td  class="heading amount" colspan="3">${formatLang(credit_check.check_amount, digits=2)}</td>
            </tr>
                <%
                    unpaid_balance = 0
                    unpaid_balance = proj_account_balance - credit_check.check_amount
                %>

            <tr>
                <td   class="heading" colspan="4">UNPAID Balance</td>
                <td   class="heading amount" colspan="3">${formatLang(unpaid_balance, digits=2)}</td>
            </tr>
        </table>

        <p style="page-break-after: always"/>
    %endfor
</body>
</html>