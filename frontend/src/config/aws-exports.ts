const awsConfig = {
    Auth: {
        Cognito: {
            userPoolId: import.meta.env.VITE_USER_POOL_ID,
            userPoolClientId: import.meta.env.VITE_USER_POOL_CLIENT_ID,
            loginWith: {
                oauth: {
                    domain: import.meta.env.VITE_COGNITO_DOMAIN,
                    scopes: ['email', 'openid', 'profile'],
                    redirectSignIn: [import.meta.env.VITE_REDIRECT_SIGN_IN],
                    redirectSignOut: [import.meta.env.VITE_REDIRECT_SIGN_OUT],
                    responseType: 'token'
                }
            }
        },
        API: {
            endpoints: [
                {
                    name: 'RecipeAPI',
                    endpoint: import.meta.env.VITE_API_ENDPOINT,
                    region: import.meta.env.VITE_AWS_REGION
                }
            ]
        }
    }
};

export default awsConfig;
