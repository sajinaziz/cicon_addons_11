<html xmlns="http://www.w3.org/1999/html">
<head>
    <style type="text/css">
      ## ${css}

##.list_sale_table {
##    border:thin solid #000000;
##    text-align:center;
##    border-collapse: collapse;
##    font-family: times,serif;
##}
##
##.list_sale_table td {
##    border:thin solid #000000;
##    text-align:right;
##    font-size:13px;
##    padding: 3px;
##}
##
####.list_sale_table tr {
####    display: block;
####    page-break-inside: avoid !important;
####}


table tbody tr{
    page-break-inside: avoid !important;
}

##
##.list_bank_table td {
##    text-align:left;
##    font-size:13px;
##    padding: 3px;
##}
##
##.list_bank_table th {
##    background-color: #EEEEEE;
##    text-align:left;
##    font-size:13px;
##    font-weight:bold;
##    padding-right:3px;
##    padding-left:3px
##}
##
##.list_sale_table th {
##    background-color: #EEEEEE;
##    border: thin solid #000000;
##    text-align:center;
##    font-size:13px;
##    font-weight:bold;
##    padding-right:3px;
##    padding-left:3px;
##}
##
##.list_table thead {
##    display:table-header-group;
##}
##
##.list_tax_table td {
##    text-align:left;
##    font-size:13px;
##}
##
##
##.list_table thead {
##    display:table-header-group;
##}
##
##.list_total_table td {
##    text-align:right;
##    font-size:13px;
##}
##
##.no_bloc {
##    border-top: thin solid  #ffffff ;
##}
##
##
##.list_total_table th {
##    background-color: #F7F7F7;
##    border-collapse: collapse;
##}
##
##tfoot.totals tr:first-child td{
##    padding-top: 15px;
##}
##
##.std_text {
##    font-family: times,serif;
##    font-size:13px;
##}
##
##span.Apple-tab-span{
##    padding: 0 80px; /* Or desired space*/
##}
##
##.note {
##    text-align:left;
##    font-size:13px;
##    border-top:thin solid  #ffffff;
##    border-left:thin solid  #ffffff;
##    border-right:thin solid  #ffffff;
##}
##
##.invoice {
##    font-family: arial,serif;
##    font-weight: bold;
##    font-size:13px;
##}
##.division{
##    color: #008000;
##}
##.left_logo{
##    float: left;
##}
##
##.right_logo{
##    float: right;
##}
##
##.header_text{
##    float: left;
##    width: 450px;
##    text-align: center;
##    font-family: arial,serif;
##    font-size: 13px;
##}
##
###container{width:100%;border-bottom: 1px solid black;}
##
##.company{
##font-weight: bold;
##}
##
##.division{
##    font-weight: bold;
##    color: #008000;
##}
##.email{
##    font-weight: bold;
##}
##.link{
##    color: blue;
##    text-decoration: underline;
##}
##.reference
##{
##    font-style: italic;
##    float: left;
##}
##.quote_date
##{
##    float: right;
##}
##
##div {
##    font-family: times,serif;
##    font-size: 13px;
##}
##
####table {
####    font-family: times;
####    font-size: 13px;
####    border-spacing: 0;
####    padding: 0;
####    border:thin solid #000000;
####    width: 100%;
####}
##
##.partner_address{
##    border: 1px solid black;
##    padding-left: 3px;
##}
</style>
</head>
<body>

<%! from dateutil import parser
from openerp.tools.amount_to_text_en import amount_to_text_ar
%>
    <%page expression_filter="entity"/>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')

    %>
    %for cheque in objects:
    <% setLang(cheque.partner_id.lang) %>
    <%
        ##   quotation = order.state in ['draft', 'sent']
    %>
        <br/>
        <br/>
        <br/>

        <table border="1" cellpadding="2" width ="100%">
            <tr>
                <td style="text-align: right; width: 40px; height: 2em; vertical-align: bottom;">${formatLang(cheque.amount)}</td>
                <td style="text-align: center; width: 150px; vertical-align: top;">${parser.parse(cheque.rcvd_date).strftime('%d/%m/%Y')} </td>
            </tr>
        </table>
        <br/>
        <table border="1" cellpadding="1" width ="100%">
            <tr>
                <td style="text-align: right; width: 40px; height: 1em; vertical-align: bottom;"></td>
                <td style="text-align: left; width: 250px; vertical-align: middle;">${cheque.partner_id.name or ''} </td>
            </tr>
        </table>
        <br/>
        <table border="1" cellpadding="1" width ="100%">
            <tr>
                <td style="text-align: left; width: 100%; height: 3em; vertical-align: top;">${amount_to_text_ar(cheque.amount,'Dirham')}</td>
            </tr>
        </table>

        <br/>
        <table border="1" cellpadding="1" width ="100%">
            <tr>
                <td style="text-align: left; width: 100%; height: 3em; vertical-align: top;"> Being : ${amount_to_text_ar(cheque.amount,'Dirham')}</td>
            </tr>
        </table>

        <br/>
        <table border="1" cellpadding="1" width ="100%">
            <tr>
                <td style="text-align: left; width: 33%; height: 3em; vertical-align: top;"></td>
                <td style="text-align: left; width: 33%; height: 3em; vertical-align: top;">${cheque.res_bank_id.name}</td>
                <td style="text-align: left; width: 33%; height: 3em; vertical-align: top;"></td>
            </tr>
            <tr>
                <td style="text-align: left; width: 33%; height: 3em; vertical-align: top;"></td>
                <td style="text-align: left; width: 33%; height: 3em; vertical-align: top;">${parser.parse(cheque.rcvd_date).strftime('%d/%m/%Y')}</td>
                <td style="text-align: left; width: 33%; height: 3em; vertical-align: top;">${cheque.check_number or ''}</td>
            </tr>
        </table>


</body>
</html>





##        <br/>
##        <br/>
##        <table border="1" style="margin:1px auto; border-color:blue;">
##            <colgroup width="20px"  align="right"></colgroup>
##            <colgroup width="350" align="right"></colgroup>
##            <tr >
##                <td > ${formatLang(cheque.amount)} </td>
####                <td width="20px"  style="text-align: right;"> ${formatLang(cheque.amount)} </td>
####                    <colgroup width="350" align="center"> </colgroup>
####                <colgroup width="50" align="center"> </colgroup>
##                <td > ${parser.parse(cheque.rcvd_date).strftime('%d/%m/%Y')} </td>
##            </tr>
####            <tr >
####                <td style="text-align: right;">${amount_to_text_ar(cheque.amount,'Dirham')}</td>
####                <td>${formatLang(cheque.amount)} </td><td> ffff${cheque.check_number or ''}</td>
####            </tr>
##        </table>
##
##        <br/>
##        <div class="reference">
##            ${cheque.rv_number}
##        </div>
##            <br/>
##        <div class="reference">
##            ${formatLang(cheque.amount)}
##        </div>
##        <div class="quote_date">
##            ${parser.parse(cheque.rcvd_date).strftime('%d/%m/%Y')}
##        </div>
##        <br/>
##        <div class="reference">
##            ${cheque.res_bank_id.name}
##        </div>
##        <br/>
####         <%
####            t=amount_to_text_ar(amount,'Dirham')
####         %>
####        <div class="reference">
####            ${t}
####        </div>
##        ##                    qty = (line.product_uos and line.product_uos_qty or line.product_uom_qty)
##        <br/>
##         <div class="reference">
##            ${cheque.check_number}
##        </div>
##        <br/>
##        <br style="clear:both;"/>
##        <br/>
##        <div class="partner_address">
##            <b>
##                    ${cheque.partner_id.name or ''}
##
##            </b><br/>
##
##            <table>
##                <tr>
##                    <td>Tel</td><td>:</td><td>${cheque.check_number or ''}</td>
##                </tr>
##            </table>
##        </div>
##        <p style="page-break-after: always"/>
    %endfor
