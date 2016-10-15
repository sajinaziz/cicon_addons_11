<html>
<head>
    <style type="text/css">
        ${css}
        
  
    body
    {
        font-size: 12;
        font-family: 'Verdana';
        height: 100%;
    }

    #highlight
    {
      font-weight: bold;

    }

    table
    {
        width:100%;
    }
    td
    {
        text-align: left;

    }


    table.normal
    {
        width: 100%;
        margin: 3px;
        border: 1px solid;
        border-collapse:collapse ;
    }

     td.normal
    {
       border:1px solid #808080;
       height: 25px;
        padding: 3px;
     }
    table.normal th
    {
        border: 1px solid;
        height: 25px;
    }
    caption
    {
        font-weight: bold;
        height: 25px;
        font-size: 16;
        border: 1px solid;
        text-align: center;
    }
     table.with_th th
     {
         border-left: 1px solid;
         border-right: 1px solid;
         height: 25px;
     }

     div.label
      {
         display: inline-block;
         float: left;
         width:25% ;
       }

      footer
      {
          bottom:5;
          font-size:6;
          position: fixed;
      }



    </style>
</head>

<body>



% for s in objects:

    <p id="highlight">
    Ref :  ${s.ref_no}
    </p>
    <p>
        Date : ${formatLang(s.submittal_date,date = True)}
    </p>
    <p style="font-size: 10px">
        <b>${s.partner_id.name}</b><br/>
        P.O Box: ${s.job_site_id.po_box or ''}<br/>
        Tel.: ${s.job_site_id.telephone or ''}<br/>
        FAX: ${s.job_site_id.fax or ''}
    </p>

    <table>
        <tr>
            <td style="width:3%;font-size: 11px;"> Attn:<td>
            <td style="font-weight:bold; font-size: 11px;" >  ${s.job_site_contact.salutation }  ${s.job_site_contact.name or ''}</td>
        </tr>
        %if s.job_site_contact.designation:
            <tr>
                <td style="width:3%;"> <td>
                <td style="font-size: 9px;">[${s.job_site_contact.designation or ''}]</td>
            </tr>
        %endif




    </table>


    <p style="font-size: 11px">
        Dear Sir,
    </p>

    <p style="font-size: 11px">
        <b>Project : ${s.job_site_id.name or ''}</b>
    </p>
    <p style="font-size: 11px">
        <b>Subject : <span style="text-decoration: underline">${s.subject or ''} </span></b>
    </p>
    <p style="font-size: 11px">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
           We would like to
        %if s.revision_number > 0:
             resubmit
        %else:
            submit
        %endif
         the following Shop Drawing and Bar Bending Schedules for the above mentioned subject.
    </p>


    <table class="normal"  style="font-size: 11px">

        <th style="width: 15px;"> SL No. </th>
        <th style="width: 160px;"> Drawing Number </th>
        <th> Status </th>
        <th> Drawing Title </th>

        % for d in s.document_ids:
        <tr>
            <td class="normal" style="width: 15px; text-align: center"> ${loop.index} </td>
            <td style="width: 160px; border:1px solid #808080; height: 25px; padding: 3px;"> ${d.name or ''} </td>
            <td class="normal" style="width: 40px; text-align: center"> ${d.document_status or ''}  </td>
            <td class="normal"> ${d.description or '' } </td>
        </tr>

        % endfor

    </table>
     <p style="font-size: 11px">
         This is for your kind information and necessary action.
     </p>
     <p style="font-size: 11px">
           Thanks & Regards,
     </p>
     <p>
            For <span style="font-weight:bold "> ${s.company_id.name or ''} </span>
     </p>


        ${helper.embed_image('jpeg',s.signed_by.signature_image  or '' )|safe }
     </p>

     <table  style="font-size: 12px;">
         <tr>
             <td style="font-weight: bold"> <p> ${s.signed_by.signature|safe or '' } </p> </td>
         </tr>
         <tr>
             <td>${s.signed_by.partner_id.function or ''}</td>
         </tr>
     </table>

      <br/>
      <table  style="font-size: 10px;">
          <tr>
              <td style="font-weight: bold;width:15%;vertical-align: top">  Enclosures : </td>
##              <td>  Drawings : ${len(s.document_ids) or ''} No(s).</td>

             <td style="vertical-align: top">
                 %for doc_type in s.document_ids |groupby('document_type_id.name'):
                     ${doc_type.grouper} :  ${doc_type.list|length} No(s).
##                    ${doc_type[1] or 'Documents'} : ${len([x for x in _doc_types if x[0] == doc_type[0]])}  No(s).
                    <br/>
                 %endfor
             </td>
              </tr>
          <tr>
              <td style="font-weight: bold;width:15%">  </td>
              <td>${s.enclosures or ''} </td>
          </tr>
      </table>

      <footer>
        <table style="font-size: 9px;">
            <tr>
                <td style="width:20%">Prepared By:</td>
                <td> ${s.submitted_by.name or ''} </td>
            </tr>
        </table>
       </footer>

        % if not loop.last:
            <p style="page-break-after: always">&nbsp;</p>
        % endif
    %endfor
</body>
</html>