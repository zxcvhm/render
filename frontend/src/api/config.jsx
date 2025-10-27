const getAPIBaseURL = () => {
    const fastApiHost = import.meta.env.VIRE_FASTAPI_HOST;

    if (fastApiHost.strartWith('http')){
        return fastApiHost;
    }
    return 'https://${fastApiHost}.onrender.com';
}

export const API_BASE_URL = getAPIBaseURL();