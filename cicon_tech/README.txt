
depend module
---------------

1) project :  To link with Project Management module with Submittal with a Job Site
2) res_company_extn : To Create Company defined customisation Eg: 'Logo' , Prefix ..etc,..
3) cic_user_sign : To Defined user access to manager signatory


User Roles
--------------

    1) Technical / User :   User who creates and revise the submittal ,
        no access on master information eg: job site , customer and to modify on state submitted for revision
    2) Technical / Approval : Group with all access for a user +  access to approve a submittal to next stage submitted

    3) Technical / Admin : Group with all access of approval and user + access to create &  modify job site , customer information
                           + reset the status of a submittal to draft state and cancel submittal

  Note:  user Creation managed by admin


WorkFlow
--------------

  1) Create Partner and Job Site with required information ( Site Ref ,Contact etc..)
  2) Create submittal and set status as Approved -> Submittal;
  3) If needs revision two level revision possible by document which is already submitted and the full set of submittal


