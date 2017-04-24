
// Cognito Identity Pool Id
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:9f38c1fd-851b-4570-a517-fdc77227e14b'
});
AWS.config.region = 'us-east-1'; // Region

// Cognito User Pool Id
AWSCognito.config.region = 'us-east-1';
AWSCognito.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:9f38c1fd-851b-4570-a517-fdc77227e14b'
});

AWSCognito.config.credentials.get();

//console.log("AWS.config.credentials"+JSON.stringify(AWS.config.credentials));
//console.log("AWSCognito.config.credentials"+JSON.stringify(AWSCognito.config.credentials));

var COGNITO_REGION = 'us-east-1';
var USER_POOL_ID = 'us-east-1_Q5V9smPLb';
var IDENTITY_POOL_ID = 'us-east-1:9f38c1fd-851b-4570-a517-fdc77227e14b';
var CLIENT_ID = '6lpap7cs0l1q28o2nnpnia8u7u';

var awstoken;

$(document).ready(function() {

    function RenderCharts() {

    var barChart = c3.generate({
            bindto: '#last6month',
            data: {
                x: 'x',
                url: 'estimate_month_to_date_payer.json',
                mimeType: 'json',
                type: 'bar'
            },
        axis: {
            x: {
                type: 'category' // this needed to load string x value
            }
        }
     });

}

    $('#login').on('click', function (e) {
        $('#id01').modal('toggle');
    });

    $("body").on("click", "#fakeSubmit", function (e) {
        e.preventDefault();
        console.log('fake_login');
        $('#id01').modal('toggle');
        uname = $("#uname").val();
        pwd = $("#psw").val();

      var authenticationData = {
          Username : uname, // your username here
          Password : pwd // your password here
      };
      var authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails(authenticationData);

      var poolData = {
          UserPoolId : USER_POOL_ID, // your user pool id here
          ClientId : CLIENT_ID // your app client id here
      };
      var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);

      var userData = {
          Username : $('#uname').val(), // your username here
          Pool : userPool
      };
      var cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

      console.log("AWS.config.credentials"+JSON.stringify(AWS.config.credentials));


      //console.log('cognitoUser'+JSON.stringify(cognitoUser));
      //console.log('userData'+JSON.stringify(userData));
      //console.log("AWS.config.credentials"+JSON.stringify(AWS.config.credentials));
      //console.log("AWSCognito.config.credentials"+JSON.stringify(AWSCognito.config.credentials));

      try {
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: function (result) {
                console.log('access token + ' + result.getAccessToken().getJwtToken());

                var login = 'cognito-idp.' + COGNITO_REGION + '.amazonaws.com/' + USER_POOL_ID;

                console.log('login string is: ' + login);

                AWS.config.credentials = new AWS.CognitoIdentityCredentials({
                    IdentityPoolId : IDENTITY_POOL_ID, // your identity pool id here
                    IdentityId: AWS.config.credentials.identityId,
                });
                AWS.config.credentials.params.Logins = {};
                AWS.config.credentials.params.Logins[login] = result.getIdToken().getJwtToken();

                AWS.config.credentials.refresh(function (err) {
                    // now using authenticated credentials
                    if(err)
                    {
                      console.log('Error in authenticating to AWS '+ err);

                    }
                    else
                    {
                      console.log('identityId is: ' + AWS.config.credentials.identityId);
                      awstoken = {
                        expireTime: AWS.config.credentials.expireTime,
                        accessKeyId: AWS.config.credentials.accessKeyId,
                        sessionToken: AWS.config.credentials.sessionToken,
                        secretAccessKey: AWS.config.credentials.secretAccessKey
                      };
                      var table = new AWS.DynamoDB({params: {TableName: 'managelock'}});
                      table.getItem({Key: {user: {S: $('#inputEmail').val()}}}, function(err, data) {
                        //{"Item":{"thingName":{"S":"jodion-pi"},"user":{"S":"jondion@amazon.com"}}}
                        console.log(data.Item.thingName.S); // print the item data
                        thingName = data.Item.thingName.S;
                        isLoggedIn = true;

                        refreshStatus();

                      });
                    }
                });
            },

            onFailure: function(err) {
                //alert(err);
            },
        });
      } catch(e) {
          console.log(e);
      }

    });
});



