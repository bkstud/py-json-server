# py-json-server
## Overview
This application allows you to create GET API from directory with JSON files. <br>
The endpoints are build based on directory structure.  <br>
The server allows some JSON preprocessing before serving to endpoints. <br> 
You can enable bearer token authentication based on JWT tokens. <br>
This is fastapi based so you get automatically generated opeanapi.json served under `/docs`.

## Example
Consider following input data directory tree:
```
static/
├── api
│   ├── menu.json
│   ├── test
│   │   └── empty.json
│   └── tests.json
├── consents.json
└── emails.json
```
With content of a file `consents.json`:
```
{
	"registerConsentText": [
		"I consent to the processing of my personal data for registration in ",
		"the system in accordance with the Regulation of the European Parliament and of the\n Council (EU)",
		"2016/679 of 27 April 2016 and in accordance with the\n information clause attached to my consent."
	],
	"teamShareConsentText": [
		"I consent to providing my personal data (name, surname, e-mail) to ",
		"other users of the system \n in order to enable possibility to be selected as a member of the team\n -\n",
		"<span class='red--text'>Lack of consent results in the inability to be invited to the research team.\n</span>"
	],
	"communicationConsentText": "I agree to receive (by e-mail) information about system events.",
	"wishesConsentText": "I agree to receive (by e-mail) occasional wishes"
}
```

After running application you will get following endpoints:
```
GET 
/share/api/menu -> menu.json
/share/api/test/empty -> empty.json
/share/api/test/tests -> tests.json
/share/consents -> consents.json
/share/emails -> emails.json

/login -> will let you get JWT token with default user/password if authentication is enabled
/docs -> Returns openapi autogenerated page
/openapi.json -> Returns autogenerated openapi json

```
Performing GET call on endpoint /share/consents will return text joined as single string:
```
GET /share/consents
{
  "registerConsentText": "I consent to the processing of my personal data for registration in the system in accordance with the Regulation of the European Parliament and of the\n Council (EU)2016/679 of 27 April 2016 and in accordance with the\n information clause attached to my consent.",
  "teamShareConsentText": "I consent to providing my personal data (name, surname, e-mail) to other users of the system \n in order to enable possibility to be selected as a member of the team\n -\n<span class='red--text'>Lack of consent results in the inability to be invited to the research team.\n</span>",
  "communicationConsentText": "I agree to receive (by e-mail) information about system events.",
  "wishesConsentText": "I agree to receive (by e-mail) occasional wishes"
}
```

## Filter data
Using url query args for data searching/filtration. <br>
If input json file is list of dictionaries it can be filtered using query args. <br>
Example consider `posts.json`:
```
[
    { "id": 1, "title": "py-json-server", "author": "bkstud" },
    { "id": 2, "title": "post2", "author": "foo" },
    { "id": 3, "title": "post2", "author": "bar" }
]
```
You can get filtered response by calling:
```
GET /posts?title=py-json-server&author=bkstud
GET /posts?title=post2
```
### Filter limitations 
Properties should not start with underscore or they will be ignored. <br>
Currently deep properties are not supported.


## Developing
### Local setup without docker
For app to work properly you need python 3.8+ <br>
Install requirements and ASGI server of your choice. 
I develop with `uvicorn` and Dockerfile is `gunicorn` based.

```
pip install -r requirements.txt
# start app with default ip, port
uvicorn --reload app.main:app
```
## Building
You can build dockerfile manually based on provided `Dockerfile`
```
docker build . -t py-json-server
```

## Check generated API
After running app enter `${APP_ADDRESS}/docs`.

## Running as docker container
If you built docker image from Dockerfile or pulled from docker repo.
Run http server on port 8080 and publish to host on the same port. <br>
This example assumes your json data to share is under directory ./json and you will use default app/share directory for storing it.
```
# run http
docker run -p 8080:8080 -v $(pwd)/json:/static/ python-json:latest --host 0.0.0.0 --port 8080

# run https by providing certificate and key
docker run -p 8443:8443 -v $(pwd)/static:/static/ -v $(pwd)/tools/certs:/certs  python-json:latest --host 0.0.0.0 --port 8443 --ssl-certfile /certs/server-cert.pem --ssl-keyfile /certs/server-key.pem
```

## Configuration
### Environment settings
Each setting should have prefix APP_ example: APP_SECRET_KEY=myExtraSecretKeyThatNobodyKnow <br>
Currently all settings are of type `str`. <br>
List of available settings:
| Name         | Description     | Default value |
|--------------|-----------|------------|
| TITLE | Title name to be set for generated openapi name | "json_server" |
| SECRET_KEY | Secret key to be used for JWT encoding/decoding      | generated based on random 64-bits and BLAKE2B see app/auth/utils.py   |
| LOG_LEVEL      | Logger for logging (DEBUG/INFO/WARNING/etc.) | "INFO" |
| LOGGER      | Module to be used for logging purposes | "loguru.logger" |
| AUTH_METHOD      |  Authentication method currently can be JWT bearer or no auth check at all for no auth set it to empty string ("") | "jwt" |
| JWT_ALGORITHM | Algorithm to be used for JWT | "HS256" |
| JWT_TOKEN_EXPIRE | Expiration time for jwt tokens in minutes | "30" |
| API_ENDPOINT_BEGIN | Makes each contents endpoint to begin with /${API_ENDPOINT_BEGIN}/... | "/share" |
| SHARE_CONTENT_INPUT_DIR | Directory containing json files to be shared by server. | "./static" |
| DEFAULT_USER | Default user name for getting JWT token via /login. | "duo" |
| DEFAULT_PASSWORD | Default password for getting JWT token via /login. | "duo" |
