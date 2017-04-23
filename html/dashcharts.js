

function AuthAws(user, pass) {

    var CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;

    var authenticationData = {
            Username : user,
            Password : pass,
        };
        var authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails(authenticationData);
        var poolData = {
            UserPoolId : 'us-east-1_Q5V9smPLb',
            ClientId : '6lpap7cs0l1q28o2nnpnia8u7u'
        };
        var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);
        var userData = {
            Username : 'username',
            Pool : userPool
        };
        var cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: function (result) {
                console.log('access token + ' + result.getAccessToken().getJwtToken());

                AWS.config.credentials = new AWS.CognitoIdentityCredentials({
                    IdentityPoolId : 'us-east-1_Q5V9smPLb',
                    Logins : {
                        // Change the key below according to the specific region your user pool is in.
                        'cognito-idp.us-east-1.amazonaws.com/us-east-1_Q5V9smPLb' : result.getIdToken().getJwtToken()
                    }
                });

                // Instantiate aws sdk service objects now that the credentials have been updated.
                // example: var s3 = new AWS.S3();

            },

            onFailure: function(err) {
                alert(err);
            },

        });

}


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
        e.preventDefault();
        uname = $("#uname").val()
        pwd = $("#psw").val()
        AuthAws(uname, pwd)
});

