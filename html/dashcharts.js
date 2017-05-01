
// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'us-east-1';
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:5308f314-dd80-4273-9130-2178df6e5dde',
});


// Cognito User Pool Id
AWSCognito.config.region = 'us-east-1';
AWSCognito.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:5308f314-dd80-4273-9130-2178df6e5dde'
});

AWSCognito.config.credentials.get();

//console.log("AWS.config.credentials"+JSON.stringify(AWS.config.credentials));
//console.log("AWSCognito.config.credentials"+JSON.stringify(AWSCognito.config.credentials));

var COGNITO_REGION = 'us-east-1';
var USER_POOL_ID = 'us-east-1_RdBiutRhk';
var IDENTITY_POOL_ID = 'us-east-1:5308f314-dd80-4273-9130-2178df6e5dde';
var CLIENT_ID = '7b6ejd42btgrtip7nvm5vd2jm';

var awstoken;

var barChart = c3.generate({
    bindto: '#last6month',
    data: {
        columns: [],
        x: 'x',
        type: 'bar'
    },
    axis: {
        x: {
            type: 'category' // this needed to load string x value
        }
    }
});

$(document).ready(function() {

    $('#login').on('click', function (e) {
        $('#id01').modal('toggle');
    });

    $('#change_psw').on('click', function (e) {
        $('#id03').modal('toggle');
    });

    $("body").on("click", "#fakeSubmit_initial_psw", function (e) {
        e.preventDefault();
        uname = $("#uname_initial_psw").val();
        initialPassword = $("#initial_psw").val();
        newPassword = $("#new_psw").val();

        var authenticationData = {
        Username : uname,
        Password : initialPassword,
        };
        var authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails(authenticationData);

        var poolData = {
            UserPoolId : USER_POOL_ID,
            ClientId : CLIENT_ID
        };

        var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);
        var userData = {
            Username : uname,
            Pool : userPool
        };

        var cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: function (result) {
                // User authentication was successful
            },

            onFailure: function(err) {
                sweetAlert("You probably messed something up!", err, "error");
                // User authentication was not successful
            },

            mfaRequired: function(codeDeliveryDetails) {
                // MFA is required to complete user authentication.
                // Get the code from user and call
                cognitoUser.sendMFACode(mfaCode, this)
            },

            newPasswordRequired: function(userAttributes, requiredAttributes) {
                // User was signed up by an admin and must provide new
                // password and required attributes, if any, to complete
                // authentication.

                // the api doesn't accept this field back
                delete userAttributes.email_verified;
                delete userAttributes.phone_number_verified;

                // Get these details and call
                cognitoUser.completeNewPasswordChallenge(newPassword, userAttributes, this);
            }
        });
        $('#id03').modal('toggle');
     })

    $("body").on("click", "#fakeSubmit", function (e) {
        e.preventDefault();
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

      //console.log("AWS.config.credentials"+JSON.stringify(AWS.config.credentials));

/*
      console.log('cognitoUser'+JSON.stringify(cognitoUser));
      console.log('userData'+JSON.stringify(userData));
      console.log("AWS.config.credentials"+JSON.stringify(AWS.config.credentials));
      console.log("AWSCognito.config.credentials"+JSON.stringify(AWSCognito.config.credentials));
*/
      try {
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: function (result) {
                //console.log('access token + ' + result.getAccessToken().getJwtToken());

                var login = 'cognito-idp.' + COGNITO_REGION + '.amazonaws.com/' + USER_POOL_ID;

                //console.log('login string is: ' + login);

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
                      sweetAlert("Login Failed", err, "error");
                      console.log('Error in authenticating to AWS '+ err);
                    }
                    else
                    {
                      //console.log('identityId is: ' + AWS.config.credentials.identityId);

                      /*
                      awstoken = {
                        expireTime: AWS.config.credentials.expireTime,
                        accessKeyId: AWS.config.credentials.accessKeyId,
                        sessionToken: AWS.config.credentials.sessionToken,
                        secretAccessKey: AWS.config.credentials.secretAccessKey
                      }; */

                    var pathname = window.location.pathname.split('/');
                    var awsBucket = pathname[1];

                    var s3 = new AWS.S3();

                    var s3content = ''
                    var params = {Bucket: awsBucket, Key: 'html/estimate_month_to_date_payer.txt'};
                    s3.getObject(params, function(err, data) {
                            if (err){
                                console.log(err, err.stack);
                                sweetAlert("Error accessing S3", err, "error");
                            } else{
                                s3content = data.Body.toString();
                                barChart.load({
                                    columns: JSON.parse("[" + s3content + "]")
                                });
                            }
                        });
                    }
                });

            },

            onFailure: function(err) {
                sweetAlert("Login Failed", err, "error");
                //alert(err);
            },
        });
      } catch(e) {
          sweetAlert("Login Failed", err, "error");
          console.log(e);
      }

    });
});



