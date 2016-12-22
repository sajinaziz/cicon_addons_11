<html xmlns="http://www.w3.org/1999/html">
<head>
    <style type="text/css">
            ${css}
        body{
            font-family: arial;
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
        }
        .table_full
        {
            width: 100%;
        }
        .table_border{
            border-width: 1px;
            border-style: solid;
            border-color: #000000;
            width: 100%;
            padding: 5px;
        }
        .remarks
        {
            height: 700px;
            vertical-align: top;
        }
    </style>
</head>
<body>
    <%! from dateutil import parser%>
    %for credit_check in objects:
        <table align="center">
            <tr>
                <td>
                    ${helper.embed_logo_by_name('cicon_logo')|n}
                </td>
                <td>
                    <h1>CREDIT CHECK</h1>
                </td>
            </tr>
        </table>
        <hr>
        <table class="table_full">
            <tr>
                <td class="big_heading">Customer Name</td>
                <td>:</td>
                <td colspan="4">${credit_check.partner_id.name}</td>
            </tr>
            <tr>
                <td colspan="5">&nbsp;</td>
            </tr>
            <tr>
                <td class="heading">Customer Status</td>
                <td>:</td>
                <td>${'Unknown' if credit_check.status == False else credit_check.status}</td>
                <td>&nbsp;</td>
                <td class="heading">Payment Term</td>
                <td>:</td>
                <td>${credit_check.payment_terms.name}</td>
            </tr>
            <tr>
                <td class="heading">Cases of Holding of Cheque</td>
                <td>:</td>
                <td>${credit_check.cheque_hold}</td>
                <td>&nbsp; </td>
                <td class="heading">Cases of Check Bounce</td>
                <td>:</td>
                <td>${credit_check.cheque_bounce}</td>
            </tr>
            <tr>
                <td class="heading">Overall Account Balance</td>
                <td>:</td>
                <td>${credit_check.account_balance}</td>
                <td>&nbsp;</td>
                <td class="heading">Sales Person</td>
                <td>:</td>
                <td>${credit_check.sales_person}</td>
            </tr>
            <tr>
                <td colspan="5">&nbsp;</td>
            </tr>
            <tr>
                <td class="big_heading">Project Name</td>
                <td>:</td>
                <td colspan="4">${credit_check.project_id.name}</td>
            </tr>
            <tr>
                <td colspan="5">&nbsp;</td>
            </tr>
            <tr>
                <td class="heading">Account Balance</td>
                <td>:</td>
                <td colspan="4">${credit_check.proj_account_balance}</td>
            </tr>
            <tr>
                <td class="heading">Current Due</td>
                <td>:</td>
                <td>${credit_check.proj_current_due}</td>
                <td>&nbsp;</td>
                <td class="heading">Over Due</td>
                <td>:</td>
                <td>${credit_check.proj_over_due}</td>
            </tr>
            <tr>
                <td class="heading">Sales Person</td>
                <td>:</td>
                <td colspan="4">${credit_check.proj_sales_person}</td>
            </tr>
            <tr>
                <td class="heading" colspan="6">Remarks :</td>
            </tr>
            <tr>
                <td colspan="6" class="remarks">${'N/A' if credit_check.remarks == False else credit_check.remarks}</td>
            </tr>
        </table>
        <table class="table_border">
            <tr>
                <td colspan="2">
                    <b>Date</b> : ${parser.parse(credit_check.date_create).strftime('%d %B %Y')}
                </td>
            </tr>
            <tr>
                <td><b>Credit check conducted by</b>:<br/><br/>
                    ${credit_check.user_id.name}<br/>
                </td>
                <td><b>Approved by</b>:<br/><br/><br/>
                    -------------------------------------------------
                </td>
            </tr>
        </table>
        <p style="page-break-after: always"/>
    %endfor
</body>
</html>